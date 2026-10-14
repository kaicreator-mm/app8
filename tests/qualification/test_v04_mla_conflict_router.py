"""Synthetic conservative H routing; source identities are real, role data fake."""
import json
import unittest
from unittest.mock import patch

from scripts.v04_mla_anchor_cohort import select_anchors
from scripts.v04_mla_conflict_router import derive_mandatory_h_review
from scripts.v04_mla_pilot_reducer import PilotBlocked, SOURCE_BLOB, ASSETS

SOURCE_SEED = "d" * 64


def example(behavior_count=1):
    slots = select_anchors(SOURCE_SEED)["slots"]
    jobs = []
    public_cases = []
    captures = {}
    for slot in slots:
        job = {
            **slot,
            "user_job": "synthetic task " + slot["case_id"],
            "claim_contract": "candidate source behavior",
            "negative_boundary": "counterexample not verified",
            "evaluation_intent": "SOURCE_SEMANTIC",
            "requires_runtime_observation": False,
            "origin": "OPERATOR_PROPOSED_NOT_GOLD",
        }
        jobs.append(job)
        public_cases.append({
            **slot,
            "model_prediction_sha256": "a" * 64,
            "reference_proposer_sha256": "b" * 64,
            "adversarial_challenger_sha256": "c" * 64,
            "source_verification_claim": "CANDIDATE_ONLY",
            "behavior_observation_sha256": None,
            "high_impact_unresolved": False,
            "oracle_visible_to_predictor": False,
            "model_consensus": False,
        })
    for asset in ASSETS:
        captures[asset] = {"outputs": {}}
        chosen = [slot for slot in slots if slot["asset"] == asset]
        for role in ("P", "R", "X"):
            batch = {"cases": [
                {"case_id": slot["case_id"], "source_anchor": slot["source_anchor"],
                 "proposal": f"hypothesis {role} {slot['case_id']}",
                 "constraints": ["synthetic only"]}
                for slot in chosen
            ]}
            captures[asset]["outputs"][role] = json.dumps(batch).encode()
    for job in jobs[:behavior_count]:
        job["requires_runtime_observation"] = True
        job["evaluation_intent"] = "BEHAVIOR_CANDIDATE"
    return {
        "schema_version": "v04-mla-pilot-public-v1",
        "study_id": "V04-MLA-1",
        "source_pack_git_blob": SOURCE_BLOB,
        "reference_origin": "LLM_PROPOSED",
        "frozen_before_model_outputs": True,
        "human_selection_seed_sha256": "9" * 64,
        "cases": public_cases,
    }, captures, jobs


def routed(public, captures, jobs):
    # Integration validators are independently exercised in their suites.
    # Mock only the validated provenance boundary; never fake a real model PASS.
    with patch("scripts.v04_mla_conflict_router.verify_role_job_context",
               return_value={"status": "STRUCTURAL_JOB_BOUND_NOT_TIME_ATTESTED"}), \
         patch("scripts.v04_mla_conflict_router.validate_role_case_payloads",
               return_value={"status": "STRUCTURAL_CANDIDATES_NO_ORACLE"}):
        return derive_mandatory_h_review(public, captures, SOURCE_SEED, jobs)


class ConflictRoutingTests(unittest.TestCase):
    def test_caller_false_cannot_hide_runtime_challenge(self):
        public, captures, jobs = example(1)
        self.assertFalse(public["cases"][0]["high_impact_unresolved"])
        report = routed(public, captures, jobs)
        self.assertIn(jobs[0]["case_id"], report["mandatory_h_case_ids"])
        self.assertFalse(report["authenticated_provider_calls_verified"])
        self.assertFalse(report["capability_promotion_allowed"])
        self.assertEqual(report["case_denominator_unchanged"], 24)

    def test_positive_operator_review_can_only_expand(self):
        public, captures, jobs = example(0)
        cid = public["cases"][7]["case_id"]
        public["cases"][7]["high_impact_unresolved"] = True
        report = routed(public, captures, jobs)
        self.assertIn(cid, report["mandatory_h_case_ids"])

    def test_more_than_twelve_mandatory_review_cards_is_blocked(self):
        public, captures, jobs = example(24)
        report = routed(public, captures, jobs)
        self.assertEqual(report["status"], "BLOCKED_HUMAN_REVIEW_BUDGET")
        self.assertEqual(len(report["mandatory_h_case_ids"]), 24)
        self.assertEqual(report["case_denominator_unchanged"], 24)

    def test_source_only_challenges_are_not_oracle_truth(self):
        public, captures, jobs = example(0)
        report = routed(public, captures, jobs)
        self.assertEqual(report["candidate_challenged_case_count"], 24)
        self.assertFalse(report["derived_challenge_is_semantic_truth"])
        self.assertEqual(report["mandatory_h_case_ids"], [])

    def test_mismatched_private_intent_blocks_routing(self):
        public, captures, jobs = example(1)
        jobs[0]["evaluation_intent"] = "SOURCE_SEMANTIC"
        with self.assertRaisesRegex(PilotBlocked, "intent"):
            routed(public, captures, jobs)

    def test_missing_role_case_denied(self):
        public, captures, jobs = example(0)
        asset = ASSETS[0]
        data = json.loads(captures[asset]["outputs"]["X"])
        data["cases"].pop()
        captures[asset]["outputs"]["X"] = json.dumps(data).encode()
        with self.assertRaisesRegex(PilotBlocked, "incomplete"):
            routed(public, captures, jobs)


if __name__ == "__main__":
    unittest.main()
