"""Claim-specific DIVERGED applicability admission; NEVER behavioral truth.

Authority trust is fixed in reviewed source (R24 P1-02, R26 P1-01): the
SHA256 fingerprint of the authority ROOT key ships as the module constant
AUTHORITY_ROOT_FINGERPRINT_SHA256 with NO runtime first-writer pin API
(pin_authority_root was removed). The shipped value is an explicit UNUSABLE
SENTINEL and provision() hard-denies while the constant is still the
sentinel, so NO key — including any byte literal published in this
repository — can provision against a shipped default. A real deployment
replaces the constant with the actual authority root fingerprint via an
independently reviewed commit before use; no usable root-key bytes or
reconstructible preimage ever ship in source. Only
ApplicabilityVerifier.provision() — which checks that fingerprint and
derives the authority-specific MAC key from the root — registers a working
verifier; directly constructed instances stay inert. The derived authority
key is domain-separated and MUST NEVER be the execution
AttestationGate/runner HMAC key (R13 §1, R15 P1).

Chronology is anchored to the runner's entry, not to post-hoc writes (R24
P1-01): the trusted ingress reserves the runner's entry BEFORE the run —
reserve_execution() journals a RESERVATION row binding a fresh unguessable
nonce to the exact case id and frozen execution scope, and hands the nonce
to the runner, which embeds it as the signed receipt nonce. verify()
requires the approval's ADMISSION journal row to strictly precede that
RESERVATION row on the ledger's single AUTOINCREMENT sequence; because the
runner can only embed a nonce after it was reserved, an approval admitted
after the runner's entry can never yield an admissible reference, regardless
of any later journal writes. The runner-supplied observation.recorded_at
never participates in ordering; the signer-declared issued_at is audit text
only (R16 condition 2).

Enforced boundary (R24 P1-02): this module runs inside the single-principal
trusted ingress service; no less-trusted in-process principal imports or
executes it (the execution runner is out-of-process with a separate HMAC
domain), so the module-private provisioning registry is not reachable across
a trust boundary at runtime.
"""
from __future__ import annotations

from dataclasses import dataclass, fields, replace
import hashlib
import hmac
import json
from pathlib import Path
import re
import secrets
import sqlite3
from datetime import datetime, timezone

APPROVAL_SCHEMA_VERSION = "app8-applicability-approval-v1"
VERDICT_ORIGINS = frozenset({"INDEPENDENT_AUTHORITY_SIGNED"})
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_COMMIT = re.compile(r"[0-9a-f]{40}\Z|[0-9a-f]{64}\Z")
_CASE_ID = re.compile(r"V04-[A-Z0-9_-]{3,48}\Z")
_NONCE = re.compile(r"[0-9a-f]{32}\Z")
MAC_PLACEHOLDER = "0" * 64
_ROOT_DERIVATION_INFO = b"app8-applicability-authority-key-v1|"
_ADMISSION = "ADMISSION"
_RESERVATION = "RESERVATION"

# Out-of-band authority root pin, fixed in reviewed source (R24 P1-02,
# R26 P1-01): the shipped value is an explicit UNUSABLE SENTINEL — never a
# fingerprint over any reconstructible published literal — and provision()
# hard-denies while the constant is the sentinel, so provisioning fails
# closed until a reviewed deployment commit replaces it with the real
# authority root fingerprint. No usable root-key bytes or their preimage
# ship in source.
AUTHORITY_ROOT_FINGERPRINT_SENTINEL = "0" * 64
AUTHORITY_ROOT_FINGERPRINT_SHA256 = AUTHORITY_ROOT_FINGERPRINT_SENTINEL

# Module-private provisioning registry. Only provision() writes it, behind
# the fingerprint preimage check; a runtime caller cannot register a verifier.
_PROVISIONED: dict[str, "ApplicabilityVerifier"] = {}


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
        self._db.execute('CREATE TABLE IF NOT EXISTS reservations ('
                         'nonce TEXT PRIMARY KEY, case_id TEXT NOT NULL, '
                         'source_sha256 TEXT NOT NULL, target_sha256 TEXT NOT NULL, '
                         'plan_sha256 TEXT NOT NULL, fixture_sha256 TEXT NOT NULL, '
                         'journal_seq INTEGER NOT NULL)')
        # R26 P1-02: private, non-authoritative audit trail for the
        # external-provisional release interpretation. Deliberately separate
        # from authority_journal so it can never influence admission or
        # reservation ordering, and never reaches the external report.
        self._db.execute('CREATE TABLE IF NOT EXISTS provisional_release_audit ('
                         'case_id TEXT NOT NULL, authority_id TEXT NOT NULL, '
                         'release_commit TEXT NOT NULL, claim_scope_sha256 TEXT NOT NULL, '
                         'binding TEXT NOT NULL, recorded_at TEXT NOT NULL)')

    @classmethod
    def provision(cls, *, root_key: bytes, authority_id: str,
                  approval_db: str | Path) -> "ApplicabilityVerifier":
        """The only route that yields a rooted, registered verifier."""
        if not isinstance(root_key, bytes) or len(root_key) < 32:
            raise ApplicabilityAdmissionError("authority root key must be >=32 private bytes")
        if not isinstance(authority_id, str) or not authority_id or len(authority_id) > 128:
            raise ApplicabilityAdmissionError("authority identity required")
        # R26 P1-01: hard-deny before any fingerprint comparison while the
        # reviewed-source constant is still the unusable shipped sentinel —
        # the shipped default must not provision ANY key.
        if hmac.compare_digest(AUTHORITY_ROOT_FINGERPRINT_SHA256,
                               AUTHORITY_ROOT_FINGERPRINT_SENTINEL):
            raise ApplicabilityAdmissionError(
                "authority root fingerprint is the unusable shipped sentinel; "
                "provisioning is denied until a reviewed deployment commit "
                "replaces it")
        if not hmac.compare_digest(hashlib.sha256(root_key).hexdigest(),
                                   AUTHORITY_ROOT_FINGERPRINT_SHA256):
            raise ApplicabilityAdmissionError("root key does not match the reviewed authority root fingerprint")
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

    def _journal(self, kind: str, subject: str) -> int:
        cursor = self._db.execute(
            'INSERT INTO authority_journal (kind, subject, recorded_at) VALUES (?, ?, ?)',
            (kind, subject,
             datetime.now(timezone.utc).isoformat(timespec="microseconds")))
        return int(cursor.lastrowid)

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

    def reserve_execution(self, *, case_id: str, scope) -> str:
        """Trusted ingress: pre-run runner-entry reservation; returns the nonce.

        Journals a RESERVATION row binding a fresh unguessable 128-bit nonce
        to the exact case id and frozen execution scope, and returns the
        nonce for the runner to embed as its receipt nonce. Because the
        runner can only learn the nonce after this reservation exists,
        verify() can require the approval's ADMISSION row to strictly precede
        the RESERVATION row: an approval admitted after the runner's entry
        can never produce an admissible reference, no matter what is written
        later. There is deliberately no post-hoc witness API.
        """
        self._require_provisioned()
        if not isinstance(case_id, str) or not _CASE_ID.fullmatch(case_id):
            raise ApplicabilityAdmissionError("reservation requires a frozen case id")
        shas = tuple(getattr(scope, name, None) for name in
                     ("source_sha256", "target_sha256", "plan_sha256", "fixture_sha256"))
        if any(not isinstance(x, str) or not _SHA256.fullmatch(x) for x in shas):
            raise ApplicabilityAdmissionError("reservation requires the frozen execution scope")
        for _ in range(8):
            nonce = secrets.token_hex(16)
            try:
                self._db.execute('BEGIN IMMEDIATE')
                try:
                    seq = self._journal(_RESERVATION, nonce)
                    self._db.execute('INSERT INTO reservations VALUES (?, ?, ?, ?, ?, ?, ?)',
                                     (nonce, case_id, shas[0], shas[1], shas[2], shas[3], seq))
                    self._db.execute('COMMIT')
                except BaseException:
                    self._db.execute('ROLLBACK')
                    raise
                return nonce
            except sqlite3.IntegrityError:
                continue  # nonce collision; retry with a fresh nonce
        raise ApplicabilityAdmissionError("reservation nonce allocation failed")

    def verify(self, *, approval, case_id: str, scope, evidence: dict,
               case: dict, receipt: dict) -> None:
        """Bridge-side check; raises instead of returning trust. No first admission.

        The caller (trusted ingress) guarantees exact FrozenExecutionScope
        type and a gate-authenticated receipt; binding here compares the
        frozen approval against that scope's four pinned SHA256 identities,
        the case id, the independently frozen Evidence source revision, the
        case-pinned release commit and claim scope (R1 P2-01), and the
        single-ledger journal order of admission strictly before the
        reserved runner entry (R24 P1-01). On success this journals a
        private, non-authoritative EXTERNAL_PROVISIONAL_CANDIDATE audit row
        (R26 P1-02) so the external report never needs more than the two
        R19-authorized keys; the audit row admits and promotes nothing.
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
        if not isinstance(receipt, dict):
            raise ApplicabilityAdmissionError("authenticated runner receipt required")
        nonce = receipt.get("nonce")
        if not isinstance(nonce, str) or not _NONCE.fullmatch(nonce):
            raise ApplicabilityAdmissionError("authenticated runner receipt nonce required")
        reserved = self._db.execute(
            'SELECT case_id, source_sha256, target_sha256, plan_sha256, fixture_sha256, '
            'journal_seq FROM reservations WHERE nonce=?', (nonce,)).fetchone()
        if reserved is None:
            raise ApplicabilityAdmissionError(
                "runner entry was not reserved in the authority ledger")
        if (reserved[0] != case_id
                or reserved[1] != scope.source_sha256
                or reserved[2] != scope.target_sha256
                or reserved[3] != scope.plan_sha256
                or reserved[4] != scope.fixture_sha256):
            raise ApplicabilityAdmissionError(
                "reserved runner entry is bound to a different case or execution scope")
        if not admission_seq[0] < reserved[5]:
            raise ApplicabilityAdmissionError(
                "approval acceptance did not precede the reserved runner entry")
        self._db.execute(
            'INSERT INTO provisional_release_audit VALUES (?, ?, ?, ?, ?, ?)',
            (case_id, self._authority_id, approval.release_commit,
             approval.claim_scope_sha256, "EXTERNAL_PROVISIONAL_CANDIDATE",
             datetime.now(timezone.utc).isoformat(timespec="microseconds")))

    def provisional_release_audit(self, *, case_id: str) -> list[dict]:
        """Read this authority's private release-binding audit rows for a case.

        R26 P1-02: the EXTERNAL_PROVISIONAL_CANDIDATE interpretation of the
        caller-pinned release commit lives ONLY in this authority-side
        private audit trail — it is never emitted in the external report and
        is not an approved release claim or promotion of any kind.
        """
        self._require_provisioned()
        if not isinstance(case_id, str) or not _CASE_ID.fullmatch(case_id):
            raise ApplicabilityAdmissionError("audit lookup requires a frozen case id")
        rows = self._db.execute(
            'SELECT release_commit, claim_scope_sha256, binding, recorded_at '
            'FROM provisional_release_audit WHERE case_id=? ORDER BY rowid',
            (case_id,)).fetchall()
        return [{"release_commit": row[0], "claim_scope_sha256": row[1],
                 "binding": row[2], "recorded_at": row[3]} for row in rows]
