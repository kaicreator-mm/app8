"""Synthetic tests for PUBLIC metadata preflight; NOT empirical study evidence."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.v04_empirical_public_preflight import assess, PINS, REPO_ROOT

SHA = "a" * 64
IMAGE = "b" * 64
ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")


def write(path, obj):
    path.write_text(json.dumps(obj, sort_keys=True) + "\n", encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fake_se10_gold():
    return {
        "schema_version": "se10-public-commitment-v1",
        "source_pack_blob": PINS["se10_source_pack"][1],
        "allowlist_git_blob": PINS["se10_allowlist"][1],
        "gold_file_sha256": SHA,
        "independent_attestation_sha256": IMAGE,
        "human_independence_requires_external_review": True,
        "declared_model_generated_gold": False,
        "declared_predictor_gold_visibility": False,
        "semantic_gold_in_public_output": False,
        "private_store_independent_reviewed": True,
        "asset_counts": {a: 12 for a in ASSETS},
        "capability_count": 48,
    }


def fake_target():
    mapping = {
        "execution_target_ref": "operator-reported-target",
        "relation": "SAME",
        "applicability_review_sha256": SHA,
        "applicability_review_status": "PASS",
        "approved_applicability_evidence": [
            {"evidence_kind": "EXACT_SOURCE_IDENTITY", "evidence_sha256": IMAGE}],
    }
    return {
        "schema_version": "se11-execution-target-manifest-v1",
        "source_execution_mappings": {a: dict(mapping) for a in ASSETS},
    }


def fake_hidden(manifest_sha):
    return {
        "schema_version": "se11-public-commitment-v1",
        "execution_target_manifest_sha256": manifest_sha,
        "stage_a_merge": "0279968580d50e51843b09aa2b6e266b9967ff93",
        "hidden_file_sha256": SHA,
        "claim_count": 80,
        "asset_counts": {a: 20 for a in ASSETS},
        "aggregate_class_counts": {"TRUE":32, "MATERIALLY_FALSE":16,
                                   "OVERBROAD":16, "NEAR_MISS":16},
        "opaque_claim_ids": [f"H_{i:032x}" for i in range(80)],
        "truth_visible_to_llm_b": False,
        "decisive_fixtures_visible_to_llm_b": False,
        "semantic_truth_in_public_output": False,
    }


class V04PublicPreflightTests(unittest.TestCase):
    def test_missing_private_commitments_are_blocked_not_pass(self):
        r = assess(REPO_ROOT)
        self.assertEqual(r["se10"], "BLOCKED_PRE_EVALUATION")
        self.assertEqual(r["se11"], "BLOCKED_PRE_EVALUATION")
        self.assertEqual(len(r["blocked_reasons"]), 4)
        self.assertFalse(r["formal_product_release_qualified"])
        self.assertFalse(r["independent_truth_and_real_execution_verified"])

    def test_synthetic_consistent_public_metadata_never_proves_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gp, pp, mp, hp = (root / x for x in ("g.json", "p.json", "m.json", "h.json"))
            goldsha = write(gp, fake_se10_gold())
            write(pp, {"schema_version": "se10-prediction-commitment-v1",
                       "gold_commitment_sha256": goldsha, "gold_file_sha256": SHA,
                       "prediction_file_sha256": IMAGE})
            targetsha = write(mp, fake_target())
            write(hp, fake_hidden(targetsha))
            r = assess(REPO_ROOT, gp, pp, mp, hp)
            self.assertFalse(r["blocked_reasons"])
            self.assertEqual(r["se10"], "PUBLIC_METADATA_PRESENT_UNVERIFIED_INDEPENDENCE")
            self.assertEqual(r["se11"], "PUBLIC_METADATA_PRESENT_UNVERIFIED_INDEPENDENCE")
            self.assertEqual(r["se10_empirical"], "NOT_PROVEN")
            self.assertEqual(r["se11_empirical"], "NOT_PROVEN")
            self.assertFalse(r["formal_product_release_qualified"])

    def test_hidden_manifest_digest_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mp, hp = root / "m.json", root / "h.json"
            write(mp, fake_target())
            write(hp, fake_hidden("f" * 64))
            r = assess(REPO_ROOT, se11_target=mp, se11_hidden=hp)
            self.assertIn("SE11_HIDDEN_COMMITMENT:PIN_OR_SCHEMA_MISMATCH",
                          r["blocked_reasons"])
            self.assertEqual(r["se11"], "BLOCKED_PRE_EVALUATION")

    def test_gold_wrong_source_pack_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            gp = Path(directory) / "g.json"
            bad = fake_se10_gold()
            bad["source_pack_blob"] = "0" * 40
            write(gp, bad)
            r = assess(REPO_ROOT, se10_gold=gp)
            self.assertIn("SE10_GOLD_COMMITMENT:INVALID_FROZEN_METADATA",
                          r["blocked_reasons"])

    def test_reject_duplicate_public_json_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            gp = Path(directory) / "g.json"
            gp.write_text('{"schema_version":"x","schema_version":"y"}',
                          encoding="utf-8")
            r = assess(REPO_ROOT, se10_gold=gp)
            self.assertIn("SE10_GOLD_COMMITMENT:INVALID_PUBLIC_JSON",
                          r["blocked_reasons"])

    def test_modified_source_pack_byte_invalidates_qualification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for _, (relative, _) in PINS.items():
                source, dest = REPO_ROOT / relative, root / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
            with (root / PINS["se11_protocol"][0]).open("ab") as stream:
                stream.write(b"\nnot-reviewed")
            r = assess(root)
            self.assertIn("se11_protocol:EXACT_GIT_BLOB_DRIFT", r["blocked_reasons"])
            self.assertEqual(r["se10"], "BLOCKED_PRE_EVALUATION")
            self.assertEqual(r["se11"], "BLOCKED_PRE_EVALUATION")


if __name__ == "__main__":
    unittest.main()
