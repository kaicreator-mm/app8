"""MLA trusted Evidence bridge tests; synthetic receipts, NOT evaluated app8 claims."""
from __future__ import annotations

import copy
import hashlib
import hmac
import json
from pathlib import Path
import tempfile
import unittest

from app8.evidence.mla_bridge import (
    FrozenExecutionScope, MLAEvidenceBlocked, reconcile_observation
)
from app8.evidence.attestation import AttestationGate
from app8.storage import EvidenceStore

KEY = b"s" * 32
POLICY = "b" * 64
IMAGE = "c" * 64
SOURCE = "d" * 64
TARGET = "e" * 64
PLAN = "f" * 64
FIXTURE = "1" * 64


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


def make_evidence():
    return {
        "schema_version":"app8-evidence-v1",
        "evidence_id":"ev:v04-mla-c001",
        "claim_id":"V04-FFMPEG-001",
        "capability_id":"cap:mla-ffmpeg-test",
        "source":{"repository":"FFmpeg/FFmpeg","revision":"frozen","content_sha256":SOURCE},
        "target":{"identity":"ffmpeg-target", "package_sha256":TARGET,
                  "environment_id":"clean-pinned", "mapping_relation":"SAME"},
        "fixture":{"content_sha256":FIXTURE,"input_description":"synthetic fixture",
                   "reset_procedure":"fresh temporary directory"},
        "plan":{"plan_sha256":PLAN,"binding_id":"binding:mla-smoke",
                "assertions":["exit_code==0"],
                "budget":{"wall_seconds":2,"max_output_bytes":1024,
                          "network_allowed":False,"mutation_allowed":False}},
        "observation":{"observer":"DETERMINISTIC_EXECUTION_ADAPTER",
                       "execution_status":"EXECUTED","invocation_sha256":"2"*64,
                       "exit_code":0,"stdout_sha256":"3"*64,
                       "stderr_sha256":"4"*64,"artifacts":[],
                       "recorded_at":"2026-10-14T00:00:00Z"},
        "assessment":{"verdict":"SUPPORTED",
                      "assessor_kind":"DETERMINISTIC_ASSERTION_ENGINE",
                      "reason_codes":["EXIT_CODE_OK"]},
        "replay":{"manifest_sha256":"5"*64,
                  "artifact_location":"LOCAL_CONTENT_ADDRESSED"},
    }


def make_receipt(evidence):
    env = {
        "schema_version":"app8-attested-evidence-v2",
        "evidence_sha256":hashlib.sha256(canonical(evidence)).hexdigest(),
        "runner_id":"trusted-fixture",
        "policy_sha256":POLICY,
        "image_sha256":IMAGE,
        "nonce":"a"*32,
    }
    env["mac_sha256"] = hmac.new(KEY, canonical(env), hashlib.sha256).hexdigest()
    return env


class MLATrustedBridgeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name)
        self.store = EvidenceStore(path/"store")
        self.addCleanup(self.store.close)
        self.gate = AttestationGate(verification_key=KEY,runner_id="trusted-fixture",
                                    policy_sha256=POLICY,image_sha256=IMAGE,
                                    nonce_db=path/"accepted.sqlite")
        self.addCleanup(self.gate.close)
        self.evidence = make_evidence()
        self.receipt = make_receipt(self.evidence)
        self.scope = FrozenExecutionScope(source_sha256=SOURCE,target_sha256=TARGET,
                                          plan_sha256=PLAN,fixture_sha256=FIXTURE,
                                          relation="SAME")
        self.case = {"case_id":"V04-FFMPEG-001",
                     "source_verification_claim":"CANDIDATE_ONLY",
                     "oracle_visible_to_predictor":False}

    def _record(self):
        self.store.append_evidence(self.evidence)
        self.gate.accept(self.evidence,self.receipt)

    def _bridge(self, **changes):
        payload = dict(case=self.case,evidence=self.evidence,receipt=self.receipt,
                       store=self.store,gate=self.gate,scope=self.scope)
        payload.update(changes)
        return reconcile_observation(**payload)

    def test_authenticated_retained_observation_is_not_behavioral_truth(self):
        self._record()
        r=self._bridge()
        self.assertEqual(r["status"],
                         "AUTHENTICATED_EXECUTION_NOT_INDEPENDENT_SEMANTIC_ORACLE")
        self.assertEqual(r["assessor_verdict"],"SUPPORTED")
        self.assertTrue(r["real_execution_receipt_accepted"])
        self.assertFalse(r["independent_behavior_oracle_verified"])
        self.assertFalse(r["capability_promotion_allowed"])
        self.assertFalse(r["formal_product_release_qualified"])

    def test_unaccepted_signature_is_blocked(self):
        self.store.append_evidence(self.evidence)
        with self.assertRaisesRegex(MLAEvidenceBlocked,"not authenticated"):
            self._bridge()

    def test_tampered_signature_is_blocked(self):
        self._record()
        bad=copy.deepcopy(self.receipt)
        bad["mac_sha256"]="f"*64
        with self.assertRaisesRegex(MLAEvidenceBlocked,"not authenticated"):
            self._bridge(receipt=bad)

    def test_model_attestation_flag_is_not_authoritative(self):
        self._record()
        bad=dict(self.case,oracle_visible_to_predictor=True)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(case=bad)

    def test_case_id_mismatch_fails(self):
        self._record()
        with self.assertRaisesRegex(MLAEvidenceBlocked,"claim identity mismatch"):
            self._bridge(case=dict(self.case,case_id="V04-OTHER-002"))

    def test_missing_store_record_fails(self):
        self.gate.accept(self.evidence,self.receipt)
        with self.assertRaisesRegex(MLAEvidenceBlocked,"missing or mismatched"):
            self._bridge()

    def test_mismatched_plan_pin_fails(self):
        self._record()
        other=FrozenExecutionScope(source_sha256=SOURCE,target_sha256=TARGET,
                                   plan_sha256="0"*64,fixture_sha256=FIXTURE,
                                   relation="SAME")
        with self.assertRaisesRegex(MLAEvidenceBlocked,"scope mismatch"):
            self._bridge(scope=other)

    def test_mismatched_target_pin_fails(self):
        self._record()
        other=FrozenExecutionScope(source_sha256=SOURCE,target_sha256="0"*64,
                                   plan_sha256=PLAN,fixture_sha256=FIXTURE,
                                   relation="SAME")
        with self.assertRaisesRegex(MLAEvidenceBlocked,"scope mismatch"):
            self._bridge(scope=other)

    def test_source_pin_mismatch_fails(self):
        self._record()
        other=FrozenExecutionScope(source_sha256="0"*64,target_sha256=TARGET,
                                   plan_sha256=PLAN,fixture_sha256=FIXTURE,
                                   relation="SAME")
        with self.assertRaisesRegex(MLAEvidenceBlocked,"scope mismatch"):
            self._bridge(scope=other)

    def test_diverged_without_external_applicability_fails(self):
        self._record()
        other=FrozenExecutionScope(source_sha256=SOURCE,target_sha256=TARGET,
                                   plan_sha256=PLAN,fixture_sha256=FIXTURE,
                                   relation="DIVERGED")
        with self.assertRaisesRegex(MLAEvidenceBlocked,"applicability required"):
            self._bridge(scope=other)

    def test_model_only_claim_fails_schema_or_origin(self):
        self._record()
        modified=copy.deepcopy(self.evidence)
        modified["assessment"]["assessor_kind"]="MODEL_PROPOSAL_ONLY"
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(evidence=modified)

    def test_nonexecuted_observation_fails(self):
        self._record()
        modified=copy.deepcopy(self.evidence)
        modified["observation"]["execution_status"]="NOT_RUN"
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(evidence=modified)

    def test_invalid_scope_pin_fails_initialization(self):
        with self.assertRaises(MLAEvidenceBlocked):
            FrozenExecutionScope(source_sha256="no",target_sha256=TARGET,
                                 plan_sha256=PLAN,fixture_sha256=FIXTURE,
                                 relation="SAME")


if __name__=="__main__":
    unittest.main()
