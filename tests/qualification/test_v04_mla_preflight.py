"""Synthetic conservative MLA preflight tests (no model/provider/host truth)."""
from __future__ import annotations

import copy
import unittest

import hashlib
import json

from app8.mla.preflight import reduce_evidence_preflight
from scripts.v04_mla_pilot_reducer import PilotBlocked, ROOT, ALLOWLIST, SOURCE_BLOB


def synthetic_pilot():
    anchors = json.loads((ROOT / ALLOWLIST).read_text(encoding="utf-8"))["assets"]
    cases = []
    for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice"):
        path, blob = sorted(anchors[asset].items())[0]
        for i in range(6):
            cases.append({
                "case_id": "V04-" + asset.upper() + "-" + str(i + 1).zfill(3),
                "asset": asset,
                "source_anchor": {"path": path, "blob": blob},
                "model_prediction_sha256": "a" * 64,
                "reference_proposer_sha256": "b" * 64,
                "adversarial_challenger_sha256": "c" * 64,
                "source_verification_claim": "CANDIDATE_ONLY",
                "behavior_observation_sha256": None,
                "high_impact_unresolved": False,
                "oracle_visible_to_predictor": False,
                "model_consensus": False,
            })
    return {
        "schema_version": "v04-mla-pilot-public-v1",
        "study_id": "V04-MLA-1",
        "source_pack_git_blob": SOURCE_BLOB,
        "reference_origin": "LLM_PROPOSED",
        "frozen_before_model_outputs": True,
        "human_selection_seed_sha256": hashlib.sha256(b"precommitted-test-seed").hexdigest(),
        "cases": cases,
    }


def rows(pilot):
    return [{
        "case_id": c["case_id"],
        "requested_outcome": "BEHAVIOR_SUPPORTED",
        "reference_origin": "LLM_PROPOSED",
        "behavior_observation_sha256": c["behavior_observation_sha256"],
    } for c in pilot["cases"]]


class UnqualifiedEvidencePreflightTests(unittest.TestCase):
    def test_24_promoted_claims_remain_unverified(self):
        pilot = synthetic_pilot()
        report = reduce_evidence_preflight(pilot, rows(pilot))
        self.assertEqual(report["denominator"], 24)
        self.assertEqual(report["admitted_outcome_counts"]["BEHAVIOR_SUPPORTED"], 0)
        self.assertEqual(report["admitted_outcome_counts"]["UNVERIFIED"], 24)
        self.assertFalse(report["empirical_success_claim_allowed"])
        self.assertFalse(report["capability_promotion_allowed"])
        self.assertFalse(report["formal_product_release_qualified"])

    def test_source_only_cannot_be_behavior_evidence(self):
        pilot = synthetic_pilot()
        claims = rows(pilot)
        claims[0]["requested_outcome"] = "SOURCE_SUPPORTED_ONLY"
        result = reduce_evidence_preflight(pilot, claims)
        self.assertEqual(result["admitted_outcome_counts"]["SOURCE_SUPPORTED_ONLY"], 0)

    def test_rebuttal_without_independent_oracle_not_refutation(self):
        pilot = synthetic_pilot()
        claims = rows(pilot)
        claims[0]["requested_outcome"] = "REFUTED"
        claims[1]["requested_outcome"] = "NARROWED"
        result = reduce_evidence_preflight(pilot, claims)
        self.assertEqual(result["admitted_outcome_counts"]["REFUTED"], 0)
        self.assertEqual(result["admitted_outcome_counts"]["NARROWED"], 0)

    def test_blocked_cases_stay_in_denominator(self):
        pilot = synthetic_pilot()
        claims = rows(pilot)
        claims[0]["requested_outcome"] = "BLOCKED"
        claims[1]["requested_outcome"] = "BLOCKED"
        result = reduce_evidence_preflight(pilot, claims)
        self.assertEqual(result["denominator"], 24)
        self.assertEqual(result["admitted_outcome_counts"]["BLOCKED"], 2)
        self.assertEqual(result["admitted_outcome_counts"]["UNVERIFIED"], 22)

    def test_orphan_case_rejected(self):
        pilot = synthetic_pilot()
        claims = rows(pilot)
        claims[0]["case_id"] = "V04-UNKNOWN-999"
        with self.assertRaisesRegex(PilotBlocked, "orphan"):
            reduce_evidence_preflight(pilot, claims)

    def test_repeated_case_rejected(self):
        pilot = synthetic_pilot()
        claims = rows(pilot)
        claims[0]["case_id"] = claims[1]["case_id"]
        with self.assertRaisesRegex(PilotBlocked, "duplicate"):
            reduce_evidence_preflight(pilot, claims)

    def test_missing_case_cannot_reduce_denominator(self):
        pilot = synthetic_pilot()
        with self.assertRaisesRegex(PilotBlocked, "24 non-replaceable"):
            reduce_evidence_preflight(pilot, rows(pilot)[:-1])

    def test_hidden_truth_and_human_self_attestation_rejected(self):
        pilot = synthetic_pilot()
        claims = rows(pilot)
        claims[0]["hidden_truth"] = "yes"
        with self.assertRaisesRegex(PilotBlocked, "truth"):
            reduce_evidence_preflight(pilot, claims)
        claims = rows(pilot)
        claims[0]["reference_origin"] = "INDEPENDENT_HUMAN_GOLD"
        with self.assertRaisesRegex(PilotBlocked, "self-attest"):
            reduce_evidence_preflight(pilot, claims)

    def test_judge_self_grading_forbidden(self):
        pilot = synthetic_pilot()
        claims = rows(pilot)
        claims[0]["reference_origin"] = "JUDGE_LLM"
        with self.assertRaisesRegex(PilotBlocked, "J or human"):
            reduce_evidence_preflight(pilot, claims)

    def test_swapped_observation_binding_is_rejected(self):
        pilot = synthetic_pilot()
        pilot["cases"][0]["behavior_observation_sha256"] = "a" * 64
        claims = rows(pilot)
        claims[0]["behavior_observation_sha256"] = "b" * 64
        with self.assertRaisesRegex(PilotBlocked, "swapped"):
            reduce_evidence_preflight(pilot, claims)

    def test_oracle_commitment_not_allowed_in_public_status(self):
        pilot = synthetic_pilot()
        claims = rows(pilot)
        claims[0]["oracle_commitment_sha256"] = "c" * 64
        with self.assertRaisesRegex(PilotBlocked, "unexpected candidate fields"):
            reduce_evidence_preflight(pilot, claims)

    def test_human_exception_budget_fail_closed(self):
        pilot = synthetic_pilot()
        for c in pilot["cases"][:16]:
            c["high_impact_unresolved"] = True
        result = reduce_evidence_preflight(pilot, rows(pilot))
        self.assertEqual(result["status"], "BLOCKED_HUMAN_REVIEW_BUDGET")
        self.assertFalse(result["capability_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
