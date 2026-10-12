#!/usr/bin/env python3
"""Synthetic STRUCTURAL tests only — not the sealed independent SE11 truth corpus."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import uuid

BASE = pathlib.Path(__file__).resolve().parent
RUNNER = BASE / "commit_hidden.py"
ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
BALANCE = {"TRUE": 8, "MATERIALLY_FALSE": 4, "OVERBROAD": 4, "NEAR_MISS": 4}


def fake_hidden():
    records = []
    index = 1
    for asset in ASSETS:
        for category, count in BALANCE.items():
            for _ in range(count):
                records.append({
                    "id": "H_" + uuid.uuid4().hex,
                    "asset": asset,
                    "truth_class": category,
                    "claim_text": "TEST_ONLY_SYNTHETIC_SECRET",
                    "binding_id": "TEST_ONLY_SYNTHETIC_BINDING",
                    "decisive_fixture_ref": "TEST_ONLY_SYNTHETIC_FIXTURE",
                    "expected_behavior": "TEST_ONLY_SYNTHETIC",
                    "provenance": "TEST_ONLY_SYNTHETIC",
                    "reset_requirements": "TEST_ONLY_SYNTHETIC",
                    "target_applicability_evidence_ref": "TEST_ONLY_SYNTHETIC"
                })
                index += 1
    return {
        "schema_version": "se11-hidden-v1",
        "stage_a_merge": "0279968580d50e51843b09aa2b6e266b9967ff93",
        "execution_target_manifest_sha256": "a" * 64,
        "source_execution_mapping_frozen": True,
        "truth_visible_to_llm_b": False,
        "decisive_fixtures_visible_to_llm_b": False,
        "curator_isolation_declaration": "TEST_ONLY_SYNTHETIC_NO_REAL_HIDDEN_TRUTH",
        "claims": records
    }


class HiddenToolTests(unittest.TestCase):
    def check_case(self, doc, success):
        with tempfile.TemporaryDirectory(prefix="se11-tool-unit-test-") as td:
            inp = pathlib.Path(td) / "private.json"
            out = pathlib.Path(td) / "public.json"
            inp.write_text(json.dumps(doc), encoding="utf-8")
            cp = subprocess.run(
                [sys.executable, str(RUNNER), str(inp), "--out", str(out)],
                text=True, capture_output=True, check=False
            )
            self.assertEqual(cp.returncode == 0, success, cp.stderr)
            if success:
                output = out.read_text(encoding="utf-8")
                obj = json.loads(output)
                self.assertNotIn("SYNTHETIC_SECRET", output)
                self.assertNotIn("SYNTHETIC_FIXTURE", output)
                self.assertEqual(obj["claim_count"], 80)
                self.assertEqual(obj["hidden_file_sha256"], hashlib.sha256(inp.read_bytes()).hexdigest())
                self.assertEqual(obj["execution_target_manifest_sha256"], "a" * 64)
            else:
                self.assertFalse(out.exists(), "invalid corpus must not yield a public commitment")

    def test_valid_structural_fixture_only(self):
        self.check_case(fake_hidden(), True)

    def test_wrong_truth_balance(self):
        d = fake_hidden()
        d["claims"][0]["truth_class"] = "NEAR_MISS"
        self.check_case(d, False)

    def test_duplicate_id(self):
        d = fake_hidden()
        d["claims"][0]["id"] = d["claims"][1]["id"]
        self.check_case(d, False)

    def test_semantic_id(self):
        d = fake_hidden()
        d["claims"][0]["id"] = "false-claim"
        self.check_case(d, False)

    def test_missing_applicability(self):
        d = fake_hidden()
        d["claims"][0].pop("target_applicability_evidence_ref")
        self.check_case(d, False)

    def test_blank_applicability(self):
        d = fake_hidden()
        d["claims"][0]["target_applicability_evidence_ref"] = "  "
        self.check_case(d, False)

    def test_wrong_manifest_hash(self):
        d = fake_hidden()
        d["execution_target_manifest_sha256"] = "z" * 64
        self.check_case(d, False)

    def test_visible_truth(self):
        d = fake_hidden()
        d["truth_visible_to_llm_b"] = True
        self.check_case(d, False)

    def test_extra_fields(self):
        d = fake_hidden()
        d["claims"][0]["label_leak"] = "SYNTHETIC_SECRET"
        self.check_case(d, False)

    def test_underfilled(self):
        d = fake_hidden()
        d["claims"].pop()
        self.check_case(d, False)

    def test_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory(prefix="e11-strict-json-") as td:
            inp = pathlib.Path(td) / "private.json"
            out = pathlib.Path(td) / "public.json"
            doc = fake_hidden()
            raw = json.dumps(doc).replace(
                '"schema_version":', '"schema_version": "shadow", "schema_version":', 1
            )
            inp.write_text(raw, encoding="utf-8")
            cp = subprocess.run(
                [sys.executable, str(RUNNER), str(inp), "--out", str(out)],
                capture_output=True, text=True, check=False
            )
            self.assertNotEqual(cp.returncode, 0)
            self.assertFalse(out.exists())
            self.assertIn("duplicate JSON key", cp.stderr)

    def test_rejects_nonfinite_json_constants(self):
        with tempfile.TemporaryDirectory(prefix="e11-strict-json-") as td:
            inp = pathlib.Path(td) / "private.json"
            out = pathlib.Path(td) / "public.json"
            doc = fake_hidden()
            raw = json.dumps(doc).replace(
                '"schema_version":', '"injected": NaN, "schema_version":', 1
            )
            inp.write_text(raw, encoding="utf-8")
            cp = subprocess.run(
                [sys.executable, str(RUNNER), str(inp), "--out", str(out)],
                capture_output=True, text=True, check=False
            )
            self.assertNotEqual(cp.returncode, 0)
            self.assertFalse(out.exists())
            self.assertIn("unsupported JSON constant", cp.stderr)

    def test_source_same_as_output(self):
        with tempfile.TemporaryDirectory(prefix="se11-tool-unit-test-") as td:
            inp = pathlib.Path(td) / "private.json"
            inp.write_text(json.dumps(fake_hidden()), encoding="utf-8")
            cp = subprocess.run(
                [sys.executable, str(RUNNER), str(inp), "--out", str(inp)],
                capture_output=True, text=True, check=False
            )
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("overwrite private", cp.stderr)


if __name__ == "__main__":
    unittest.main()
