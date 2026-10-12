#!/usr/bin/env python3
"""Synthetic STRUCTURAL tests only — not the sealed independent SE11 truth corpus."""
import copy
import hashlib
import hmac
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

BASE = pathlib.Path(__file__).resolve().parent
RUNNER = BASE / "commit_hidden.py"
ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
BALANCE = {"TRUE": 8, "MATERIALLY_FALSE": 4, "OVERBROAD": 4, "NEAR_MISS": 4}


def derived_id(secret_hex, nonce):
    digest = bytearray(hmac.new(bytes.fromhex(secret_hex), nonce.encode("utf-8"), hashlib.sha256).digest()[:16])
    digest[6] = (digest[6] & 0x0F) | 0x40
    digest[8] = (digest[8] & 0x3F) | 0x80
    return "H_" + bytes(digest).hex()


def fake_hidden():
    secret = "ab" * 32
    mappings = {
        "FFmpeg": {
            "execution_target_ref": "TEST_ONLY_FFMPEG_TARGET",
            "relation": "SAME",
            "applicability_review_sha256": "1" * 64,
            "applicability_review_status": "PASS",
            "approved_applicability_evidence": []
        },
        "pandas": {
            "execution_target_ref": "TEST_ONLY_PANDAS_TARGET",
            "relation": "SAME",
            "applicability_review_sha256": "2" * 64,
            "applicability_review_status": "PASS",
            "approved_applicability_evidence": []
        },
        "MinIO": {
            "execution_target_ref": "TEST_ONLY_MINIO_TARGET",
            "relation": "SAME",
            "applicability_review_sha256": "3" * 64,
            "applicability_review_status": "PASS",
            "approved_applicability_evidence": []
        },
        "LibreOffice": {
            "execution_target_ref": "TEST_ONLY_LIBREOFFICE_RELEASE_TARGET",
            "relation": "DIVERGED",
            "applicability_review_sha256": "4" * 64,
            "applicability_review_status": "PASS",
            "approved_applicability_evidence": []
        }
    }
    records = []
    index = 1
    for asset in ASSETS:
        for category, count in BALANCE.items():
            for _ in range(count):
                nonce = f"TEST_NONCE_{index:04d}"
                relation = mappings[asset]["relation"]
                evidence_kind = "RELEASE_SPECIFIC_SOURCE" if relation == "DIVERGED" else "EXACT_SOURCE_IDENTITY"
                evidence_sha = f"{index:064x}"
                mappings[asset]["approved_applicability_evidence"].append({
                    "evidence_kind": evidence_kind,
                    "evidence_sha256": evidence_sha
                })
                records.append({
                    "id": derived_id(secret, nonce),
                    "id_nonce": nonce,
                    "asset": asset,
                    "truth_class": category,
                    "claim_text": "TEST_ONLY_SYNTHETIC_SECRET",
                    "binding_id": "TEST_ONLY_SYNTHETIC_BINDING",
                    "decisive_fixture_ref": "TEST_ONLY_SYNTHETIC_FIXTURE",
                    "expected_behavior": "TEST_ONLY_SYNTHETIC",
                    "provenance": "TEST_ONLY_SYNTHETIC",
                    "reset_requirements": "TEST_ONLY_SYNTHETIC",
                    "target_applicability": {
                        "mapping_relation": relation,
                        "evidence_kind": evidence_kind,
                        "evidence_sha256": evidence_sha,
                        "independent_review_status": "PASS"
                    }
                })
                index += 1
    return {
        "schema_version": "se11-hidden-v1",
        "stage_a_merge": "0279968580d50e51843b09aa2b6e266b9967ff93",
        "execution_target_manifest_sha256": "AUTO",
        "source_execution_mapping_frozen": True,
        "source_execution_mappings": mappings,
        "id_scheme": "HMAC_SHA256_UUIDV4_V1",
        "id_secret_hex": secret,
        "truth_visible_to_llm_b": False,
        "decisive_fixtures_visible_to_llm_b": False,
        "curator_isolation_declaration": "TEST_ONLY_SYNTHETIC_NO_REAL_HIDDEN_TRUTH",
        "claims": records
    }

def write_manifest_and_bind(doc, path, mutator=None):
    manifest = {
        "schema_version": "se11-execution-target-manifest-v1",
        "source_execution_mappings": copy.deepcopy(doc["source_execution_mappings"])
    }
    if mutator is not None:
        mutator(manifest)
    raw = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(raw)
    if doc["execution_target_manifest_sha256"] == "AUTO":
        doc["execution_target_manifest_sha256"] = hashlib.sha256(raw).hexdigest()
    return raw


class HiddenToolTests(unittest.TestCase):
    def check_case(self, doc, success, manifest_mutator=None):
        with tempfile.TemporaryDirectory(prefix="se11-tool-unit-test-") as td:
            td = pathlib.Path(td)
            inp = td / "private.json"
            out = td / "public.json"
            manifest = td / "target-manifest.json"
            write_manifest_and_bind(doc, manifest, manifest_mutator)
            inp.write_text(json.dumps(doc), encoding="utf-8")
            cp = subprocess.run(
                [sys.executable, str(RUNNER), str(inp),
                 "--execution-target-manifest", str(manifest),
                 "--out", str(out)],
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
                self.assertEqual(obj["execution_target_manifest_sha256"], hashlib.sha256(manifest.read_bytes()).hexdigest())
                self.assertEqual(obj["id_scheme"], "HMAC_SHA256_UUIDV4_V1")
                self.assertEqual(obj["source_execution_relations"]["LibreOffice"], "DIVERGED")
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
        d["claims"][0].pop("target_applicability")
        self.check_case(d, False)

    def test_placeholder_applicability_hash_rejected(self):
        d = fake_hidden()
        d["claims"][0]["target_applicability"]["evidence_sha256"] = "x"
        self.check_case(d, False)

    def test_unapproved_well_formed_applicability_hash_rejected(self):
        d = fake_hidden()
        d["claims"][0]["target_applicability"]["evidence_sha256"] = "f" * 64
        self.check_case(d, False)

    def test_diverged_exact_source_evidence_rejected(self):
        d = fake_hidden()
        lo = next(c for c in d["claims"] if c["asset"] == "LibreOffice")
        lo["target_applicability"]["evidence_kind"] = "EXACT_SOURCE_IDENTITY"
        self.check_case(d, False)

    def test_mapping_relation_mismatch_rejected(self):
        d = fake_hidden()
        d["claims"][0]["target_applicability"]["mapping_relation"] = "DIVERGED"
        self.check_case(d, False)

    def test_predictable_uuid_shape_without_hmac_binding_rejected(self):
        d = fake_hidden()
        d["claims"][0]["id"] = "H_00000000000040008000000000000001"
        self.check_case(d, False)

    def test_manifest_mapping_mismatch_rejected(self):
        d = fake_hidden()
        def mutate(manifest):
            manifest["source_execution_mappings"]["LibreOffice"]["execution_target_ref"] = "ALTERED_TARGET"
        self.check_case(d, False, mutate)

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
        with tempfile.TemporaryDirectory(prefix="se11-strict-json-") as td:
            td = pathlib.Path(td)
            inp = td / "private.json"
            out = td / "public.json"
            manifest = td / "target-manifest.json"
            doc = fake_hidden()
            write_manifest_and_bind(doc, manifest)
            raw = json.dumps(doc).replace(
                '"schema_version":', '"schema_version": "shadow", "schema_version":', 1
            )
            inp.write_text(raw, encoding="utf-8")
            cp = subprocess.run(
                [sys.executable, str(RUNNER), str(inp),
                 "--execution-target-manifest", str(manifest),
                 "--out", str(out)],
                capture_output=True, text=True, check=False
            )
            self.assertNotEqual(cp.returncode, 0)
            self.assertFalse(out.exists())
            self.assertIn("duplicate JSON key", cp.stderr)

    def test_rejects_nonfinite_json_constants(self):
        with tempfile.TemporaryDirectory(prefix="se11-strict-json-") as td:
            td = pathlib.Path(td)
            inp = td / "private.json"
            out = td / "public.json"
            manifest = td / "target-manifest.json"
            doc = fake_hidden()
            write_manifest_and_bind(doc, manifest)
            raw = json.dumps(doc).replace(
                '"schema_version":', '"injected": NaN, "schema_version":', 1
            )
            inp.write_text(raw, encoding="utf-8")
            cp = subprocess.run(
                [sys.executable, str(RUNNER), str(inp),
                 "--execution-target-manifest", str(manifest),
                 "--out", str(out)],
                capture_output=True, text=True, check=False
            )
            self.assertNotEqual(cp.returncode, 0)
            self.assertFalse(out.exists())
            self.assertIn("unsupported JSON constant", cp.stderr)

    def test_source_same_as_output(self):
        with tempfile.TemporaryDirectory(prefix="se11-tool-unit-test-") as td:
            td = pathlib.Path(td)
            inp = td / "private.json"
            manifest = td / "target-manifest.json"
            doc = fake_hidden()
            write_manifest_and_bind(doc, manifest)
            inp.write_text(json.dumps(doc), encoding="utf-8")
            cp = subprocess.run(
                [sys.executable, str(RUNNER), str(inp),
                 "--execution-target-manifest", str(manifest),
                 "--out", str(inp)],
                capture_output=True, text=True, check=False
            )
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("overwrite private", cp.stderr)


if __name__ == "__main__":
    unittest.main()
