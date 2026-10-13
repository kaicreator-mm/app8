"""A deterministic readiness reducer, not an LLM judge or an evidence observer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

NEGATIVE_EVENTS = {"REFUTED", "BLOCKED", "STALE", "REVOKED", "TARGET_DRIFT"}


@dataclass(frozen=True)
class Readiness:
    lifecycle_state: str
    export_ready: bool
    reason_codes: tuple[str, ...]
    qualified_evidence_ids: tuple[str, ...]


def evaluate_readiness(
    capability: dict[str, Any], evidence: Iterable[dict[str, Any]],
    events: Iterable[dict[str, Any]] = (),
    *, projection_verifier: Callable[[dict[str, Any]], bool] | None = None,
) -> Readiness:
    """Return status from scoped real observations, not supplied capability.readiness.

    projection_verifier is reserved for a deterministic trusted T07 adapter.
    If it is absent, actual EXPORT_READY is deliberately impossible.
    """
    reasons: set[str] = set()
    events = list(events)
    event_kinds = {e.get("kind") for e in events if isinstance(e, dict)}
    if event_kinds & NEGATIVE_EVENTS:
        reasons.add("MATERIAL_NEGATIVE_EVIDENCE")

    source = capability.get("source", {})
    target = capability.get("target", {})
    if target.get("mapping_relation") in {"DIVERGED", "UNRESOLVED"}:
        applicability = any(
            e.get("kind") == "TARGET_APPLICABILITY_CONFIRMED" and
            e.get("payload", {}).get("package_sha256") == target.get("package_sha256")
            for e in events if isinstance(e, dict)
        )
        if not applicability:
            reasons.add("TARGET_APPLICABILITY_UNVERIFIED")

    ids = set(capability.get("evidence_refs", []))
    bindings = {b.get("binding_id") for b in capability.get("bindings", []) if isinstance(b, dict)}
    qualified = []
    for ev in evidence:
        if not isinstance(ev, dict) or ev.get("evidence_id") not in ids:
            continue
        if any(ev.get("source", {}).get(k) != source.get(k)
               for k in ("repository", "revision", "content_sha256")):
            reasons.add("SOURCE_MISMATCH")
            continue
        if any(ev.get("target", {}).get(k) != target.get(k)
               for k in ("identity", "package_sha256", "environment_id", "mapping_relation")):
            reasons.add("EXECUTION_TARGET_MISMATCH")
            continue
        observation, assessment = ev.get("observation", {}), ev.get("assessment", {})
        plan = ev.get("plan", {})
        if plan.get("binding_id") not in bindings:
            reasons.add("BINDING_NOT_AUTHORIZED")
            continue
        if (observation.get("execution_status") != "EXECUTED" or
            observation.get("observer") not in {"DETERMINISTIC_EXECUTION_ADAPTER", "MANUAL_OPERATOR_ATTESTED"} or
            not isinstance(observation.get("exit_code"), int)):
            reasons.add("NO_VALID_REAL_OBSERVATION")
            continue
        if (assessment.get("verdict") != "SUPPORTED" or
            assessment.get("assessor_kind") not in {"DETERMINISTIC_ASSERTION_ENGINE", "HUMAN_OPERATOR"} or
            "ASSERTIONS_PASSED" not in assessment.get("reason_codes", []) or
            not plan.get("assertions")):
            reasons.add("NO_DETERMINISTIC_ASSERTION_PASS")
            continue
        qualified.append(ev["evidence_id"])

    if not qualified:
        reasons.add("NO_QUALIFIED_POSITIVE_EVIDENCE")
        return Readiness("HYPOTHESIZED", False, tuple(sorted(reasons)), ())
    if reasons & {"MATERIAL_NEGATIVE_EVIDENCE", "TARGET_APPLICABILITY_UNVERIFIED",
                  "SOURCE_MISMATCH", "EXECUTION_TARGET_MISMATCH", "BINDING_NOT_AUTHORIZED",
                  "NO_VALID_REAL_OBSERVATION", "NO_DETERMINISTIC_ASSERTION_PASS"}:
        return Readiness("BLOCKED", False, tuple(sorted(reasons)), tuple(sorted(set(qualified))))
    if projection_verifier is None or not projection_verifier(capability):
        reasons.add("PROJECTION_NOT_VERIFIED")
        return Readiness("EVIDENCED", False, tuple(sorted(reasons)), tuple(sorted(set(qualified))))
    return Readiness("EXPORT_READY", True, tuple(sorted(reasons)), tuple(sorted(set(qualified))))
