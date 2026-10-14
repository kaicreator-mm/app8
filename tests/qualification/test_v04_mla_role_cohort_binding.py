"""Synthetic four-asset transcript binding tests. No provider invocations."""
import hashlib
import json
import unittest

from scripts.v04_mla_role_cohort_binding import bind_role_cohort
from scripts.v04_mla_pilot_reducer import ALLOWLIST, ROOT, SOURCE_BLOB, PilotBlocked


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fixtures():
    from app8.mla.blind_capture import VIS
    anchors = json.loads((ROOT / ALLOWLIST).read_text(encoding="utf-8"))["assets"]
    cases, captures = [], {}
    for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice"):
        ctx_sha = sha(asset.encode())
        freeze = {
            "schema_version": "v04-mla-blind-freeze-v1",
            "study_id": "V04-MLA-1",
            "source_pack_git_blob": SOURCE_BLOB,
            "frozen_before_first_response": True,
            "source_context_sha256": ctx_sha,
            "roles": {},
        }
        inputs, outputs = {}, {}
        for role in ("P", "R", "X"):
            envelope = {
                "source_pack_git_blob": SOURCE_BLOB,
                "source_context_sha256": ctx_sha,
                "task_instruction_sha256": sha((role + ":" + asset).encode()),
                "visibility_scope": VIS[role],
            }
            inputs[role] = (json.dumps(envelope, sort_keys=True) + "\n").encode()
            outputs[role] = ("synthetic:" + asset + ":" + role).encode()
            freeze["roles"][role] = {
                "model_family": "family-" + role,
                "provider": "fixture-provider",
                "model_version": "synthetic-1",
                "prompt_sha256": sha(("prompt:" + asset + ":" + role).encode()),
                "sampling_sha256": sha(("sampling:" + asset + ":" + role).encode()),
                "input_sha256": sha(inputs[role]),
            }
        captures[asset] = {"freeze": freeze, "inputs": inputs, "outputs": outputs}
        path, blob = sorted(anchors[asset].items())[0]
        for i in range(6):
            cases.append({
                "case_id": "V04-" + asset.upper() + "-" + str(i + 1).zfill(3),
                "asset": asset,
                "source_anchor": {"path": path, "blob": blob},
                "model_prediction_sha256": sha(outputs["P"]),
                "reference_proposer_sha256": sha(outputs["R"]),
                "adversarial_challenger_sha256": sha(outputs["X"]),
                "source_verification_claim": "CANDIDATE_ONLY",
                "behavior_observation_sha256": None,
                "high_impact_unresolved": False,
                "oracle_visible_to_predictor": False,
                "model_consensus": False,
            })
    pilot = {
        "schema_version": "v04-mla-pilot-public-v1",
        "study_id": "V04-MLA-1",
        "source_pack_git_blob": SOURCE_BLOB,
        "reference_origin": "LLM_PROPOSED",
        "frozen_before_model_outputs": True,
        "human_selection_seed_sha256": sha(b"precommitted-sample-seed"),
        "cases": cases,
    }
    return pilot, captures


class CohortTranscriptBindingTests(unittest.TestCase):
    def test_24_cases_bound_to_four_asset_batches(self):
        result = bind_role_cohort(*fixtures())
        self.assertEqual(result["case_denominator"], 24)
        self.assertEqual(result["status"], "STRUCTURAL_BOUND_NOT_EXECUTION_PROOF")
        self.assertEqual(set(result["assets"]), {"FFmpeg", "pandas", "MinIO", "LibreOffice"})
        self.assertFalse(result["trusted_provider_invocation_proven"])
        self.assertFalse(result["empirical_qualification_pass"])

    def test_swapped_asset_transcript_rejected(self):
        pilot, captures = fixtures()
        captures["FFmpeg"]["outputs"]["R"] = captures["pandas"]["outputs"]["R"]
        with self.assertRaisesRegex(PilotBlocked, "digest differs"):
            bind_role_cohort(pilot, captures)

    def test_swapped_case_transcript_rejected(self):
        pilot, captures = fixtures()
        pilot["cases"][0]["model_prediction_sha256"] = "a" * 64
        with self.assertRaisesRegex(PilotBlocked, "digest differs"):
            bind_role_cohort(pilot, captures)

    def test_missing_asset_rejected(self):
        pilot, captures = fixtures()
        captures.pop("MinIO")
        with self.assertRaisesRegex(PilotBlocked, "exactly four"):
            bind_role_cohort(pilot, captures)

    def test_reused_context_between_assets_rejected(self):
        pilot, captures = fixtures()
        other = captures["FFmpeg"]["freeze"]["source_context_sha256"]
        for role in ("P", "R", "X"):
            raw = json.loads(captures["MinIO"]["inputs"][role])
            raw["source_context_sha256"] = other
            captures["MinIO"]["inputs"][role] = (json.dumps(raw, sort_keys=True) + "\n").encode()
            captures["MinIO"]["freeze"]["roles"][role]["input_sha256"] = sha(
                captures["MinIO"]["inputs"][role])
        captures["MinIO"]["freeze"]["source_context_sha256"] = other
        with self.assertRaisesRegex(PilotBlocked, "cannot be reused"):
            bind_role_cohort(pilot, captures)

    def test_hidden_truth_field_rejected(self):
        pilot, captures = fixtures()
        raw = json.loads(captures["FFmpeg"]["inputs"]["P"])
        raw["hidden_truth"] = "yes"
        captures["FFmpeg"]["inputs"]["P"] = (json.dumps(raw, sort_keys=True) + "\n").encode()
        captures["FFmpeg"]["freeze"]["roles"]["P"]["input_sha256"] = sha(
            captures["FFmpeg"]["inputs"]["P"])
        with self.assertRaisesRegex(PilotBlocked, "invalid P/R/X"):
            bind_role_cohort(pilot, captures)

    def test_correlated_model_family_is_provisional(self):
        pilot, captures = fixtures()
        captures["MinIO"]["freeze"]["roles"]["X"]["model_family"] = "family-R"
        result = bind_role_cohort(pilot, captures)
        self.assertEqual(result["status"], "PROVISIONAL_CORRELATED_MODEL_FAMILY")
        self.assertFalse(result["formal_product_release_qualified"])

    def test_role_swap_fails(self):
        pilot, captures = fixtures()
        c = captures["LibreOffice"]
        c["inputs"]["P"], c["inputs"]["X"] = c["inputs"]["X"], c["inputs"]["P"]
        with self.assertRaises(PilotBlocked):
            bind_role_cohort(pilot, captures)

    def test_extra_private_fields_fail(self):
        pilot, captures = fixtures()
        captures["FFmpeg"]["truth"] = "private"
        with self.assertRaisesRegex(PilotBlocked, "incomplete"):
            bind_role_cohort(pilot, captures)

    def test_duplicate_case_rejected(self):
        pilot, captures = fixtures()
        pilot["cases"][0]["case_id"] = pilot["cases"][1]["case_id"]
        with self.assertRaises(PilotBlocked):
            bind_role_cohort(pilot, captures)


if __name__ == "__main__":
    unittest.main()
