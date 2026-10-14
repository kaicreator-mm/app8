"""Synthetic structural adversarial reducer tests; NOT real semantic/behavioral evidence."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.v04_mla_pilot_reducer import (
    ALLOWLIST, ROOT, SOURCE_BLOB, PilotBlocked, assess, read_json,
)


def synthetic_pilot():
    anchors = json.loads((ROOT / ALLOWLIST).read_text(encoding="utf-8"))["assets"]
    cases = []
    for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice"):
        one_path, one_sha = sorted(anchors[asset].items())[0]
        for i in range(6):
            cases.append({
                "case_id": "V04-" + asset.upper() + "-" + str(i + 1).zfill(3),
                "asset": asset,
                "source_anchor": {"path": one_path, "blob": one_sha},
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
        "human_selection_seed_sha256": hashlib.sha256(b"precommitted-seed").hexdigest(),
        "cases": cases,
    }


class MLAStageOneTests(unittest.TestCase):
    def test_24_cases_four_assets_minimal_four_review_cards(self):
        result = assess(ROOT, synthetic_pilot())
        self.assertEqual(result["case_count"], 24)
        self.assertEqual(result["asset_counts"],
                         {"FFmpeg": 6, "pandas": 6, "MinIO": 6, "LibreOffice": 6})
        self.assertEqual(result["human_review_card_count"], 4)
        self.assertFalse(result["eligible_for_capability_promotion"])
        self.assertFalse(result["formal_product_release_qualified"])
        self.assertFalse(result["behavioral_truth_verified"])
        self.assertIn("PROVISIONAL", result["status"])

    def test_seeded_selection_is_deterministic(self):
        a = assess(ROOT, synthetic_pilot())
        b = assess(ROOT, synthetic_pilot())
        self.assertEqual(a["human_sample_case_ids"], b["human_sample_case_ids"])

    def test_unresolved_high_impact_always_selected(self):
        trial = synthetic_pilot()
        trial["cases"][0]["high_impact_unresolved"] = True
        res = assess(ROOT, trial)
        self.assertIn(trial["cases"][0]["case_id"], res["human_sample_case_ids"])

    def test_human_review_card_budget_overflow_blocks(self):
        trial = synthetic_pilot()
        for case in trial["cases"][:16]:
            case["high_impact_unresolved"] = True
        res = assess(ROOT, trial)
        self.assertGreater(res["human_review_card_count"], 12)
        self.assertEqual(res["status"], "BLOCKED_HUMAN_REVIEW_BUDGET")
        self.assertFalse(res["eligible_for_capability_promotion"])

    def test_fake_human_authorship_rejected(self):
        trial = synthetic_pilot()
        trial["reference_origin"] = "INDEPENDENT_HUMAN_GOLD"
        with self.assertRaises(PilotBlocked):
            assess(ROOT, trial)

    def test_model_consensus_never_promotes(self):
        trial = synthetic_pilot()
        for case in trial["cases"]:
            case["model_consensus"] = True
            case["behavior_observation_sha256"] = "d" * 64
        res = assess(ROOT, trial)
        self.assertFalse(res["observation_digests_verified"])
        self.assertFalse(res["behavioral_truth_verified"])
        self.assertFalse(res["eligible_for_capability_promotion"])

    def test_hidden_oracle_exposure_fails_closed(self):
        trial = synthetic_pilot()
        trial["cases"][0]["oracle_visible_to_predictor"] = True
        with self.assertRaises(PilotBlocked):
            assess(ROOT, trial)

    def test_extra_truth_field_leak_rejected(self):
        trial = synthetic_pilot()
        trial["cases"][0]["truth_class"] = "TRUE"
        with self.assertRaises(PilotBlocked):
            assess(ROOT, trial)

    def test_swapped_source_anchor_rejected(self):
        trial = synthetic_pilot()
        trial["cases"][0]["source_anchor"]["blob"] = "0" * 40
        with self.assertRaises(PilotBlocked):
            assess(ROOT, trial)

    def test_duplicate_case_id_rejected(self):
        trial = synthetic_pilot()
        trial["cases"][1]["case_id"] = trial["cases"][0]["case_id"]
        with self.assertRaises(PilotBlocked):
            assess(ROOT, trial)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(PilotBlocked):
            read_json(b'{"study_id":1,"study_id":2}')

    def test_original_allowlist_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / ALLOWLIST
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / ALLOWLIST, p)
            with p.open("ab") as f:
                f.write(b" ")
            with self.assertRaises(PilotBlocked):
                assess(Path(td), synthetic_pilot())

    def test_schema_accepts_synthetic_pilot_if_jsonschema_available(self):
        import jsonschema
        schema = json.loads(
            (ROOT / "research/mla/v04-mla-pilot-public.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(synthetic_pilot())


if __name__ == "__main__":
    unittest.main()
