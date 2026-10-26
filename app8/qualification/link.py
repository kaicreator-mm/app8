"""Narrow verifier for selected Capability and already-accepted signed Evidence.

No signature creation, license authority, target-admission override or execution.
A verified link is NOT Capability readiness and never unlocks invocation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app8.contracts import validate_contract
from app8.evidence.attestation import AttestationGate


class EvidenceLinkError(ValueError):
    """An evidence payload is not bound to the selected Capability."""


@dataclass(frozen=True)
class EvidenceLink:
    capability_id: str
    evidence_id: str
    binding_id: str
    status: str = "AUTHENTICATED_LINK_NOT_RELEASE_QUALIFIED"
    export_ready: bool = False


def verify_evidence_link(
    capability: dict[str, Any],
    evidence: dict[str, Any],
    signed_receipt: dict[str, Any],
    gate: AttestationGate,
) -> EvidenceLink:
    """Verify existing acceptance and exact target/source/binding identity.

    Caller-supplied trust flags have no effect. This is a read-only preflight.
    Only the existing full-ledger qualifier can derive actual readiness.
    """
    validate_contract("capability", capability)
    validate_contract("evidence", evidence)
    if type(gate) is not AttestationGate:
        raise EvidenceLinkError("privileged accepted receipt verifier required")
    if evidence["capability_id"] != capability["capability_id"]:
        raise EvidenceLinkError("different capability identity")
    if evidence["evidence_id"] not in capability["evidence_refs"]:
        raise EvidenceLinkError("evidence omitted from frozen Capability refs")
    if evidence["source"] != {
        key: capability["source"][key]
        for key in ("repository", "revision", "content_sha256")
    }:
        raise EvidenceLinkError("source identity mismatch")
    if evidence["target"] != capability["target"]:
        raise EvidenceLinkError("exact target or environment mismatch")
    bid = evidence["plan"]["binding_id"]
    if bid not in {item["binding_id"] for item in capability["bindings"]}:
        raise EvidenceLinkError("binding identity mismatch")
    if (evidence["observation"]["execution_status"] != "EXECUTED"
            or evidence["observation"]["observer"] != "DETERMINISTIC_EXECUTION_ADAPTER"
            or evidence["assessment"]["assessor_kind"] != "DETERMINISTIC_ASSERTION_ENGINE"
            or not evidence["plan"]["assertions"]):
        raise EvidenceLinkError("not a deterministic observed assertion")
    if not isinstance(signed_receipt, dict) or not gate.is_accepted(evidence, signed_receipt):
        raise EvidenceLinkError("receipt missing, modified, or not previously accepted")
    return EvidenceLink(capability["capability_id"], evidence["evidence_id"], bid)
