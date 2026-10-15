"""No network, no LLM: P candidate must pass real app8 hypothesis compiler."""
import copy
import hashlib
import json
import unittest

from scripts.v04_mla_pilot_reducer import ROOT, ALLOWLIST, PilotBlocked
from scripts.v04_mla_app8_p_ingress import ingest_p_batch_via_app8


def fixture():
    selected = json.loads((ROOT / ALLOWLIST).read_text(encoding="utf-8"))
    anchor_paths = sorted(selected["assets"]["FFmpeg"].items())[:6]
    slots = [
        {"case_id": f"V04-FFMPEG-{i:03d}", "source_anchor": {"path": p, "blob": b}}
        for i, (p, b) in enumerate(anchor_paths, 1)
    ]
    context = b"fixture verified context, NOT real upstream source"
    source_hash = hashlib.sha256(context).hexdigest()
    doc = {
        "schema_version": "v04-mla-role-batch-v1",
        "study_id": "V04-MLA-1",
        "asset": "FFmpeg", "role": "P",
        "source_context_sha256": source_hash,
        "cases": [
            {"case_id": row["case_id"], "source_anchor": row["source_anchor"],
             "origin": "LLM_PROPOSED", "kind": "P_CAPABILITY_PREDICTION",
             "proposal": "Synthetic hypothesis " + row["case_id"],
             "constraints": ["no observed behavior"]}
            for row in slots
        ],
    }
    return slots, context, source_hash, doc


def run(slots, context, sha, doc):
    raw = (json.dumps(doc, sort_keys=True, ensure_ascii=False) + "\n").encode()
    return ingest_p_batch_via_app8(
        asset="FFmpeg", source_context_bytes=context,
        source_context_sha256=sha, frozen_slots=slots, p_batch_bytes=raw)


class ProductPIngressTests(unittest.TestCase):
    def test_six_candidates_compile_through_actual_app8_hypothesis_freeze(self):
        slots, ctx, sha, batch = fixture()
        out = run(slots, ctx, sha, batch)
        self.assertEqual(out["case_count"], 6)
        self.assertEqual(out["app8_hypotheses_origin"], "MODEL_PROPOSAL_ONLY")
        self.assertEqual(len(out["app8_frozen_hypotheses_sha256"]), 64)
        self.assertFalse(out["actual_app8_predictor_transport_independently_verified"])
        self.assertFalse(out["formal_product_release_qualified"])

    def test_wrong_source_bytes_refused(self):
        slots, ctx, sha, batch = fixture()
        with self.assertRaisesRegex(PilotBlocked, "context bytes mismatch"):
            run(slots, ctx + b"tampered", sha, batch)

    def test_missing_case_and_duplicate_rejected(self):
        slots, ctx, sha, batch = fixture()
        batch["cases"].pop()
        with self.assertRaises(PilotBlocked):
            run(slots, ctx, sha, batch)
        slots, ctx, sha, batch = fixture()
        batch["cases"][0] = copy.deepcopy(batch["cases"][1])
        with self.assertRaises(PilotBlocked):
            run(slots, ctx, sha, batch)

    def test_cross_source_and_wrong_role_rejected(self):
        slots, ctx, sha, batch = fixture()
        batch["cases"][0]["source_anchor"]["path"] = "not approved"
        with self.assertRaises(PilotBlocked):
            run(slots, ctx, sha, batch)
        slots, ctx, sha, batch = fixture()
        batch["role"] = "R"
        with self.assertRaises(PilotBlocked):
            run(slots, ctx, sha, batch)

    def test_private_oracle_key_refused_and_app8_contract_bound(self):
        slots, ctx, sha, batch = fixture()
        batch["cases"][0]["hidden_truth"] = "yes"
        with self.assertRaises(PilotBlocked):
            run(slots, ctx, sha, batch)
        slots, ctx, sha, batch = fixture()
        batch["cases"][0]["proposal"] = "x" * 2001
        with self.assertRaises(PilotBlocked):
            run(slots, ctx, sha, batch)

    def test_output_sha_changes_with_candidate_proposal(self):
        slots, ctx, sha, batch = fixture()
        first = run(slots, ctx, sha, batch)
        batch["cases"][0]["proposal"] += " with different input"
        next_result = run(slots, ctx, sha, batch)
        self.assertNotEqual(first["app8_frozen_hypotheses_sha256"],
                            next_result["app8_frozen_hypotheses_sha256"])


if __name__ == "__main__":
    unittest.main()
