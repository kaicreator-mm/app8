"""Trusted-service ingress for signed, runner-origin Evidence; not self-certification."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .attestation import AttestationGate, AttestationError

@dataclass(frozen=True)
class EvidenceImport:
    evidence_sha256: str
    receipt_sha256: str
    status: str = 'AUTHENTICATED_OBSERVATION_NOT_RELEASE_QUALIFIED'
    capability_export_ready: bool = False

def import_signed_observation(store: Any, gate: AttestationGate,
                              evidence: dict, signed_receipt: dict) -> EvidenceImport:
    """Validate -> consume authenticated nonce -> append immutable Evidence/event.

    A failed store write consumes nonce (fail closed), requiring fresh runner
    signing for retry. This routine never creates the receipt or decides PASS.
    """
    if type(gate) is not AttestationGate:
        raise AttestationError('privileged AttestationGate required')
    store.validator('evidence', evidence)
    receipt_sha = gate.accept(evidence, signed_receipt)
    evidence_sha = store.append_evidence(evidence)
    store.append_event(evidence['evidence_id'], 'RUNNER_RECEIPT_AUTHENTICATED',
                       {'receipt_sha256': receipt_sha, 'evidence_sha256': evidence_sha,
                        'release_qualified': False})
    return EvidenceImport(evidence_sha, receipt_sha)
