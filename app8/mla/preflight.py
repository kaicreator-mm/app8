"""Bounded 24-case MLA evidence-status preflight: NO behavioral truth scorer.

A model-proposed disposition, public digest or human/J text is never proof of
an independent real-software oracle. This reducer is intentionally limited to
structural identity, denominator completeness and conservative case outcomes.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

from scripts.v04_mla_pilot_reducer import ROOT, PilotBlocked, assess

OUTCOMES = frozenset({
    "BEHAVIOR_SUPPORTED", "SOURCE_SUPPORTED_ONLY", "REFUTED",
    "NARROWED", "UNVERIFIED", "BLOCKED",
})
ROW_KEYS = frozenset({
    "case_id", "requested_outcome", "reference_origin",
    "behavior_observation_sha256", "oracle_commitment_sha256",
})
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def _sha_or_null(value: object) -> bool:
    return value is None or (isinstance(value, str)
                             and HEX64.fullmatch(value) is not None)


def reduce_evidence_preflight(pilot_public: dict, candidate_rows: list[dict],
                              *, repo_root: Path = ROOT) -> dict:
    """Require 24/24 source-bound candidate rows; deny all unsupported truth.

    This is intentionally not a general empirical reducer. Even apparently
    signed-looking SHA256 strings cannot cross the trusted oracle boundary.
    The result can only be PROVISIONAL or BLOCKED, never PASS or promotion.
    """
    pilot_report = assess(repo_root, pilot_public)
    original_cases = {c["case_id"]: c for c in pilot_public["cases"]}
    if not isinstance(candidate_rows, list) or len(candidate_rows) != 24:
        raise PilotBlocked("24 non-replaceable case statuses required")
    seen: set[str] = set()
    candidates = Counter()
    admitted = Counter()
    reported = []
    for row in candidate_rows:
        if not isinstance(row, dict) or set(row) != ROW_KEYS:
            raise PilotBlocked("unexpected candidate fields: truth/leakage guard")
        cid = row["case_id"]
        if not isinstance(cid, str) or cid not in original_cases or cid in seen:
            raise PilotBlocked("missing, duplicate, or orphan case identity")
        seen.add(cid)
        requested = row["requested_outcome"]
        if not isinstance(requested, str) or requested not in OUTCOMES:
            raise PilotBlocked("unrecognized or nonexclusive outcome class")
        if row["reference_origin"] != "LLM_PROPOSED":
            raise PilotBlocked("J or human cannot self-attest semantic Gold")
        obs = row["behavior_observation_sha256"]
        oracle = row["oracle_commitment_sha256"]
        if not _sha_or_null(obs) or not _sha_or_null(oracle):
            raise PilotBlocked("invalid observation/oracle commitment")
        if obs != original_cases[cid]["behavior_observation_sha256"]:
            raise PilotBlocked("swapped or post-frozen observation SHA")
        candidates[requested] += 1
        # A missing execution prerequisite, including model-declared BLOCKED,
        # is safely denied. Everything else is UNVERIFIED until separately
        # qualified trusted oracle + evidence authority is implemented.
        disposition = "BLOCKED" if requested == "BLOCKED" else "UNVERIFIED"
        admitted[disposition] += 1
        reported.append({
            "case_id": cid,
            "asset": original_cases[cid]["asset"],
            "candidate_outcome": requested,
            "admitted_outcome": disposition,
            "observation_reference_present": obs is not None,
            "oracle_commitment_present": oracle is not None,
            "independent_oracle_verified": False,
            "behavior_promotion_allowed": False,
        })
    if seen != set(original_cases):
        raise PilotBlocked("cohort loss or post-result substitution")
    all_outcomes = sorted(OUTCOMES)
    counts = {name: admitted[name] for name in all_outcomes}
    if sum(counts.values()) != 24:
        raise PilotBlocked("denominator/integrity failure")
    return {
        "schema_version": "v04-mla-unqualified-preflight-v1",
        "study_id": "V04-MLA-1",
        "status": ("BLOCKED_HUMAN_REVIEW_BUDGET"
                   if pilot_report["status"] == "BLOCKED_HUMAN_REVIEW_BUDGET"
                   else "PROVISIONAL_NO_INDEPENDENT_ORACLE"),
        "denominator": 24,
        "denominators_by_asset": pilot_report["asset_counts"],
        "candidate_outcome_counts": {name: candidates[name] for name in all_outcomes},
        "admitted_outcome_counts": counts,
        "cases": sorted(reported, key=lambda x: x["case_id"]),
        "human_sample_case_ids": pilot_report["human_sample_case_ids"],
        "human_review_card_count": pilot_report["human_review_card_count"],
        "human_review_card_budget": pilot_report["human_review_card_budget"],
        "original_se10_se11_studies_pass": False,
        "all_real_observation_digests_authenticated": False,
        "independent_behavior_oracles_verified": False,
        "human_decision_authority_verified": False,
        "empirical_success_claim_allowed": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
