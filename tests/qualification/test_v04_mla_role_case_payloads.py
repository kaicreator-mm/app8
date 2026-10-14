"""Synthetic typed per-case MLA role payload validation."""
import hashlib
import json
import unittest

from app8.mla.blind_capture import VIS
from scripts.v04_mla_role_case_payloads import validate_role_case_payloads, KINDS
from scripts.v04_mla_pilot_reducer import ALLOWLIST, ROOT, SOURCE_BLOB, PilotBlocked


def sha(x):
    return hashlib.sha256(x).hexdigest()


def fixture():
    anchors = json.loads((ROOT / ALLOWLIST).read_text(encoding="utf-8"))["assets"]
    cases, captures = [], {}
    for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice"):
        ctx = sha(asset.encode())
        path, blob = sorted(anchors[asset].items())[0]
        case_slots = [{"case_id": f"V04-{asset.upper()}-{i:03d}",
                       "source_anchor": {"path": path, "blob": blob}}
                      for i in range(1, 7)]
        freeze = {
            "schema_version": "v04-mla-blind-freeze-v1",
            "study_id": "V04-MLA-1",
            "source_pack_git_blob": SOURCE_BLOB,
            "frozen_before_first_response": True,
            "source_context_sha256": ctx,
            "roles": {},
        }
        inputs, outputs = {}, {}
        for role in ("P", "R", "X"):
            entry = {
                "source_pack_git_blob": SOURCE_BLOB,
                "source_context_sha256": ctx,
                "task_instruction_sha256": sha((role + ":" + asset).encode()),
                "visibility_scope": VIS[role],
            }
            inputs[role] = (json.dumps(entry, sort_keys=True) + "\n").encode()
            batch = {
                "schema_version": "v04-mla-role-batch-v1",
                "study_id": "V04-MLA-1",
                "asset": asset,
                "role": role,
                "source_context_sha256": ctx,
                "cases": [
                    {"case_id": s["case_id"],
                     "source_anchor": s["source_anchor"],
                     "origin": "LLM_PROPOSED",
                     "kind": KINDS[role],
                     "proposal": f"Fixture-only {role} unverified hypothesis {s['case_id']}",
                     "constraints": ["synthetic only"]}
                    for s in case_slots
                ],
            }
            outputs[role] = (json.dumps(batch, sort_keys=True) + "\n").encode()
            freeze["roles"][role] = {
                "model_family": f"test-family-{role}",
                "provider": "synthetic",
                "model_version": "fixture-only",
                "prompt_sha256": sha((role + asset + "prompt").encode()),
                "sampling_sha256": sha((role + asset + "sampling").encode()),
                "input_sha256": sha(inputs[role]),
            }
        captures[asset] = {"freeze": freeze, "inputs": inputs, "outputs": outputs}
        for s in case_slots:
            cases.append({
                "case_id": s["case_id"],
                "asset": asset,
                "source_anchor": s["source_anchor"],
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
        "human_selection_seed_sha256": "9" * 64,
        "cases": cases,
    }
    return pilot, captures


def change_batch(captures, asset, role, f):
    value = json.loads(captures[asset]["outputs"][role])
    f(value)
    captures[asset]["outputs"][role] = (json.dumps(value, sort_keys=True) + "\n").encode()
    # Update public transcript hashes so only new payload constraint fails.
    return sha(captures[asset]["outputs"][role])


class TypedRoleCandidateTests(unittest.TestCase):
    def test_24_cases_each_p_r_x_and_no_truth(self):
        p, c = fixture()
        r = validate_role_case_payloads(p, c)
        self.assertEqual(r["case_denominator"], 24)
        self.assertEqual(r["asset_count"], 4)
        self.assertEqual(r["role_count"], 3)
        self.assertEqual(len(r["role_case_payloads"]["MinIO"]["X"]["case_payload_sha256"]), 6)
        self.assertFalse(r["provider_transport_and_time_freeze_verified"])
        self.assertFalse(r["capability_promotion_allowed"])

    def test_missing_case_rejected(self):
        p, c = fixture()
        digest = change_batch(c, "FFmpeg", "P", lambda d: d["cases"].pop())
        for x in p["cases"][:6]:
            x["model_prediction_sha256"] = digest
        with self.assertRaisesRegex(PilotBlocked, "six nonreplaceable"):
            validate_role_case_payloads(p, c)

    def test_duplicate_case_rejected(self):
        p, c = fixture()
        def duplicate(d):
            d["cases"][0] = dict(d["cases"][1])
        digest = change_batch(c, "pandas", "R", duplicate)
        for x in p["cases"][6:12]:
            x["reference_proposer_sha256"] = digest
        with self.assertRaisesRegex(PilotBlocked, "duplicate"):
            validate_role_case_payloads(p, c)

    def test_hidden_truth_key_rejected(self):
        p, c = fixture()
        def hidden(d):
            d["cases"][0]["hidden_truth"] = "true"
        digest = change_batch(c, "MinIO", "X", hidden)
        for x in p["cases"][12:18]:
            x["adversarial_challenger_sha256"] = digest
        with self.assertRaisesRegex(PilotBlocked, "private truth fields"):
            validate_role_case_payloads(p, c)

    def test_swapped_source_anchor_rejected(self):
        p, c = fixture()
        def swap(d):
            d["cases"][0]["source_anchor"]["path"] = "non-pinned"
        digest = change_batch(c, "LibreOffice", "P", swap)
        for x in p["cases"][18:24]:
            x["model_prediction_sha256"] = digest
        with self.assertRaisesRegex(PilotBlocked, "source/role"):
            validate_role_case_payloads(p, c)

    def test_swapped_role_marker_rejected(self):
        p, c = fixture()
        def swap(d):
            d["role"] = "X"
        digest = change_batch(c, "FFmpeg", "P", swap)
        for x in p["cases"][:6]:
            x["model_prediction_sha256"] = digest
        with self.assertRaisesRegex(PilotBlocked, "wrong role"):
            validate_role_case_payloads(p, c)

    def test_cross_asset_marker_rejected(self):
        p, c = fixture()
        def swap(d):
            d["asset"] = "pandas"
        digest = change_batch(c, "FFmpeg", "R", swap)
        for x in p["cases"][:6]:
            x["reference_proposer_sha256"] = digest
        with self.assertRaisesRegex(PilotBlocked, "wrong role"):
            validate_role_case_payloads(p, c)

    def test_bad_origin_rejected(self):
        p, c = fixture()
        def fake(d):
            d["cases"][0]["origin"] = "INDEPENDENT_HUMAN_GOLD"
        digest = change_batch(c, "pandas", "X", fake)
        for x in p["cases"][6:12]:
            x["adversarial_challenger_sha256"] = digest
        with self.assertRaisesRegex(PilotBlocked, "source/role"):
            validate_role_case_payloads(p, c)

    def test_non_json_rejected(self):
        p, c = fixture()
        c["LibreOffice"]["outputs"]["X"] = b"not json"
        digest = sha(c["LibreOffice"]["outputs"]["X"])
        for x in p["cases"][18:24]:
            x["adversarial_challenger_sha256"] = digest
        with self.assertRaisesRegex(PilotBlocked, "invalid P/R/X typed case JSON"):
            validate_role_case_payloads(p, c)

    def test_empty_proposal_rejected(self):
        p, c = fixture()
        def empty(d):
            d["cases"][0]["proposal"] = " "
        digest = change_batch(c, "FFmpeg", "X", empty)
        for x in p["cases"][:6]:
            x["adversarial_challenger_sha256"] = digest
        with self.assertRaisesRegex(PilotBlocked, "missing or oversized"):
            validate_role_case_payloads(p, c)


if __name__ == "__main__":
    unittest.main()
