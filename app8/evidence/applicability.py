"""Claim-specific DIVERGED applicability admission; NEVER behavioral truth.

The authority MAC key is provisioned only to the independent applicability
authority service and MUST NEVER be the execution AttestationGate/runner HMAC
key (R13 §1, R15 P1). An approval becomes admissible only when the trusted
ingress `admit()`s it into the ledger strictly before the real oracle outcome;
`verify()` inside the bridge never creates a first ledger row and never trusts
the signer-declared `issued_at` for ordering (R16 condition 2).
"""
from __future__ import annotations

from dataclasses import dataclass, fields, replace
import hashlib
import hmac
import json
from pathlib import Path
import re
import sqlite3
from datetime import datetime, timezone

APPROVAL_SCHEMA_VERSION = "app8-applicability-approval-v1"
VERDICT_ORIGINS = frozenset({"INDEPENDENT_AUTHORITY_SIGNED"})
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_COMMIT = re.compile(r"[0-9a-f]{40}\Z|[0-9a-f]{64}\Z")
_CASE_ID = re.compile(r"V04-[A-Z0-9_-]{3,48}\Z")
MAC_PLACEHOLDER = "0" * 64


class ApplicabilityAdmissionError(ValueError):
    """Untrusted, mis-scoped, replayed or chronologically inadmissible approval."""


def _canonical(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


def _digest(value: str) -> None:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ApplicabilityAdmissionError("exact lowercase SHA256 required")


def _parse_instant(value: str, label: str) -> datetime:
    if not isinstance(value, str):
        raise ApplicabilityAdmissionError(f"{label} instant must be an RFC3339 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ApplicabilityAdmissionError(f"{label} instant is not RFC3339") from exc
    if parsed.tzinfo is None:
        raise ApplicabilityAdmissionError(f"{label} instant requires a timezone")
    return parsed


@dataclass(frozen=True)
class ApplicabilityApproval:
    """Frozen case-scoped authority approval; no naked boolean, no TTL field."""

    schema_version: str
    case_id: str
    authority_id: str
    source_revision: str
    source_content_sha256: str
    release_commit: str
    target_package_sha256: str
    claim_scope_sha256: str
    plan_sha256: str
    fixture_sha256: str
    verdict_origin: str
    issued_at: str
    mac_sha256: str

    def __post_init__(self):
        if self.schema_version != APPROVAL_SCHEMA_VERSION:
            raise ApplicabilityAdmissionError("unsupported approval schema version")
        if not isinstance(self.case_id, str) or not _CASE_ID.fullmatch(self.case_id):
            raise ApplicabilityAdmissionError("approval requires a frozen case id")
        if (not isinstance(self.authority_id, str) or not self.authority_id
                or len(self.authority_id) > 128):
            raise ApplicabilityAdmissionError("authority identity required")
        if not isinstance(self.source_revision, str) or not self.source_revision:
            raise ApplicabilityAdmissionError("source revision required")
        _digest(self.source_content_sha256)
        _digest(self.target_package_sha256)
        _digest(self.claim_scope_sha256)
        _digest(self.plan_sha256)
        _digest(self.fixture_sha256)
        if (not isinstance(self.release_commit, str)
                or not _COMMIT.fullmatch(self.release_commit)):
            raise ApplicabilityAdmissionError("tagged release commit required")
        if self.verdict_origin not in VERDICT_ORIGINS:
            raise ApplicabilityAdmissionError("verdict origin must be independent authority signed")
        _parse_instant(self.issued_at, "issued_at")
        _digest(self.mac_sha256)

    def _record(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def unsigned_payload(self) -> dict:
        return {k: v for k, v in self._record().items() if k != "mac_sha256"}

    def record_digest(self) -> str:
        return hashlib.sha256(_canonical(self._record())).hexdigest()


class ApplicabilityVerifier:
    """Single trusted construction route for applicability admission.

    Holds the authority-specific MAC key and its OWN sqlite ledger; this is
    deliberately not the execution AttestationGate, its nonce db, or its key.
    """

    def __init__(self, *, authority_key: bytes, authority_id: str,
                 approval_db: str | Path):
        if not isinstance(authority_key, bytes) or len(authority_key) < 32:
            raise ApplicabilityAdmissionError("authority key must be >=32 private bytes")
        if not isinstance(authority_id, str) or not authority_id or len(authority_id) > 128:
            raise ApplicabilityAdmissionError("authority identity required")
        self._key = authority_key
        self._authority_id = authority_id
        self._db = sqlite3.connect(approval_db, isolation_level=None, timeout=15)
        self._db.execute('CREATE TABLE IF NOT EXISTS admitted ('
                         'case_id TEXT PRIMARY KEY, approval_sha256 TEXT NOT NULL, '
                         'authority_id TEXT NOT NULL, accepted_at TEXT NOT NULL)')
    def close(self): self._db.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    def _mac(self, approval: ApplicabilityApproval) -> str:
        return hmac.new(self._key, _canonical(approval.unsigned_payload()),
                        hashlib.sha256).hexdigest()

    def seal(self, approval: ApplicabilityApproval) -> ApplicabilityApproval:
        """Authority minting route: the only place a valid MAC is produced."""
        if type(approval) is not ApplicabilityApproval:
            raise ApplicabilityAdmissionError("exact frozen approval record required")
        if approval.authority_id != self._authority_id:
            raise ApplicabilityAdmissionError("approval belongs to another authority")
        return replace(approval, mac_sha256=self._mac(approval))

    def admit(self, approval: ApplicabilityApproval) -> str:
        """Trusted-ingress pre-outcome acceptance; idempotent per exact digest."""
        if type(approval) is not ApplicabilityApproval:
            raise ApplicabilityAdmissionError("exact frozen approval record required")
        if approval.authority_id != self._authority_id:
            raise ApplicabilityAdmissionError("approval belongs to another authority")
        if not hmac.compare_digest(self._mac(approval), approval.mac_sha256):
            raise ApplicabilityAdmissionError("untrusted authority signature")
        digest = approval.record_digest()
        row = self._db.execute('SELECT approval_sha256 FROM admitted WHERE case_id=?',
                               (approval.case_id,)).fetchone()
        if row is not None:
            if row[0] != digest:
                raise ApplicabilityAdmissionError("conflicting approval already admitted for case")
            return digest
        accepted_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        self._db.execute('INSERT INTO admitted VALUES (?, ?, ?, ?)',
                         (approval.case_id, digest, self._authority_id, accepted_at))
        return digest

    def verify(self, *, approval, case_id: str, scope, outcome_recorded_at: str) -> None:
        """Bridge-side check; raises instead of returning trust. No first admission.

        The caller (trusted ingress) guarantees exact FrozenExecutionScope type;
        binding here compares the frozen approval against that scope's four
        pinned SHA256 identities and the case id.
        """
        if type(approval) is not ApplicabilityApproval:
            raise ApplicabilityAdmissionError("exact frozen approval record required")
        if approval.authority_id != self._authority_id:
            raise ApplicabilityAdmissionError("approval belongs to another authority")
        if not hmac.compare_digest(self._mac(approval), approval.mac_sha256):
            raise ApplicabilityAdmissionError("untrusted authority signature")
        if approval.case_id != case_id:
            raise ApplicabilityAdmissionError("approval bound to a different case")
        if (approval.source_content_sha256 != scope.source_sha256
                or approval.target_package_sha256 != scope.target_sha256
                or approval.plan_sha256 != scope.plan_sha256
                or approval.fixture_sha256 != scope.fixture_sha256):
            raise ApplicabilityAdmissionError("approval scope does not match frozen execution scope")
        row = self._db.execute('SELECT approval_sha256, accepted_at FROM admitted WHERE case_id=?',
                               (case_id,)).fetchone()
        if row is None:
            raise ApplicabilityAdmissionError("approval was not admitted before the outcome")
        digest = approval.record_digest()
        if row[0] != digest:
            raise ApplicabilityAdmissionError("conflicting approval already admitted for case")
        accepted_at = _parse_instant(row[1], "accepted_at")
        outcome_at = _parse_instant(outcome_recorded_at, "outcome_recorded_at")
        if accepted_at >= outcome_at:
            raise ApplicabilityAdmissionError("approval acceptance is not strictly before the observed outcome")
