"""Qualify a pinned Capability from *stored* signed Evidence only.

This module cannot sign receipts, run Docker, or authorize an unreviewed
binding. Its readiness statement is scoped to one source/target/environment
and is NOT a claim about overall product SE10/SE11 effectiveness.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

from app8.contracts import validate_contract
from app8.evidence.attestation import AttestationGate
from app8.projections import build_projections, verify_projection_suite
from app8.readiness import Readiness, evaluate_readiness
from app8.storage import EvidenceStore

_NEGATIVE_VERDICTS = frozenset({"REFUTED", "BLOCKED", "NARROWED"})
_EVENT_VETOES = frozenset({"REFUTED", "BLOCKED", "STALE", "REVOKED", "TARGET_DRIFT"})


@dataclass(frozen=True)
class Qualification:
    status: str
    readiness: Readiness
    evidence_snapshot_sha256: str
    evidence_count: int
    projections: dict[str, dict]
    release_qualified: bool = False


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _blocked(reason: str, snapshot: str, count: int) -> Qualification:
    return Qualification("BLOCKED", Readiness("BLOCKED", False, (reason,), ()),
                         snapshot, count, {})


def qualify_stored_capability(
    capability: dict[str, Any],
    *, store: EvidenceStore,
    attestation_gate: AttestationGate,
    signed_attestations: Mapping[str, dict[str, Any]],
) -> Qualification:
    """Read the entire local Evidence ledger, veto omissions and negative facts.

    The caller cannot select only positive Evidence by choosing evidence_refs.
    Privileged service must supply its existing private-key verifier and the
    externally generated signed sidecars. No model-proposed record is trusted.
    """
    validate_contract("capability", capability)
    if type(store) is not EvidenceStore or type(attestation_gate) is not AttestationGate:
        raise TypeError("Trusted EvidenceStore and AttestationGate required")
    if not isinstance(signed_attestations, Mapping):
        raise TypeError("Signed Evidence sidecars required")

    cid = capability["capability_id"]
    records = store.list_evidence_for_capability(cid)
    stored_ids = {ev["evidence_id"] for ev in records}
    declared_ids = set(capability["evidence_refs"])
    snapshot = sha256(_canonical([
        {"id": ev["evidence_id"], "sha256": sha256(_canonical(ev)).hexdigest()}
        for ev in sorted(records, key=lambda item: item["evidence_id"])
    ])).hexdigest()

    if stored_ids != declared_ids:
        return _blocked("EVIDENCE_REFERENCE_SET_NOT_COMPLETE", snapshot, len(records))
    if not records:
        return _blocked("NO_STORED_BEHAVIORAL_EVIDENCE", snapshot, 0)
    if capability["source"]["license_disposition"] != "REVIEWED_COMPATIBLE":
        return _blocked("LICENSE_DISPOSITION_NOT_REVIEWED", snapshot, len(records))
    # v0.3 pilot does not support mapping across source vs runtime revisions.
    if capability["target"]["mapping_relation"] != "SAME":
        return _blocked("SOURCE_TARGET_APPLICABILITY_UNPROVEN", snapshot, len(records))

    for ev in records:
        signed = signed_attestations.get(ev["evidence_id"])
        if not isinstance(signed, dict) or not attestation_gate.is_accepted(ev, signed):
            return _blocked("UNAUTHENTICATED_LEDGER_EVIDENCE", snapshot, len(records))
        if ev["capability_id"] != cid or ev["source"]["repository"] != capability["source"]["repository"]:
            return _blocked("CAPABILITY_OR_SOURCE_MISMATCH", snapshot, len(records))

    events = list(store.history(cid))
    # A material falsification may exist as a signed, stored record rather than
    # a separate mutable Capability event. Do not silently omit it.
    for ev in records:
        verdict = ev["assessment"]["verdict"]
        if verdict in _NEGATIVE_VERDICTS:
            events.append({"kind": "REFUTED", "payload": {"evidence_id": ev["evidence_id"]}})
        if ev["observation"]["execution_status"] != "EXECUTED":
            events.append({"kind": "BLOCKED", "payload": {"evidence_id": ev["evidence_id"]}})

    preliminary = evaluate_readiness(
        capability, records, events, attestation_gate=attestation_gate,
        signed_attestations=signed_attestations,
    )
    if any(event.get("kind") in _EVENT_VETOES for event in events):
        return _blocked("MATERIAL_NEGATIVE_OR_CURRENTNESS_EVENT", snapshot, len(records))
    if preliminary.lifecycle_state != "EVIDENCED":
        return Qualification("UNREADY", preliminary, snapshot, len(records), {})

    # Only our deterministic projection implementation can make the final
    # transition. An arbitrary caller lambda(True) is never accepted.
    candidate_projections = build_projections(capability, preliminary, snapshot)
    if not verify_projection_suite(capability, snapshot, candidate_projections):
        return _blocked("PROJECTION_SUITE_NOT_AUTHORITATIVE", snapshot, len(records))
    final = evaluate_readiness(
        capability, records, events,
        projection_verifier=lambda _: verify_projection_suite(
            capability, snapshot, candidate_projections
        ),
        attestation_gate=attestation_gate,
        signed_attestations=signed_attestations,
    )
    if not final.export_ready:
        return Qualification("UNREADY", final, snapshot, len(records),
                             candidate_projections)
    projections = build_projections(capability, final, snapshot)
    if not verify_projection_suite(capability, snapshot, projections):
        return _blocked("PROJECTION_REVALIDATION_FAILED", snapshot, len(records))
    return Qualification("SCOPED_EXPORT_READY", final, snapshot, len(records), projections)
