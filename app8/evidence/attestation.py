"""Authenticated evidence sidecar; NEVER mints signatures or behavioral truth.

Provision the HMAC verification key only in a privileged trusted service. A
signature binds the full Evidence JSON but is not OS-sandbox certification.
"""
from __future__ import annotations
import hashlib
import hmac
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

_HEX64 = re.compile(r'[0-9a-f]{64}\Z')
_HEX32 = re.compile(r'[0-9a-f]{32}\Z')
_FIELDS = {'schema_version', 'evidence_sha256', 'runner_id', 'policy_sha256',
           'image_sha256', 'nonce', 'mac_sha256'}

class AttestationError(ValueError):
    """Forged, unbound or replayed observation."""

def _canonical(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False, allow_nan=False) + '\n').encode()

class AttestationGate:
    """Once-only nonce ledger; repeatable authenticated Evidence rechecks."""
    def __init__(self, *, verification_key: bytes, runner_id: str,
                 policy_sha256: str, image_sha256: str, nonce_db: str | Path):
        if not isinstance(verification_key, bytes) or len(verification_key) < 32:
            raise AttestationError('private key must have at least 32 bytes')
        if not isinstance(runner_id, str) or not runner_id or len(runner_id) > 128:
            raise AttestationError('trusted runner identity required')
        if any(not isinstance(x, str) or not _HEX64.fullmatch(x)
               for x in (policy_sha256, image_sha256)):
            raise AttestationError('policy/image hashes must be frozen')
        self._key, self._runner = verification_key, runner_id
        self._policy, self._image = policy_sha256, image_sha256
        self._db = sqlite3.connect(nonce_db, isolation_level=None, timeout=15)
        self._db.execute('CREATE TABLE IF NOT EXISTS accepted ('
                         'nonce TEXT PRIMARY KEY, evidence_sha256 TEXT NOT NULL, '
                         'attestation_sha256 TEXT NOT NULL)')
    def close(self): self._db.close()
    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    def _validate(self, evidence: dict, attestation: dict) -> tuple[str, str, str]:
        if not isinstance(evidence, dict) or not isinstance(attestation, dict) or set(attestation) != _FIELDS:
            raise AttestationError('exact evidence and signed v2 envelope required')
        if attestation['schema_version'] != 'app8-attested-evidence-v2':
            raise AttestationError('unsupported receipt version')
        for key in ('evidence_sha256', 'policy_sha256', 'image_sha256', 'mac_sha256'):
            if not isinstance(attestation[key], str) or not _HEX64.fullmatch(attestation[key]):
                raise AttestationError(f'bad {key}')
        nonce = attestation['nonce']
        if not isinstance(nonce, str) or not _HEX32.fullmatch(nonce):
            raise AttestationError('invalid nonce')
        if (attestation['runner_id'] != self._runner or attestation['policy_sha256'] != self._policy or
                attestation['image_sha256'] != self._image):
            raise AttestationError('pinned runner/policy/image mismatch')
        evidence_sha = hashlib.sha256(_canonical(evidence)).hexdigest()
        if attestation['evidence_sha256'] != evidence_sha:
            raise AttestationError('full evidence payload modified')
        unsigned = {k: v for k, v in attestation.items() if k != 'mac_sha256'}
        mac = hmac.new(self._key, _canonical(unsigned), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(attestation['mac_sha256'], mac):
            raise AttestationError('untrusted runner signature')
        observation = evidence.get('observation', {})
        assessment = evidence.get('assessment', {})
        if (observation.get('execution_status') != 'EXECUTED' or
                observation.get('observer') != 'DETERMINISTIC_EXECUTION_ADAPTER' or
                type(observation.get('exit_code')) is not int or
                assessment.get('assessor_kind') != 'DETERMINISTIC_ASSERTION_ENGINE'):
            raise AttestationError('nonexecuted or non-deterministic evidence')
        receipt_sha = hashlib.sha256(_canonical(attestation)).hexdigest()
        return nonce, evidence_sha, receipt_sha

    def accept(self, evidence: dict, attestation: dict) -> str:
        """Ingest authenticated runner receipt exactly once; no semantic PASS."""
        nonce, evidence_sha, receipt_sha = self._validate(evidence, attestation)
        try:
            self._db.execute('INSERT INTO accepted VALUES (?, ?, ?)',
                             (nonce, evidence_sha, receipt_sha))
        except sqlite3.IntegrityError as exc:
            raise AttestationError('replayed nonce') from exc
        return receipt_sha

    def is_accepted(self, evidence: dict, attestation: dict) -> bool:
        """An unauthenticated caller flag is never accepted as evidence."""
        try:
            nonce, evidence_sha, receipt_sha = self._validate(evidence, attestation)
        except (AttestationError, ValueError, TypeError, OverflowError):
            return False
        row = self._db.execute('SELECT evidence_sha256, attestation_sha256 FROM accepted '
                               'WHERE nonce=?', (nonce,)).fetchone()
        return row == (evidence_sha, receipt_sha)
