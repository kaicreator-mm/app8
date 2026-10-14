"""Fail-closed bounded model-call and operator-declared spend preflight.

Neither a caller's counters nor a source SHA establish genuine provider billing,
trusted chronology or model invocation. The real executor must separately
enforce caps *before* dispatch and attest usage from provider transport.
"""
from __future__ import annotations

import re

from scripts.v04_mla_pilot_reducer import ASSETS, PilotBlocked

ROLES = ("P", "R", "X")
BASE_COUNT = 12
MAX_J = 12
TOTAL_CALLS = 24
LIMIT_FIELDS = frozenset({
    "max_calls", "max_j_calls", "billing_currency",
    "max_total_input_tokens", "max_total_output_tokens",
    "max_total_cost_microunits", "max_total_wall_ms",
    "max_per_call_input_tokens", "max_per_call_output_tokens",
    "max_per_call_cost_microunits", "max_per_call_wall_ms",
})
CALL_FIELDS = frozenset({
    "role", "asset", "case_id", "input_tokens", "output_tokens",
    "cost_microunits", "wall_ms",
})
MEASURES = ("input_tokens", "output_tokens", "cost_microunits", "wall_ms")
TOTAL_NAMES = ("max_total_input_tokens", "max_total_output_tokens",
               "max_total_cost_microunits", "max_total_wall_ms")
PER_NAMES = ("max_per_call_input_tokens", "max_per_call_output_tokens",
             "max_per_call_cost_microunits", "max_per_call_wall_ms")


def check_budget(config: dict, calls: list[dict],
                 *, frozen_case_ids: set[str],
                 eligible_j_case_ids: set[str]) -> dict:
    """Check proposed/recorded P,R,X,J invocations against explicit fixed caps.

    Runtime caller MUST check this against a trusted append-only event stream
    before each actual dispatch. A standalone PASS from here is NOT authorization.
    """
    if not isinstance(config, dict) or set(config) != LIMIT_FIELDS:
        raise PilotBlocked("complete numeric pre-run budget required")
    numeric_keys = LIMIT_FIELDS - {"billing_currency"}
    if (any(type(config[key]) is not int or config[key] <= 0
            for key in numeric_keys)
            or not isinstance(config["billing_currency"], str)
            or re.fullmatch(r"[A-Z]{3}", config["billing_currency"]) is None
            or config["max_calls"] != TOTAL_CALLS
            or config["max_j_calls"] != MAX_J):
        raise PilotBlocked("invalid or mutable fixed budget limits")
    if (any(config[total] < config[per_call]
            for total, per_call in zip(TOTAL_NAMES, PER_NAMES))):
        raise PilotBlocked("total budget below a single call cap")
    if (not isinstance(frozen_case_ids, set)
            or not isinstance(eligible_j_case_ids, set)
            or any(not isinstance(x, str) for x in frozen_case_ids)
            or any(not isinstance(x, str) for x in eligible_j_case_ids)
            or not eligible_j_case_ids <= frozen_case_ids):
        raise PilotBlocked("invalid frozen case or J eligibility scope")
    if (not isinstance(calls, list) or len(calls) > TOTAL_CALLS):
        raise PilotBlocked("model call ceiling exceeded")
    seen_base: set[tuple[str, str]] = set()
    seen_j: set[str] = set()
    totals = dict.fromkeys(MEASURES, 0)
    for call in calls:
        if not isinstance(call, dict) or set(call) != CALL_FIELDS:
            raise PilotBlocked("missing or private model usage fields")
        role, asset, cid = call["role"], call["asset"], call["case_id"]
        if not isinstance(role, str) or role not in (*ROLES, "J"):
            raise PilotBlocked("unknown provider call role")
        if not isinstance(asset, str) or asset not in ASSETS:
            raise PilotBlocked("unknown provider call asset")
        if role in ROLES:
            if cid is not None or (role, asset) in seen_base:
                raise PilotBlocked("duplicated or case-swapped base role invocation")
            seen_base.add((role, asset))
        else:
            if (not isinstance(cid, str) or cid not in eligible_j_case_ids
                    or cid in seen_j
                    or not cid.startswith(f"V04-{asset.upper()}-")):
                raise PilotBlocked("J outside eligible predeclared case or duplicate")
            seen_j.add(cid)
        for field, cap in zip(MEASURES, PER_NAMES):
            actual = call[field]
            if type(actual) is not int or actual < 0 or actual > config[cap]:
                raise PilotBlocked("model invocation usage invalid or above per-call cap")
            totals[field] += actual
    if len(seen_j) > MAX_J:
        raise PilotBlocked("J escalation hard cap exceeded")
    for field, limit in zip(MEASURES, TOTAL_NAMES):
        if totals[field] > config[limit]:
            raise PilotBlocked("aggregate provider spend/time cap exceeded")
    return {
        "schema_version": "v04-mla-untrusted-spend-preflight-v1",
        "status": ("STRUCTURAL_USAGE_WITHIN_DECLARED_LIMITS"
                   if len(seen_base) == BASE_COUNT
                   else "BLOCKED_BASELINE_PROVIDER_CALLS_INCOMPLETE"),
        "model_calls_reported": len(calls),
        "base_calls_reported": len(seen_base),
        "j_calls_reported": len(seen_j),
        "call_limit": TOTAL_CALLS,
        "j_call_limit": MAX_J,
        "usage_reported": totals,
        "trusted_usage_and_provider_identity_verified": False,
        "pre_dispatch_budget_enforcement_verified": False,
        "pre_run_budget_freeze_verified": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
