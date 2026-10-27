"""V04-MLA typed bridge from already trusted app8 Evidence to pilot cases.

Only the privileged, previously accepted signed receipt is authoritative for
an observed execution. Even this does NOT establish semantic truth or release.
No model, caller boolean, naked SHA, or unapproved source/target mapping wins.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from app8.contracts import validate_contract, ContractError
from app8.evidence.attestation import AttestationGate
from app8.storage import EvidenceStore, IntegrityError

SHA = re.compile(r"[0-9a-f]{64}\Z")
CASE_ID = re.compile(r"V04-[A-Z0-9_-]{3,48}\Z")
RELATIONS = frozenset({"SAME", "KNOWLEDGE_SOURCE_ANCESTOR",
                       "KNOWLEDGE_SOURCE_DESCENDANT", "DIVERGED", "UNRESOLVED"})


class MLAEvidenceBlocked(ValueError):
    """Non-authenticated, wrong-binding or ineligible MLA evidence."""


@dataclass(frozen=True)
class FrozenExecutionScope:
    """Approved externally before execution; this object alone isn't approval."""
    source_sha256: str
    target_sha256: str
    plan_sha256: str
    fixture_sha256: str
    relation: str

    def __post_init__(self):
        values = (self.source_sha256, self.target_sha256,
                  self.plan_sha256, self.fixture_sha256)
        if any(not isinstance(x, str) or not SHA.fullmatch(x) for x in values):
            raise MLAEvidenceBlocked("execution scope requires four exact SHA256 identities")
        if self.relation not in RELATIONS:
            raise MLAEvidenceBlocked("invalid frozen source-to-target relation")


def _digest(document: dict) -> str:
    return hashlib.sha256((json.dumps(document, sort_keys=True, separators=(",", ":"),
                                      ensure_ascii=False, allow_nan=False) + "\n").encode()).hexdigest()


def reconcile_observation(*, case: dict, evidence: dict, receipt: dict,
                          store: EvidenceStore, gate: AttestationGate,
                          scope: FrozenExecutionScope) -> dict:
    """Report authenticated execution fact, NEVER inferred behavior truth or PASS.

    Must be called only by the trusted ingress service. No keys, raw runtime
    observations, sensitive fixtures or oracle verdicts emitted in this report.
    """
    if (type(gate) is not AttestationGate or type(store) is not EvidenceStore
            or type(scope) is not FrozenExecutionScope):
        raise MLAEvidenceBlocked("trusted durable evidence store and verification gate required")
    if (not isinstance(case, dict)
            or case.get("oracle_visible_to_predictor") is not False
            or case.get("source_verification_claim") != "CANDIDATE_ONLY"
            or not isinstance(case.get("case_id"), str)
            or not CASE_ID.fullmatch(case["case_id"])):
        raise MLAEvidenceBlocked("invalid case origin or hidden oracle exposure")
    if scope.relation in {"DIVERGED", "UNRESOLVED"}:
        raise MLAEvidenceBlocked("claim-specific independently reviewed target applicability required")
    try:
        validate_contract("evidence", evidence)
    except (ContractError, ValueError, TypeError) as exc:
        raise MLAEvidenceBlocked("frozen Evidence schema invalid") from exc
    if evidence.get("claim_id") != case["case_id"]:
        raise MLAEvidenceBlocked("case/evidence claim identity mismatch")
    if (evidence["source"]["content_sha256"] != scope.source_sha256
            or evidence["target"]["package_sha256"] != scope.target_sha256
            or evidence["target"]["mapping_relation"] != scope.relation
            or evidence["plan"]["plan_sha256"] != scope.plan_sha256
            or evidence["fixture"]["content_sha256"] != scope.fixture_sha256):
        raise MLAEvidenceBlocked("evidence source/target/plan/fixture scope mismatch")
    if (evidence["observation"]["execution_status"] != "EXECUTED"
            or evidence["observation"]["observer"] != "DETERMINISTIC_EXECUTION_ADAPTER"
            or evidence["assessment"]["assessor_kind"] != "DETERMINISTIC_ASSERTION_ENGINE"):
        raise MLAEvidenceBlocked("not a deterministic executed observation")
    try:
        retained = store.get_evidence(evidence["evidence_id"])
    except (IntegrityError, OSError, ValueError) as exc:
        raise MLAEvidenceBlocked("retained observation cannot be independently checked") from exc
    if retained != evidence:
        raise MLAEvidenceBlocked("missing or mismatched append-only Evidence")
    if not gate.is_accepted(evidence, receipt):
        raise MLAEvidenceBlocked("receipt not authenticated and accepted in durable nonce ledger")

    return {
        "schema_version": "v04-mla-authenticated-observation-ref-v1",
        "case_id": case["case_id"],
        "evidence_id": evidence["evidence_id"],
        "evidence_sha256": _digest(evidence),
        "receipt_sha256": _digest(receipt),
        "source_sha256": scope.source_sha256,
        "target_sha256": scope.target_sha256,
        "plan_sha256": scope.plan_sha256,
        "fixture_sha256": scope.fixture_sha256,
        "assessor_verdict": evidence["assessment"]["verdict"],
        "status": "AUTHENTICATED_EXECUTION_NOT_INDEPENDENT_SEMANTIC_ORACLE",
        "real_execution_receipt_accepted": True,
        "independent_behavior_oracle_verified": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
