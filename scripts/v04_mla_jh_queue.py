"""Bounded J/H audit candidate queue for MLA. Never confers review authority.

J is optional and only for predeclared high-impact unresolved cases.
H submissions here are *unverified*, even if signed-looking digests exist.
The private, authoritative reviewer service belongs to a separate gate.
"""
from __future__ import annotations

from pathlib import Path
import re

from scripts.v04_mla_pilot_reducer import ROOT, PilotBlocked, assess

SHA = re.compile(r"[0-9a-f]{64}\Z")
J_KEYS = frozenset({
    "case_id", "reference_origin", "model_family", "provider",
    "prompt_sha256", "config_sha256", "response_sha256",
})
H_KEYS = frozenset({
    "case_id", "decision", "decision_origin", "reviewer_id_sha256",
    "evidence_ref_sha256", "submission_sha256",
})
DECISIONS = frozenset({"CONFIRM", "REJECT", "DEFER"})


def _sha(value: object) -> bool:
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def build_jh_candidate_queue(pilot_public: dict, judge_rows: list[dict],
                             human_rows: list[dict], *,
                             repo_root: Path = ROOT) -> dict:
    """Validate bounded untrusted J/H metadata with no authority promotion."""
    base = assess(repo_root, pilot_public)
    selected = set(base["human_sample_case_ids"])
    cases = {case["case_id"]: case for case in pilot_public["cases"]}
    if not isinstance(judge_rows, list) or len(judge_rows) > 24:
        raise PilotBlocked("invalid J escalation budget")
    if not isinstance(human_rows, list) or len(human_rows) > 12:
        raise PilotBlocked("invalid H submission budget")
    judges: set[str] = set()
    for row in judge_rows:
        if not isinstance(row, dict) or set(row) != J_KEYS:
            raise PilotBlocked("J field leakage or missing commitment")
        cid = row["case_id"]
        if (not isinstance(cid, str) or cid not in cases
                or not cases[cid]["high_impact_unresolved"] or cid in judges):
            raise PilotBlocked("J requires one eligible predeclared conflict per case")
        if row["reference_origin"] != "LLM_PROPOSED":
            raise PilotBlocked("J cannot claim oracle or human Gold authority")
        if any(not isinstance(row[k], str) or not row[k].strip()
               for k in ("model_family", "provider")):
            raise PilotBlocked("missing J model identity")
        if any(not _sha(row[k])
               for k in ("prompt_sha256", "config_sha256", "response_sha256")):
            raise PilotBlocked("invalid J transcript commitment")
        judges.add(cid)

    submissions: set[str] = set()
    deferred: set[str] = set()
    counts = {"CONFIRM": 0, "REJECT": 0, "DEFER": 0}
    for row in human_rows:
        if not isinstance(row, dict) or set(row) != H_KEYS:
            raise PilotBlocked("H field leakage or authority assertion")
        cid = row["case_id"]
        if not isinstance(cid, str) or cid not in selected or cid in submissions:
            raise PilotBlocked("H decision outside precommitted sample or duplicate")
        if (row["decision"] not in DECISIONS
                or row["decision_origin"] != "HUMAN_SELF_REPORT_UNVERIFIED"
                or any(not _sha(row[k]) for k in
                       ("reviewer_id_sha256", "evidence_ref_sha256",
                        "submission_sha256"))):
            raise PilotBlocked("invalid or claimed-authoritative H submission")
        submissions.add(cid)
        counts[row["decision"]] += 1
        if row["decision"] == "DEFER":
            deferred.add(cid)

    missing = selected - submissions
    if base["status"] == "BLOCKED_HUMAN_REVIEW_BUDGET":
        status = "BLOCKED_HUMAN_REVIEW_BUDGET"
    elif missing or deferred:
        status = "BLOCKED_HUMAN_REVIEW_PENDING_OR_DEFERRED"
    else:
        status = "PROVISIONAL_H_SUBMISSIONS_UNVERIFIED"

    return {
        "schema_version": "v04-mla-jh-candidate-queue-v1",
        "study_id": "V04-MLA-1",
        "status": status,
        "denominator": 24,
        "required_human_case_ids": sorted(selected),
        "missing_human_case_ids": sorted(missing),
        "deferred_human_case_ids": sorted(deferred),
        "reported_human_decision_counts": counts,
        "reported_j_escalation_case_ids": sorted(judges),
        "judge_transcripts_authoritative": False,
        "human_identity_and_decision_verified": False,
        "human_gold_authorship_verified": False,
        "oracle_verified": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
