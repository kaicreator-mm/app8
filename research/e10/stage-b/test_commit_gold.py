#!/usr/bin/env python3
"""Test-only synthetic fixtures. NEVER use these as independent human SE10 gold."""
import copy
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

BASE = pathlib.Path(__file__).resolve().parent
RUNNER = BASE / "commit_gold.py"
SOURCE = json.loads((BASE / "source_anchor_allowlist.json").read_text(encoding="utf-8"))


def fake_gold():
    cases = []
    index = 1
    for asset, paths in SOURCE["assets"].items():
        path, blob = next(iter(paths.items()))
        for _ in range(12):
            cases.append({
                "id": f"G{index:04d}",
                "asset": asset,
                "canonical_identity": "TEST_ONLY_SYNTHETIC",
                "purpose": "TEST_ONLY_SYNTHETIC_CANARY_SECRET",
                "source_anchors": [{"path": path, "blob": blob}],
                "variants": [], "constraints": [], "negative_boundaries": [],
                "failure_semantics": [],
                "binding_equivalence_group": None, "ambiguity": False
            })
            index += 1
    return {
        "schema_version": "se10-gold-v1",
        "source_pack_blob": SOURCE["source_pack_blob"],
        "model_generated_gold": False,  # structural validator test; not a real authorship claim
        "predictor_gold_visibility": False,
        "human_author_declaration": "TEST_ONLY_SYNTHETIC_NOT_REAL_GOLD",
        "capabilities": cases
    }


class GoldToolTests(unittest.TestCase):
    def execute(self, doc, expected_success):
        with tempfile.TemporaryDirectory(prefix="se10-tool-unit-test-") as tmp:
            private = pathlib.Path(tmp) / "private.json"
            output = pathlib.Path(tmp) / "public.json"
            private.write_text(json.dumps(doc), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(RUNNER), str(private), "--out", str(output)],
                text=True, capture_output=True, check=False
            )
            self.assertEqual(proc.returncode == 0, expected_success, proc.stderr)
            if expected_success:
                public = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(public["capability_count"], 48)
                self.assertEqual(public["gold_file_sha256"], hashlib.sha256(private.read_bytes()).hexdigest())
                self.assertNotIn("CANARY_SECRET", output.read_text(encoding="utf-8"))
                self.assertEqual(len(public["opaque_reference_ids"]), 48)
            else:
                self.assertFalse(output.exists(), "failed validation must not emit commitment")

    def test_accepts_structural_fixture_not_semantic_gold(self):
        self.execute(fake_gold(), True)

    def test_rejects_semantic_ids(self):
        d = fake_gold()
        d["capabilities"][0]["id"] = "video-trimming"
        self.execute(d, False)

    def test_rejects_forged_source_anchor(self):
        d = fake_gold()
        d["capabilities"][0]["source_anchors"][0]["blob"] = "0" * 40
        self.execute(d, False)

    def test_rejects_invalid_field_types(self):
        d = fake_gold()
        d["capabilities"][0]["constraints"] = "not-a-list"
        self.execute(d, False)

    def test_rejects_duplicate_ids(self):
        d = fake_gold()
        d["capabilities"][0]["id"] = d["capabilities"][1]["id"]
        self.execute(d, False)

    def test_rejects_underfilled_asset(self):
        d = fake_gold()
        d["capabilities"].pop(0)
        self.execute(d, False)

    def test_rejects_blank_human_declaration(self):
        d = fake_gold()
        d["human_author_declaration"] = " "
        self.execute(d, False)

    def test_rejects_extra_fields(self):
        d = fake_gold()
        d["capabilities"][0]["gold_leak"] = "CANARY_SECRET"
        self.execute(d, False)

    def test_rejects_same_input_output_file(self):
        with tempfile.TemporaryDirectory(prefix="se10-tool-unit-test-") as tmp:
            private = pathlib.Path(tmp) / "private.json"
            private.write_text(json.dumps(fake_gold()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(RUNNER), str(private), "--out", str(private)],
                capture_output=True, text=True, check=False
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("private gold", proc.stderr)
            self.assertTrue(private.exists())


if __name__ == "__main__":
    unittest.main()
