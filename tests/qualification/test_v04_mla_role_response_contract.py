"""No network, no LLM: v5 role-batch response format contract rehearsal gate.

Regression target (issue #166 Step H): the v4 pilot sealed 72/72 case rows
with string `source_anchor` values, so every P batch failed the typed ingress.
The gate must reject every observed string shape and pass only the frozen
{path,blob} object form.
"""
import hashlib
import json
import unittest

from scripts.v04_mla_pilot_reducer import ROOT, ALLOWLIST, PilotBlocked
from scripts.v04_mla_app8_p_ingress import ingest_p_batch_via_app8
from scripts.v04_mla_role_response_contract import validate_response_contract

SCHEMA = ROOT / "research/mla/v04-mla-role-batch-response-contract.schema.json"
SYNTHETIC_PATH = "doc/example.texi"
SYNTHETIC_BLOB = "b" * 40

# The four desensitized string shapes actually observed across the v4 batches.
V4_STRING_SHAPES = (
    SYNTHETIC_PATH + " git blob: " + SYNTHETIC_BLOB,
    SYNTHETIC_PATH + ":" + SYNTHETIC_BLOB,
    SYNTHETIC_PATH + " | git blob: " + SYNTHETIC_BLOB,
    SYNTHETIC_PATH + " @ git blob " + SYNTHETIC_BLOB,
)


def synthetic_slots(asset="FFmpeg"):
    return [
        {"case_id": f"V04-FFMPEG-{i:03d}",
         "source_anchor": {"path": SYNTHETIC_PATH, "blob": SYNTHETIC_BLOB}}
        for i in range(1, 7)
    ]


def batch(asset="FFmpeg", role="P", slots=None, anchor_form="object"):
    slots = slots or synthetic_slots(asset)
    context = b"fixture verified context, NOT real upstream source"
    doc = {
        "schema_version": "v04-mla-role-batch-v1",
        "study_id": "V04-MLA-1",
        "asset": asset, "role": role,
        "source_context_sha256": hashlib.sha256(context).hexdigest(),
        "cases": [
            {"case_id": s["case_id"],
             "source_anchor": dict(s["source_anchor"])
             if anchor_form == "object" else anchor_form,
             "origin": "LLM_PROPOSED", "kind": "P_CAPABILITY_PREDICTION",
             "proposal": "Synthetic hypothesis " + s["case_id"],
             "constraints": ["no observed behavior"]}
            for s in slots
        ],
    }
    return slots, context, doc


def run(role="P", asset="FFmpeg", content_bytes=None, slots=None,
        context=None, sha=None):
    slots = slots or synthetic_slots(asset)
    context = context or b"fixture verified context, NOT real upstream source"
    return validate_response_contract(
        role=role, asset=asset,
        content_bytes=content_bytes or (json.dumps(batch(
            asset=asset, role=role, slots=slots)[2],
            sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"),
        frozen_slots=slots,
        source_context_sha256=sha or hashlib.sha256(context).hexdigest())


class ResponseContractTests(unittest.TestCase):
    def test_object_anchor_batch_passes_with_safe_metadata_only(self):
        out = run()
        self.assertEqual(out["status"], "RESPONSE_CONTRACT_STRUCTURAL_PASS_ONLY")
        self.assertEqual(out["case_count"], 6)
        self.assertEqual(len(out["case_payload_sha256"]), 6)
        self.assertTrue(out["source_anchor_object_form_enforced"])
        self.assertFalse(out["real_behavior_oracle_verified"])
        self.assertFalse(out["capability_promotion_allowed"])
        self.assertFalse(out["formal_product_release_qualified"])

    def test_every_observed_v4_string_anchor_shape_fails_closed(self):
        for shape in V4_STRING_SHAPES:
            slots, context, doc = batch(anchor_form=shape)
            raw = (json.dumps(doc, sort_keys=True, ensure_ascii=False)
                   + "\n").encode("utf-8")
            with self.assertRaisesRegex(PilotBlocked, "rendered as string"):
                run(content_bytes=raw, slots=slots, context=context)

    def test_mismatched_object_anchor_fails(self):
        slots, context, doc = batch()
        doc["cases"][0]["source_anchor"]["blob"] = "c" * 40
        raw = (json.dumps(doc, sort_keys=True, ensure_ascii=False)
               + "\n").encode("utf-8")
        with self.assertRaisesRegex(PilotBlocked, "differs from frozen slot"):
            run(content_bytes=raw, slots=slots, context=context)

    def test_proposal_2000_boundary_and_ingress_bound(self):
        slots, context, doc = batch()
        doc["cases"][0]["proposal"] = "x" * 2000
        raw = (json.dumps(doc, sort_keys=True, ensure_ascii=False)
               + "\n").encode("utf-8")
        self.assertEqual(run(content_bytes=raw, slots=slots, context=context)["case_count"], 6)
        slots, context, doc = batch()
        doc["cases"][0]["proposal"] = "x" * 2001
        raw = (json.dumps(doc, sort_keys=True, ensure_ascii=False)
               + "\n").encode("utf-8")
        with self.assertRaisesRegex(PilotBlocked, "2000-character"):
            run(content_bytes=raw, slots=slots, context=context)

    def test_constraint_bounds_fail_closed(self):
        slots, context, doc = batch()
        doc["cases"][0]["constraints"] = [f"c{i}" for i in range(9)]
        raw = (json.dumps(doc, sort_keys=True, ensure_ascii=False)
               + "\n").encode("utf-8")
        with self.assertRaisesRegex(PilotBlocked, "constraints"):
            run(content_bytes=raw, slots=slots, context=context)
        slots, context, doc = batch()
        doc["cases"][0]["constraints"] = ["y" * 401]
        raw = (json.dumps(doc, sort_keys=True, ensure_ascii=False)
               + "\n").encode("utf-8")
        with self.assertRaisesRegex(PilotBlocked, "constraints"):
            run(content_bytes=raw, slots=slots, context=context)

    def test_non_strict_json_content_fails_before_structure(self):
        slots, context, doc = batch()
        fenced = ("```json\n"
                  + json.dumps(doc, sort_keys=True, ensure_ascii=False)
                  + "\n```").encode("utf-8")
        with self.assertRaises(PilotBlocked):
            run(content_bytes=fenced, slots=slots, context=context)

    def test_markdown_fenced_content_rejected_with_distinct_error(self):
        # v4 Step H defect: all four R sealed batches were markdown-fenced.
        slots, context, doc = batch()
        body = json.dumps(doc, sort_keys=True, ensure_ascii=False)
        for fenced in (
                ("```json\n" + body + "\n```").encode("utf-8"),
                ("```\n" + body + "\n```").encode("utf-8")):
            with self.assertRaisesRegex(PilotBlocked, "code fence"):
                run(content_bytes=fenced, slots=slots, context=context)

    def test_whitespace_padding_still_accepted_no_false_fence_positive(self):
        slots, context, doc = batch()
        padded = (b"\n  "
                  + json.dumps(doc, sort_keys=True, ensure_ascii=False).encode("utf-8")
                  + b"  \n")
        out = run(content_bytes=padded, slots=slots, context=context)
        self.assertEqual(out["status"], "RESPONSE_CONTRACT_STRUCTURAL_PASS_ONLY")

    def test_identity_kind_and_coverage_fail_closed(self):
        slots, context, doc = batch(role="R")
        raw = (json.dumps(doc, sort_keys=True, ensure_ascii=False)
               + "\n").encode("utf-8")
        with self.assertRaisesRegex(PilotBlocked, "kind mismatch"):
            run(role="R", content_bytes=raw, slots=slots, context=context)
        slots, context, doc = batch()
        doc["cases"].pop()
        raw = (json.dumps(doc, sort_keys=True, ensure_ascii=False)
               + "\n").encode("utf-8")
        with self.assertRaisesRegex(PilotBlocked, "exactly six"):
            run(content_bytes=raw, slots=slots, context=context)

    def test_contract_schema_pins_object_anchor_and_2000_bound(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        anchor = schema["properties"]["cases"]["items"]["properties"]["source_anchor"]
        self.assertEqual(anchor["type"], "object")
        proposal = schema["properties"]["cases"]["items"]["properties"]["proposal"]
        self.assertEqual(proposal["maxLength"], 2000)

    def test_schema_accepts_object_form_and_rejects_string_form(self):
        import jsonschema
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        slots, _, doc = batch()
        jsonschema.validate(doc, schema)
        slots, _, doc = batch(anchor_form=V4_STRING_SHAPES[0])
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(doc, schema)

    def test_passing_contract_batch_compiles_through_real_app8_ingress(self):
        selected = json.loads((ROOT / ALLOWLIST).read_text(encoding="utf-8"))
        anchor_paths = sorted(selected["assets"]["FFmpeg"].items())[:6]
        slots = [
            {"case_id": f"V04-FFMPEG-{i:03d}",
             "source_anchor": {"path": p, "blob": b}}
            for i, (p, b) in enumerate(anchor_paths, 1)
        ]
        context = b"fixture verified context, NOT real upstream source"
        doc = {
            "schema_version": "v04-mla-role-batch-v1",
            "study_id": "V04-MLA-1",
            "asset": "FFmpeg", "role": "P",
            "source_context_sha256": hashlib.sha256(context).hexdigest(),
            "cases": [
                {"case_id": s["case_id"],
                 "source_anchor": dict(s["source_anchor"]),
                 "origin": "LLM_PROPOSED", "kind": "P_CAPABILITY_PREDICTION",
                 "proposal": "Synthetic hypothesis " + s["case_id"],
                 "constraints": ["no observed behavior"]}
                for s in slots
            ],
        }
        raw = (json.dumps(doc, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        out = validate_response_contract(
            role="P", asset="FFmpeg", content_bytes=raw, frozen_slots=slots,
            source_context_sha256=hashlib.sha256(context).hexdigest())
        self.assertEqual(out["status"], "RESPONSE_CONTRACT_STRUCTURAL_PASS_ONLY")
        ingress = ingest_p_batch_via_app8(
            asset="FFmpeg", source_context_bytes=context,
            source_context_sha256=hashlib.sha256(context).hexdigest(),
            frozen_slots=slots, p_batch_bytes=raw)
        self.assertEqual(ingress["case_count"], 6)
        self.assertEqual(ingress["app8_hypotheses_origin"], "MODEL_PROPOSAL_ONLY")


if __name__ == "__main__":
    unittest.main()
