"""Conservative private P/R/X conflict evidence and H mandatory-card derivation.

The *operator* may add mandatory review, but cannot suppress runtime-challenged
cases. The heuristic is an auditable upper-bound route, never a semantic oracle.
If required H cards exceed 12 the run BLOCKS instead of discarding cases.
The public-only reducer is deliberately not an authoritative H admission gate.
"""
from __future__ import annotations

import copy
from pathlib import Path

from scripts.v04_mla_pilot_reducer import (
    ASSETS, ROOT, PilotBlocked, assess, read_json,
)
from scripts.v04_mla_case_job_contract import verify_role_job_context
from scripts.v04_mla_role_case_payloads import validate_role_case_payloads

ROLES = ("P", "R", "X")


def derive_mandatory_h_review(pilot_public: dict, captures: dict,
                              source_selection_seed_sha256: str,
                              private_job_rows: list[dict], *,
                              repo_root: Path = ROOT) -> dict:
    """Derive non-downgradable H exceptions from all 24 frozen typed role rows.

    Require exact prospective jobs, all P/R/X envelopes and source-linked six
    rows per asset. Candidate P and counterhypothesis X are not proven opposing
    truth values; conservative review is mandatory for runtime-impact cases.
    """
    verified_jobs = verify_role_job_context(
        pilot_public, source_selection_seed_sha256, private_job_rows,
        captures, repo_root=repo_root)
    role_meta = validate_role_case_payloads(
        pilot_public, captures, repo_root=repo_root)
    expected = {c["case_id"]: c for c in pilot_public["cases"]}
    jobs = {j["case_id"]: j for j in private_job_rows}
    if (len(expected) != 24 or len(jobs) != 24 or set(jobs) != set(expected)):
        raise PilotBlocked("24 precommitted private intent rows required")
    found = {}
    for asset in ASSETS:
        role_rows = {}
        for role in ROLES:
            try:
                role_rows[role] = {
                    row["case_id"]: row
                    for row in read_json(captures[asset]["outputs"][role])["cases"]
                }
            except (TypeError, ValueError, KeyError) as exc:
                raise PilotBlocked("unusable independently typed role payload") from exc
        if any(len(role_rows[r]) != 6 for r in ROLES):
            raise PilotBlocked("incomplete six case role batch")
        for cid in role_rows["P"]:
            if any(cid not in role_rows[r] for r in ROLES):
                raise PilotBlocked("missing role counterpart for source case")
            job = jobs[cid]
            if (type(job.get("requires_runtime_observation")) is not bool
                    or job.get("evaluation_intent") != (
                        "BEHAVIOR_CANDIDATE" if job["requires_runtime_observation"]
                        else "SOURCE_SEMANTIC")):
                raise PilotBlocked("untrusted source-versus-runtime job intent")
            p, x = role_rows["P"][cid], role_rows["X"][cid]
            # The typed P is a positive candidate Capability hypothesis and
            # X is a nonempty adversarial hypothesis. Neither is truth.
            challenged = bool(p["proposal"].strip() and x["proposal"].strip())
            mandatory = challenged and job["requires_runtime_observation"]
            # A public operator may ALWAYS up-rank; it can never down-rank a
            # potential runtime high-impact conflict into four easy H cards.
            mandatory = mandatory or expected[cid]["high_impact_unresolved"]
            found[cid] = {
                "candidate_challenged": challenged,
                "behavior_requires_oracle": job["requires_runtime_observation"],
                "mandatory_h": mandatory,
            }
    if set(found) != set(expected):
        raise PilotBlocked("missing prospective case in derived conflict set")

    # Do not let any operator-selected false boolean erase a derived exception.
    augmented = copy.deepcopy(pilot_public)
    for row in augmented["cases"]:
        row["high_impact_unresolved"] = found[row["case_id"]]["mandatory_h"]
    selection = assess(repo_root, augmented)
    result = {
        "schema_version": "v04-mla-derived-conflict-h-cards-v1",
        "study_id": "V04-MLA-1",
        "status": selection["status"],
        "case_count": 24,
        "behavior_challenged_case_ids": sorted(
            cid for cid, meta in found.items()
            if meta["candidate_challenged"] and meta["behavior_requires_oracle"]),
        "candidate_challenged_case_count": sum(
            meta["candidate_challenged"] for meta in found.values()),
        "mandatory_h_case_ids": sorted(
            cid for cid, meta in found.items() if meta["mandatory_h"]),
        "human_sample_case_ids": selection["human_sample_case_ids"],
        "human_review_card_count": selection["human_review_card_count"],
        "human_review_card_budget": selection["human_review_card_budget"],
        "case_denominator_unchanged": 24,
        "role_job_context_validation": verified_jobs["status"],
        "role_metadata_validation": role_meta["status"],
        "caller_declared_false_may_suppress_derived_mandatory_case": False,
        "derived_challenge_is_semantic_truth": False,
        "authenticated_provider_calls_verified": False,
        "independent_calibrated_oracle_verified": False,
        "human_decisions_authoritative": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
    if result["human_review_card_count"] > 12:
        assert result["status"] == "BLOCKED_HUMAN_REVIEW_BUDGET"
    return result
