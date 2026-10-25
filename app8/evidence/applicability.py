"""Claim-specific DIVERGED applicability admission; NEVER behavioral truth.

Authority trust is anchored out-of-band (R1 review P1-01): the deployment
pins the SHA256 fingerprint of the authority ROOT key exactly once via
pin_authority_root(), and only ApplicabilityVerifier.provision() — which
checks that fingerprint and derives the authority-specific MAC key from the
root — registers a working verifier. Directly constructed instances stay
inert (seal/admit/verify/witness all refuse them), so a caller-chosen
key/id/db can never mint or vouch for an approval. The derived authority key
is domain-separated and MUST NEVER be the execution AttestationGate/runner
HMAC key (R13 §1, R15 P1).

Chronology is witnessed inside this single ledger (R1 review P1-02): admit()
journals an ADMISSION row, and the trusted ingress journals an
EXECUTION_WITNESS row bound to the exact canonical Evidence digest at runner
acceptance time. verify() requires the admission row to strictly precede the
witness row on the journal's one AUTOINCREMENT sequence; the runner-supplied
observation.recorded_at never participates in ordering, and the signer
declared issued_at is audit text only (R16 condition 2).
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
_ROOT_DERIVATION_INFO = b"app8-applicability-authority-key-v1|"
_ADMISSION = "ADMISSION"
_EXECUTION_WITNESS = "EXECUTION_WITNESS"

# Module-private provisioning state: the out-of-band root fingerprint pin and
# the registry of provisioned verifiers. Only provision() writes either after
# its fingerprint preimage check; a runtime caller cannot register a verifier.
_ROOT_PIN: dict[str, str] = {}
_PROVISIONED: dict[str, "ApplicabilityVerifier"] = {}


class ApplicabilityAdmissionError(ValueError):
    """Untrusted, mis-scoped, replayed or chronologically inadmissible approval."""


def pin_authority_root(*, root_key_fingerprint_sha256: str) -> None:
    """Deployment-time out-of-band pin of the authority root key fingerprint.

    Exactly-once per process: a second call with the same fingerprint is a
    no-op, any different value fails closed. Nothing else establishes trust.
    """
    _digest(root_key_fingerprint_sha256)
    pinned = _ROOT_PIN.get("fingerprint")
    if pinned is None:
        _ROOT_PIN["fingerprint"] = root_key_fingerprint_sha256
    elif not hmac.compare_digest(pinned, root_key_fingerprint_sha256):
        raise ApplicabilityAdmissionError("authority root pin is immutable")


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

    Working instances exist only via provision() (root-fingerprint checked);
    this holds the derived authority-specific MAC key and its OWN sqlite
    ledger, deliberately not the execution AttestationGate, its nonce db, or
    its key.
    """

    def __init__(self, *, authority_key: bytes, authority_id: str,
                 approval_db: str | Path):
        if not isinstance(authority_key, bytes) or len(authority_key) < 32:
            raise ApplicabilityAdmissionError("authority key must be >=32 private bytes")
        if not isinstance(authority_id, str) or not authority_id or len(authority_id) > 128:
            raise ApplicabilityAdmissionError("authority identity required")
        self._key = authority_key
        self._authority_id = authority_id
        self._rooted = False
        self._db = sqlite3.connect(approval_db, isolation_level=None, timeout=15)
        self._db.execute('CREATE TABLE IF NOT EXISTS admitted ('
                         'case_id TEXT PRIMARY KEY, approval_sha256 TEXT NOT NULL, '
                         'authority_id TEXT NOT NULL, accepted_at TEXT NOT NULL)')
        self._db.execute('CREATE TABLE IF NOT EXISTS authority_journal ('
                         'seq INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, '
                         'subject TEXT NOT NULL, recorded_at TEXT NOT NULL)')

    @classmethod
    def provision(cls, *, root_key: bytes, authority_id: str,
                  approval_db: str | Path) -> "ApplicabilityVerifier":
        """The only route that yields a rooted, registered verifier."""
        if not isinstance(root_key, bytes) or len(root_key) < 32:
            raise ApplicabilityAdmissionError("authority root key must be >=32 private bytes")
        if not isinstance(authority_id, str) or not authority_id or len(authority_id) > 128:
            raise ApplicabilityAdmissionError("authority identity required")
        pinned = _ROOT_PIN.get("fingerprint")
        if pinned is None:
            raise ApplicabilityAdmissionError("authority root fingerprint is not pinned out-of-band")
        if not hmac.compare_digest(hashlib.sha256(root_key).hexdigest(), pinned):
            raise ApplicabilityAdmissionError("root key does not match the pinned authority root")
        derived = hmac.new(root_key, _ROOT_DERIVATION_INFO + authority_id.encode("utf-8"),
                           hashlib.sha256).digest()
        verifier = cls(authority_key=derived, authority_id=authority_id,
                       approval_db=approval_db)
        verifier._rooted = True
        _PROVISIONED[authority_id] = verifier
        return verifier

    @classmethod
    def is_provisioned(cls, verifier: object) -> bool:
        """Total provenance check for the bridge; False for anything else."""
        return (type(verifier) is cls
                and verifier._rooted is True
                and _PROVISIONED.get(verifier._authority_id) is verifier)

    def _require_provisioned(self) -> None:
        if (self._rooted is not True
                or _PROVISIONED.get(self._authority_id) is not self):
            raise ApplicabilityAdmissionError(
                "verifier is not the provisioned authority instance")

    def _journal(self, kind: str, subject: str) -> None:
        self._db.execute('INSERT INTO authority_journal (kind, subject, recorded_at) '
                         'VALUES (?, ?, ?)',
                         (kind, subject,
                          datetime.now(timezone.utc).isoformat(timespec="microseconds")))

    def _evidence_digest(self, evidence) -> str:
        if not isinstance(evidence, dict):
            raise ApplicabilityAdmissionError("exact signed Evidence record required")
        return hashlib.sha256(_canonical(evidence)).hexdigest()

    def close(self):
        if _PROVISIONED.get(self._authority_id) is self:
            del _PROVISIONED[self._authority_id]
        self._db.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    def _mac(self, approval: ApplicabilityApproval) -> str:
        return hmac.new(self._key, _canonical(approval.unsigned_payload()),
                        hashlib.sha256).hexdigest()

    def seal(self, approval: ApplicabilityApproval) -> ApplicabilityApproval:
        """Authority minting route: the only place a valid MAC is produced."""
        self._require_provisioned()
        if type(approval) is not ApplicabilityApproval:
            raise ApplicabilityAdmissionError("exact frozen approval record required")
        if approval.authority_id != self._authority_id:
            raise ApplicabilityAdmissionError("approval belongs to another authority")
        return replace(approval, mac_sha256=self._mac(approval))

    def admit(self, approval: ApplicabilityApproval) -> str:
        """Trusted-ingress pre-outcome acceptance; idempotent per exact digest."""
        self._require_provisioned()
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
        self._db.execute('BEGIN IMMEDIATE')
        try:
            self._db.execute('INSERT INTO admitted VALUES (?, ?, ?, ?)',
                             (approval.case_id, digest, self._authority_id, accepted_at))
            self._journal(_ADMISSION, approval.case_id)
            self._db.execute('COMMIT')
        except BaseException:
            self._db.execute('ROLLBACK')
            raise
        return digest

    def witness_execution(self, evidence: dict) -> str:
        """Trusted ingress: journal the accepted runner outcome by exact digest.

        Called immediately after the execution gate accepts the Evidence, this
        row is the authority-ledger witness of the runner's accepted outcome;
        only journal order against the ADMISSION row decides chronology.
        """
        self._require_provisioned()
        digest = self._evidence_digest(evidence)
        row = self._db.execute('SELECT seq FROM authority_journal WHERE kind=? AND subject=?',
                               (_EXECUTION_WITNESS, digest)).fetchone()
        if row is None:
            self._journal(_EXECUTION_WITNESS, digest)
        return digest

    def verify(self, *, approval, case_id: str, scope, evidence: dict,
               case: dict) -> None:
        """Bridge-side check; raises instead of returning trust. No first admission.

        The caller (trusted ingress) guarantees exact FrozenExecutionScope type;
        binding here compares the frozen approval against that scope's four
        pinned SHA256 identities, the case id, the independently frozen
        Evidence source revision, the case-pinned release commit and claim
        scope (R1 review P2-01), and the single-ledger journal order of
        admission before the witnessed runner acceptance (R1 review P1-02).
        """
        self._require_provisioned()
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
        source = evidence.get("source") if isinstance(evidence, dict) else None
        if not isinstance(source, dict) or approval.source_revision != source.get("revision"):
            raise ApplicabilityAdmissionError(
                "approval source revision does not match the frozen evidence source")
        if not isinstance(case, dict):
            raise ApplicabilityAdmissionError("frozen case record required")
        if approval.release_commit != case.get("target_release_commit"):
            raise ApplicabilityAdmissionError(
                "approval release commit does not match the case-pinned release")
        if approval.claim_scope_sha256 != case.get("claim_scope_sha256"):
            raise ApplicabilityAdmissionError(
                "approval claim scope does not match the case-pinned claim scope")
        row = self._db.execute('SELECT approval_sha256 FROM admitted WHERE case_id=?',
                               (case_id,)).fetchone()
        if row is None:
            raise ApplicabilityAdmissionError("approval was not admitted before the outcome")
        digest = approval.record_digest()
        if row[0] != digest:
            raise ApplicabilityAdmissionError("conflicting approval already admitted for case")
        admission_seq = self._db.execute(
            'SELECT MIN(seq) FROM authority_journal WHERE kind=? AND subject=?',
            (_ADMISSION, case_id)).fetchone()
        if admission_seq is None or admission_seq[0] is None:
            raise ApplicabilityAdmissionError("approval was not admitted before the outcome")
        witness_seq = self._db.execute(
            'SELECT MIN(seq) FROM authority_journal WHERE kind=? AND subject=?',
            (_EXECUTION_WITNESS, self._evidence_digest(evidence))).fetchone()
        if witness_seq is None or witness_seq[0] is None:
            raise ApplicabilityAdmissionError(
                "runner acceptance was not witnessed in the authority ledger")
        if not admission_seq[0] < witness_seq[0]:
            raise ApplicabilityAdmissionError(
                "approval acceptance did not precede the witnessed runner acceptance")
