"""Synthetic per-case precommitted job/source context tests."""
import json
import hashlib
import unittest

from app8.mla.blind_capture import VIS
from scripts.v04_mla_anchor_cohort import select_anchors
from scripts.v04_mla_case_job_contract import (
    prepare_case_job_commitments, verify_role_job_context
)
from scripts.v04_mla_pilot_reducer import SOURCE_BLOB, PilotBlocked

SEED = "d" * 64


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fixture():
    slots = select_anchors(SEED)["slots"]
    jobs = [{
        "case_id": slot["case_id"],
        "asset": slot["asset"],
        "source_anchor": slot["source_anchor"],
        "user_job": "Untrusted fixture job " + slot["case_id"],
        "claim_contract": "Fixture description of a bounded source capability",
        "negative_boundary": "Fixture counterexample, no real execution",
        "evaluation_intent": "SOURCE_SEMANTIC",
        "origin": "OPERATOR_PROPOSED_NOT_GOLD",
    } for slot in slots]
    return slots, jobs


def pilot(slots):
    return {
        "schema_version": "v04-mla-pilot-public-v1",
        "study_id": "V04-MLA-1",
        "source_pack_git_blob": SOURCE_BLOB,
        "reference_origin": "LLM_PROPOSED",
        "frozen_before_model_outputs": True,
        "human_selection_seed_sha256": "a" * 64,
        "cases": [{
            **slot,
            "model_prediction_sha256": "b" * 64,
            "reference_proposer_sha256": "c" * 64,
            "adversarial_challenger_sha256": "d" * 64,
            "source_verification_claim": "CANDIDATE_ONLY",
            "behavior_observation_sha256": None,
            "high_impact_unresolved": False,
            "oracle_visible_to_predictor": False,
            "model_consensus": False,
        } for slot in slots],
    }


def capture_fixture(p, jobs):
    identity = prepare_case_job_commitments(p, SEED, jobs)
    captures = {}
    for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice"):
        ctx = identity["asset_source_context_sha256"][asset]
        freeze = {
            "schema_version": "v04-mla-blind-freeze-v1",
            "study_id": "V04-MLA-1", "source_pack_git_blob": SOURCE_BLOB,
            "frozen_before_first_response": True,
            "source_context_sha256": ctx, "roles": {},
        }
        inputs = {}
        outputs = {}
        for role in ("P", "R", "X"):
            input_object = {
                "source_pack_git_blob": SOURCE_BLOB,
                "source_context_sha256": ctx,
                "task_instruction_sha256": sha((role + asset).encode()),
                "visibility_scope": VIS[role],
            }
            inputs[role] = (json.dumps(input_object, sort_keys=True) + "\n").encode()
            outputs[role] = ("synthetic-" + asset + "-" + role).encode()
            freeze["roles"][role] = {
                "model_family": "family-" + role, "provider": "fixture-only",
                "model_version": "v1",
                "prompt_sha256": sha((role + asset + "prompt").encode()),
                "sampling_sha256": sha((role + asset + "sampling").encode()),
                "input_sha256": sha(inputs[role]),
            }
        captures[asset] = {"freeze": freeze, "inputs": inputs, "outputs": outputs}
        for case in p["cases"]:
            if case["asset"] == asset:
                case["model_prediction_sha256"] = sha(outputs["P"])
                case["reference_proposer_sha256"] = sha(outputs["R"])
                case["adversarial_challenger_sha256"] = sha(outputs["X"])
    return captures


class ProspectiveJobContractTests(unittest.TestCase):
    def test_complete_24_job_hashes_and_four_contexts(self):
        slots, jobs = fixture()
        out = prepare_case_job_commitments(pilot(slots), SEED, jobs)
        self.assertEqual(out["case_denominator"], 24)
        self.assertEqual(len(out["asset_source_context_sha256"]), 4)
        self.assertFalse(out["trusted_pre_prediction_freeze_attested"])
        self.assertNotIn("user_job", str(out))

    def test_prepared_jobs_bind_to_role_inputs(self):
        slots, jobs = fixture()
        p = pilot(slots)
        cap = capture_fixture(p, jobs)
        out = verify_role_job_context(p, SEED, jobs, cap)
        self.assertEqual(out["status"], "STRUCTURAL_JOB_BOUND_NOT_TIME_ATTESTED")
        self.assertFalse(out["trusted_provider_invocation_proven"])

    def test_job_changed_after_capture_rejected(self):
        slots, jobs = fixture()
        p = pilot(slots)
        cap = capture_fixture(p, jobs)
        jobs[0]["user_job"] += " post-hoc change"
        with self.assertRaisesRegex(PilotBlocked, "not bound"):
            verify_role_job_context(p, SEED, jobs, cap)

    def test_wrong_source_anchor_rejected(self):
        slots, jobs = fixture()
        jobs[0]["source_anchor"] = slots[1]["source_anchor"]
        with self.assertRaisesRegex(PilotBlocked, "source"):
            prepare_case_job_commitments(pilot(slots), SEED, jobs)

    def test_hidden_truth_in_job_contract_rejected(self):
        slots, jobs = fixture()
        jobs[0]["oracle_truth"] = True
        with self.assertRaisesRegex(PilotBlocked, "private truth"):
            prepare_case_job_commitments(pilot(slots), SEED, jobs)

    def test_duplicate_job_rejected(self):
        slots, jobs = fixture()
        jobs[0]["case_id"] = jobs[1]["case_id"]
        with self.assertRaisesRegex(PilotBlocked, "duplicate"):
            prepare_case_job_commitments(pilot(slots), SEED, jobs)

    def test_empty_job_rejected(self):
        slots, jobs = fixture()
        jobs[0]["user_job"] = ""
        with self.assertRaisesRegex(PilotBlocked, "incomplete"):
            prepare_case_job_commitments(pilot(slots), SEED, jobs)

    def test_operator_cannot_claim_human_gold(self):
        slots, jobs = fixture()
        jobs[0]["origin"] = "INDEPENDENT_HUMAN_GOLD"
        with self.assertRaisesRegex(PilotBlocked, "Gold"):
            prepare_case_job_commitments(pilot(slots), SEED, jobs)

    def test_changed_seed_rejects_frozen_source_assignments(self):
        slots, jobs = fixture()
        with self.assertRaises(PilotBlocked):
            prepare_case_job_commitments(pilot(slots), "a" * 64, jobs)

    def test_truncated_jobs_rejected(self):
        slots, jobs = fixture()
        with self.assertRaisesRegex(PilotBlocked, "exactly 24"):
            prepare_case_job_commitments(pilot(slots), SEED, jobs[:-1])


if __name__ == "__main__":
    unittest.main()
