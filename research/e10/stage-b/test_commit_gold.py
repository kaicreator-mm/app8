#!/usr/bin/env python3
"""Test-only synthetic fixtures. NEVER use these as independent human SE10 gold."""
import copy
import hashlib
import json
import os
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
                "binding_equivalence_group": None, "duplicate_identity_disposition": "UNIQUE", "ambiguity": False
            })
            index += 1
    return {
        "schema_version": "se10-gold-v1",
        "source_pack_blob": SOURCE["source_pack_blob"],
        "model_generated_gold": False,  # structural validator test; not a real authorship claim
        "predictor_gold_visibility": False,
        "human_author_declaration": "I attest that this semantic Gold was authored by an independent human without model-generated Gold.",
        "human_author_identity_class": "INDEPENDENT_HUMAN_DOMAIN_CURATOR",
        "human_reviewer_identity_class": "INDEPENDENT_HUMAN_GOLD_REVIEWER",
        "independence_declaration": "INDEPENDENT_HUMANS_NO_MODEL_GOLD_NO_PREDICTOR_ACCESS",
        "isolation_statement": "TEST_ONLY_SYNTHETIC_ISOLATION_DECLARATION",
        "adjudication_procedure_sha256": "1" * 64,
        "adjudication_code_sha256": "2" * 64,
        "private_store_class": "SEALED_ACCESS_CONTROLLED_OUTSIDE_DISCOVERABLE_GIT",
        "private_store_independent_reviewed": True,
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
                self.assertEqual(public["allowlist_git_blob"], "5be0ed7674fcdfd7361a57fd4f29a6f9655c1df1")
                self.assertEqual(public["human_author_identity_class"], "INDEPENDENT_HUMAN_DOMAIN_CURATOR")
                self.assertEqual(public["human_reviewer_identity_class"], "INDEPENDENT_HUMAN_GOLD_REVIEWER")
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

    def test_rejects_contradictory_human_declaration(self):
        d = fake_gold()
        d["human_author_declaration"] = "LLM_GENERATED_NOT_HUMAN"
        self.execute(d, False)

    def test_rejects_missing_duplicate_identity_disposition(self):
        d = fake_gold()
        d["capabilities"][0].pop("duplicate_identity_disposition")
        self.execute(d, False)

    def test_rejects_invalid_equivalence_disposition(self):
        d = fake_gold()
        d["capabilities"][0]["duplicate_identity_disposition"] = "EQUIVALENT_GROUP_MEMBER"
        d["capabilities"][0]["binding_equivalence_group"] = None
        self.execute(d, False)

    def test_rejects_extra_fields(self):
        d = fake_gold()
        d["capabilities"][0]["gold_leak"] = "CANARY_SECRET"
        self.execute(d, False)

    def test_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory(prefix="se10-strict-json-") as td:
            inp = pathlib.Path(td) / "private.json"
            out = pathlib.Path(td) / "public.json"
            doc = fake_gold()
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
        with tempfile.TemporaryDirectory(prefix="se10-strict-json-") as td:
            inp = pathlib.Path(td) / "private.json"
            out = pathlib.Path(td) / "public.json"
            doc = fake_gold()
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

    def test_rejects_hardlink_output_alias(self):
        with tempfile.TemporaryDirectory(prefix="se10-hardlink-") as tmp:
            private = pathlib.Path(tmp) / "private.json"
            output = pathlib.Path(tmp) / "public.json"
            private.write_text(json.dumps(fake_gold()), encoding="utf-8")
            try:
                os.link(private, output)
            except OSError as exc:
                self.skipTest(f"hardlink unsupported: {exc}")
            proc = subprocess.run(
                [sys.executable, str(RUNNER), str(private), "--out", str(output)],
                capture_output=True, text=True, check=False
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("inode/file identity", proc.stderr)
            self.assertIn("TEST_ONLY_SYNTHETIC_CANARY_SECRET", private.read_text(encoding="utf-8"))

    def test_rejects_tampered_runtime_allowlist(self):
        with tempfile.TemporaryDirectory(prefix="se10-allowlist-") as tmp:
            td = pathlib.Path(tmp)
            runner = td / "commit_gold.py"
            allowlist = td / "source_anchor_allowlist.json"
            runner.write_text(RUNNER.read_text(encoding="utf-8"), encoding="utf-8")
            altered = copy.deepcopy(SOURCE)
            altered["assets"]["FFmpeg"]["README.md"] = "0" * 40
            allowlist.write_text(json.dumps(altered, indent=2) + "\n", encoding="utf-8")
            private = td / "private.json"
            output = td / "public.json"
            private.write_text(json.dumps(fake_gold()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(runner), str(private), "--out", str(output)],
                capture_output=True, text=True, check=False
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(output.exists())
            self.assertIn("reviewed Git blob", proc.stderr)

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
