"""Synthetic deterministic MLA anchor selection, no LLM or host oracles."""
import copy
import json
import unittest
from scripts.v04_mla_anchor_cohort import select_anchors, validate_anchor_assignment
from scripts.v04_mla_pilot_reducer import (
    ALLOWLIST, ROOT, SOURCE_BLOB, PilotBlocked
)

SEED = "d" * 64


def pilot():
    cohort = select_anchors(SEED)
    cases = []
    for slot in cohort["slots"]:
        cases.append({
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
    return {
        "schema_version": "v04-mla-pilot-public-v1",
        "study_id": "V04-MLA-1", "source_pack_git_blob": SOURCE_BLOB,
        "reference_origin": "LLM_PROPOSED",
        "frozen_before_model_outputs": True,
        "human_selection_seed_sha256": "f" * 64,
        "cases": cases,
    }


class DeterministicAnchorCohortTests(unittest.TestCase):
    def test_exact_24_distinct_source_slots(self):
        x = select_anchors(SEED)
        self.assertEqual(len(x["slots"]), 24)
        for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice"):
            group = [row for row in x["slots"] if row["asset"] == asset]
            self.assertEqual(len(group), 6)
            self.assertEqual(len({r["source_anchor"]["path"] for r in group}), 6)
        self.assertFalse(x["pre_prediction_freeze_attested"])

    def test_seed_is_reproducible(self):
        a, b = select_anchors(SEED), select_anchors(SEED)
        self.assertEqual(a["anchor_assignment_sha256"], b["anchor_assignment_sha256"])
        self.assertEqual(a["slots"], b["slots"])

    def test_valid_pilot_cohort_matches_prechosen_anchors(self):
        v = validate_anchor_assignment(pilot(), SEED)
        self.assertEqual(v["denominator"], 24)
        self.assertFalse(v["behavior_promotion_allowed"])

    def test_seed_change_rejects_assignment(self):
        p = pilot()
        other = "0" * 64
        if select_anchors(SEED)["slots"] == select_anchors(other)["slots"]:
            self.skipTest("astronomically unlikely identical choice")
        with self.assertRaisesRegex(PilotBlocked, "differs"):
            validate_anchor_assignment(p, other)

    def test_different_valid_anchor_is_still_rejected(self):
        p = pilot()
        allow = json.loads((ROOT / ALLOWLIST).read_text(encoding="utf-8"))["assets"]
        first = p["cases"][0]
        source = first["source_anchor"]
        replacement = next((path, blob) for path, blob in allow["FFmpeg"].items()
                           if path != source["path"])
        first["source_anchor"] = {"path": replacement[0], "blob": replacement[1]}
        with self.assertRaisesRegex(PilotBlocked, "differs"):
            validate_anchor_assignment(p, SEED)

    def test_anchor_slot_swap_rejected(self):
        p = pilot()
        p["cases"][0]["source_anchor"], p["cases"][1]["source_anchor"] = (
            p["cases"][1]["source_anchor"], p["cases"][0]["source_anchor"])
        with self.assertRaisesRegex(PilotBlocked, "differs"):
            validate_anchor_assignment(p, SEED)

    def test_duplicate_case_id_rejected(self):
        p = pilot()
        p["cases"][1]["case_id"] = p["cases"][0]["case_id"]
        with self.assertRaises(PilotBlocked):
            validate_anchor_assignment(p, SEED)

    def test_shortened_cohort_rejected(self):
        p = pilot()
        p["cases"].pop()
        with self.assertRaises(PilotBlocked):
            validate_anchor_assignment(p, SEED)

    def test_invalid_seed_fail_closed(self):
        with self.assertRaisesRegex(PilotBlocked, "seed required"):
            select_anchors("not-a-sha")

    def test_output_never_claims_oracle_or_freeze(self):
        a = select_anchors(SEED)
        b = validate_anchor_assignment(pilot(), SEED)
        self.assertFalse(a["semantic_reference_gold_verified"])
        self.assertFalse(b["pre_prediction_freeze_attested"])
        self.assertFalse(b["independent_oracle_verified"])
        self.assertFalse(b["formal_product_release_qualified"])


if __name__ == "__main__":
    unittest.main()
