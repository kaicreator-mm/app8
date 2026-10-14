"""Bind prospective user jobs and claim boundaries to frozen source slots.

This is a deterministic digest compiler. Its output is NOT a trusted timestamp
or a claim of independently authored semantic Gold.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.v04_mla_anchor_cohort import validate_anchor_assignment
from scripts.v04_mla_pilot_reducer import ASSETS, ROOT, PilotBlocked, SOURCE_BLOB
from scripts.v04_mla_role_cohort_binding import bind_role_cohort

JOB_KEYS = frozenset({
    "case_id", "asset", "source_anchor", "user_job",
    "claim_contract", "negative_boundary", "evaluation_intent", "origin",
    "requires_runtime_observation",
})
INTENTS = frozenset({"SOURCE_SEMANTIC", "BEHAVIOR_CANDIDATE"})


def _json_sha(payload: object) -> str:
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _bounded(text: object, max_len: int) -> bool:
    return (isinstance(text, str) and 0 < len(text.strip()) <= max_len
            and "\x00" not in text)


def prepare_case_job_commitments(pilot_public: dict, seed_sha256: str,
                                 job_rows: list[dict],
                                 *, repo_root: Path = ROOT) -> dict:
    """Check 24 case-to-job contracts; publish only SHA256 digests, not jobs."""
    frozen = validate_anchor_assignment(pilot_public, seed_sha256,
                                        repo_root=repo_root)
    if not isinstance(job_rows, list) or len(job_rows) != 24:
        raise PilotBlocked("exactly 24 pre-result user jobs required")
    lookup = {x["case_id"]: x for x in pilot_public["cases"]}
    seen: set[str] = set()
    by_asset: dict[str, list[dict]] = {a: [] for a in ASSETS}
    for job in job_rows:
        if not isinstance(job, dict) or set(job) != JOB_KEYS:
            raise PilotBlocked("private truth field or missing job contract")
        cid = job["case_id"]
        if not isinstance(cid, str) or cid not in lookup or cid in seen:
            raise PilotBlocked("orphan or duplicate prospective job case")
        seen.add(cid)
        pilot = lookup[cid]
        if (job["asset"] != pilot["asset"]
                or job["source_anchor"] != pilot["source_anchor"]
                or job["origin"] != "OPERATOR_PROPOSED_NOT_GOLD"
                or not isinstance(job["evaluation_intent"], str)
                or job["evaluation_intent"] not in INTENTS
                or type(job["requires_runtime_observation"]) is not bool
                or job["evaluation_intent"] != (
                    "BEHAVIOR_CANDIDATE" if job["requires_runtime_observation"]
                    else "SOURCE_SEMANTIC")):
            raise PilotBlocked("job source, intent or independent-Gold claim mismatch")
        if (not _bounded(job["user_job"], 2400)
                or not _bounded(job["claim_contract"], 2400)
                or not _bounded(job["negative_boundary"], 800)):
            raise PilotBlocked("invalid or incomplete semantic job contract")
        by_asset[pilot["asset"]].append(job)
    if seen != set(lookup):
        raise PilotBlocked("unfrozen missing job IDs")
    job_hashes = {}
    contexts = {}
    for asset in ASSETS:
        jobs = sorted(by_asset[asset], key=lambda job: job["case_id"])
        if len(jobs) != 6:
            raise PilotBlocked("each asset needs exactly six prospective user jobs")
        job_hashes[asset] = {job["case_id"]: _json_sha(job) for job in jobs}
        contexts[asset] = _json_sha({
            "schema_version": "v04-mla-asset-job-context-v1",
            "asset": asset,
            "source_pack_git_blob": SOURCE_BLOB,
            "case_job_sha256": job_hashes[asset],
        })
    return {
        "schema_version": "v04-mla-case-job-commitments-v1",
        "study_id": "V04-MLA-1",
        "case_denominator": 24,
        "anchor_assignment_sha256": frozen["anchor_assignment_sha256"],
        "job_contract_digests_by_asset": job_hashes,
        "asset_source_context_sha256": contexts,
        "user_job_authority_independently_verified": False,
        "job_semantics_validated": False,
        "trusted_pre_prediction_freeze_attested": False,
        "reference_gold_verified": False,
        "empirical_qualification_pass": False,
        "formal_product_release_qualified": False,
    }


def verify_role_job_context(pilot_public: dict, seed_sha256: str,
                            job_rows: list[dict], captures: dict, *,
                            repo_root: Path = ROOT) -> dict:
    """Require all captured role input contexts to match exact prospective jobs."""
    identity = prepare_case_job_commitments(
        pilot_public, seed_sha256, job_rows, repo_root=repo_root)
    capture = bind_role_cohort(pilot_public, captures, repo_root=repo_root)
    for asset in ASSETS:
        if (capture["assets"][asset]["source_context_sha256"]
                != identity["asset_source_context_sha256"][asset]):
            raise PilotBlocked("P/R/X frozen source context is not bound to user jobs")
    return {
        "schema_version": "v04-mla-case-job-role-binding-v1",
        "study_id": "V04-MLA-1",
        "status": "STRUCTURAL_JOB_BOUND_NOT_TIME_ATTESTED",
        "case_denominator": 24,
        "anchor_assignment_sha256": identity["anchor_assignment_sha256"],
        "asset_source_context_sha256": identity["asset_source_context_sha256"],
        "role_capture_status": capture["status"],
        "trusted_pre_prediction_freeze_attested": False,
        "trusted_provider_invocation_proven": False,
        "independent_behavior_oracle_verified": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
