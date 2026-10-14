"""Synthetic P/R/X capture isolation tests; not a real provider integration."""
import copy
import hashlib
import json
import unittest

from app8.mla.blind_capture import (
    SOURCE_BLOB, BlindCaptureBlocked, verify_blind_capture
)

ROLE_VIS = {"P":"P_SOURCE_ONLY", "R":"R_REFERENCE_SOURCE_ONLY",
            "X":"X_CHALLENGER_SOURCE_ONLY"}
SOURCE_CONTEXT = "1"*64


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fixture():
    freeze = {
        "schema_version": "v04-mla-blind-freeze-v1",
        "study_id": "V04-MLA-1",
        "source_pack_git_blob": SOURCE_BLOB,
        "frozen_before_first_response": True,
        "source_context_sha256": SOURCE_CONTEXT,
        "roles": {},
    }
    prompts = {}
    outputs = {}
    for role in ("P", "R", "X"):
        content = {
            "source_pack_git_blob": SOURCE_BLOB,
            "source_context_sha256": SOURCE_CONTEXT,
            "task_instruction_sha256": sha(role.encode()),
            "visibility_scope": ROLE_VIS[role],
        }
        raw = (json.dumps(content, sort_keys=True) + "\n").encode()
        prompts[role] = raw
        outputs[role] = ("sealed-" + role).encode()
        freeze["roles"][role] = {
            "model_family": "family-" + role,
            "provider": "provider",
            "model_version": "synthetic-1",
            "prompt_sha256": sha(b"prompt-" + role.encode()),
            "sampling_sha256": sha(b"sampling-" + role.encode()),
            "input_sha256": sha(raw),
        }
    return freeze, prompts, outputs


class BlindCaptureTests(unittest.TestCase):
    def test_three_distinct_role_captures_structural_only(self):
        result = verify_blind_capture(*fixture())
        self.assertEqual(result["status"], "STRUCTURAL_CAPTURE_ONLY")
        self.assertEqual(set(result["roles"]), {"P","R","X"})
        self.assertTrue(result["reference_challenger_different_model_families"])
        self.assertFalse(result["trusted_provider_invocation_proven"])
        self.assertFalse(result["real_software_oracle_verified"])
        self.assertFalse(result["empirical_qualification_pass"])

    def test_identical_reference_and_challenge_family_is_flagged(self):
        f, i, o = fixture()
        f["roles"]["X"]["model_family"] = f["roles"]["R"]["model_family"]
        result=verify_blind_capture(f,i,o)
        self.assertEqual(result["status"],"PROVISIONAL_CORRELATED_MODEL_FAMILY")
        self.assertFalse(result["formal_product_release_qualified"])

    def test_frozen_input_byte_swap_blocked(self):
        f, i, o = fixture()
        i["P"] = i["R"]
        with self.assertRaises(BlindCaptureBlocked):
            verify_blind_capture(f,i,o)

    def test_hidden_truth_field_rejected_even_if_sha_rebound(self):
        f,i,o=fixture()
        modified=json.loads(i["X"])
        modified["hidden_truth"]="TRUE"
        i["X"]=(json.dumps(modified,sort_keys=True)+"\n").encode()
        f["roles"]["X"]["input_sha256"]=sha(i["X"])
        with self.assertRaisesRegex(BlindCaptureBlocked,"non-allowlisted"):
            verify_blind_capture(f,i,o)

    def test_hidden_role_scope_rejected(self):
        f,i,o=fixture()
        modified=json.loads(i["P"])
        modified["visibility_scope"]="P_ORACLE_ACCESS"
        i["P"]=(json.dumps(modified,sort_keys=True)+"\n").encode()
        f["roles"]["P"]["input_sha256"]=sha(i["P"])
        with self.assertRaises(BlindCaptureBlocked):
            verify_blind_capture(f,i,o)

    def test_missing_challenger_output_blocked(self):
        f,i,o=fixture()
        del o["X"]
        with self.assertRaisesRegex(BlindCaptureBlocked,"all P/R/X"):
            verify_blind_capture(f,i,o)

    def test_unfrozen_campaign_blocked(self):
        f,i,o=fixture()
        f["frozen_before_first_response"]=False
        with self.assertRaises(BlindCaptureBlocked):
            verify_blind_capture(f,i,o)

    def test_duplicate_context_json_key_rejected(self):
        f,i,o=fixture()
        i["P"]=b'{"source_pack_git_blob":"a","source_pack_git_blob":"b"}'
        f["roles"]["P"]["input_sha256"]=sha(i["P"])
        with self.assertRaises(BlindCaptureBlocked):
            verify_blind_capture(f,i,o)

    def test_mutated_output_changes_commitment_not_truth(self):
        f,i,o=fixture()
        a=verify_blind_capture(f,i,o)
        o["R"]=b"changed-response"
        b=verify_blind_capture(f,i,o)
        self.assertNotEqual(a["roles"]["R"]["output_transcript_sha256"],
                            b["roles"]["R"]["output_transcript_sha256"])
        self.assertFalse(b["empirical_qualification_pass"])

    def test_invalid_model_sampling_identity_rejected(self):
        f,i,o=fixture()
        f["roles"]["R"]["sampling_sha256"]="not-sha"
        with self.assertRaises(BlindCaptureBlocked):
            verify_blind_capture(f,i,o)


if __name__=="__main__":
    unittest.main()
