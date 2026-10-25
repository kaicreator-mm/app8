"""DIVERGED applicability admission tests; synthetic keys, NOT evaluated claims.

R17 contract: 17 negatives + 1 positive pin. The authority key below is
deliberately different bytes from the execution runner key in test_mla_bridge;
production provisioning must never share the AttestationGate HMAC either.
"""
from __future__ import annotations

from dataclasses import replace
import hashlib
import hmac
import json
from pathlib import Path
import tempfile
import unittest

from app8.evidence.applicability import (
    MAC_PLACEHOLDER, ApplicabilityAdmissionError, ApplicabilityApproval,
    ApplicabilityVerifier,
)
from app8.evidence.mla_bridge import (
    FrozenExecutionScope, MLAEvidenceBlocked, reconcile_observation,
)
from app8.evidence.attestation import AttestationGate
from app8.storage import EvidenceStore

RUNNER_KEY = b"s" * 32
AUTHORITY_KEY = b"a" * 32  # never equal to RUNNER_KEY; separate MAC domain
POLICY = "b" * 64
IMAGE = "c" * 64
SOURCE = "d" * 64
TARGET = "e" * 64
PLAN = "f" * 64
FIXTURE = "1" * 64
CLAIM_SCOPE = "9" * 64
RELEASE_COMMIT = "3" * 40
AUTHORITY_ID = "lo-mapping-authority"
PRE_OUTCOME_AT = "2027-01-01T00:00:00Z"   # run happens after ledger admission
POST_OUTCOME_AT = "2020-01-01T00:00:00Z"  # run predates any possible admission


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


def make_diverged_evidence(recorded_at=PRE_OUTCOME_AT):
    return {
        "schema_version":"app8-evidence-v1",
        "evidence_id":"ev:v04-mla-lo002",
        "claim_id":"V04-LO-002",
        "capability_id":"cap:mla-lo-test",
        "source":{"repository":"libreoffice/core","revision":"frozen-branch",
                  "content_sha256":SOURCE},
        "target":{"identity":"libreoffice-26.8.1.1-msi", "package_sha256":TARGET,
                  "environment_id":"clean-pinned", "mapping_relation":"DIVERGED"},
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
                       "recorded_at":recorded_at},
        "assessment":{"verdict":"SUPPORTED",
                      "assessor_kind":"DETERMINISTIC_ASSERTION_ENGINE",
                      "reason_codes":["EXIT_CODE_OK"]},
        "replay":{"manifest_sha256":"5"*64,
                  "artifact_location":"LOCAL_CONTENT_ADDRESSED"},
    }


def make_runner_receipt(evidence, nonce="a"*32):
    env = {
        "schema_version":"app8-attested-evidence-v2",
        "evidence_sha256":hashlib.sha256(canonical(evidence)).hexdigest(),
        "runner_id":"trusted-fixture",
        "policy_sha256":POLICY,
        "image_sha256":IMAGE,
        "nonce":nonce,
    }
    env["mac_sha256"] = hmac.new(RUNNER_KEY, canonical(env), hashlib.sha256).hexdigest()
    return env


def make_unsigned_approval(case_id="V04-LO-002", source_sha=SOURCE, target_sha=TARGET,
                           plan_sha=PLAN, fixture_sha=FIXTURE,
                           claim_scope=CLAIM_SCOPE):
    return ApplicabilityApproval(
        schema_version="app8-applicability-approval-v1",
        case_id=case_id,
        authority_id=AUTHORITY_ID,
        source_revision="frozen-branch@3317-ahead",
        source_content_sha256=source_sha,
        release_commit=RELEASE_COMMIT,
        target_package_sha256=target_sha,
        claim_scope_sha256=claim_scope,
        plan_sha256=plan_sha,
        fixture_sha256=fixture_sha,
        verdict_origin="INDEPENDENT_AUTHORITY_SIGNED",
        issued_at="2026-10-26T00:00:00Z",
        mac_sha256=MAC_PLACEHOLDER,
    )


class DivergedApplicabilityAdmissionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name)
        self.store = EvidenceStore(path/"store")
        self.addCleanup(self.store.close)
        self.gate = AttestationGate(verification_key=RUNNER_KEY, runner_id="trusted-fixture",
                                    policy_sha256=POLICY, image_sha256=IMAGE,
                                    nonce_db=path/"accepted.sqlite")
        self.addCleanup(self.gate.close)
        self.verifier = ApplicabilityVerifier(authority_key=AUTHORITY_KEY,
                                              authority_id=AUTHORITY_ID,
                                              approval_db=path/"applicability.sqlite")
        self.addCleanup(self.verifier.close)
        self.approval = self.verifier.seal(make_unsigned_approval())
        self.evidence = make_diverged_evidence()
        self.receipt = make_runner_receipt(self.evidence)
        self.scope = FrozenExecutionScope(source_sha256=SOURCE, target_sha256=TARGET,
                                          plan_sha256=PLAN, fixture_sha256=FIXTURE,
                                          relation="DIVERGED")
        self.case = {"case_id":"V04-LO-002",
                     "source_verification_claim":"CANDIDATE_ONLY",
                     "oracle_visible_to_predictor":False}

    def _record(self):
        self.store.append_evidence(self.evidence)
        self.gate.accept(self.evidence, self.receipt)

    def _admit(self):
        self.verifier.admit(self.approval)

    def _bridge(self, **changes):
        payload = dict(case=self.case, evidence=self.evidence, receipt=self.receipt,
                       store=self.store, gate=self.gate, scope=self.scope,
                       applicability=self.approval, applicability_verifier=self.verifier)
        payload.update(changes)
        return reconcile_observation(**payload)

    def test_positive_diverged_with_preoutcome_admission_reports_two_keys_only(self):
        self._record(); self._admit()
        report = self._bridge()
        self.assertEqual(report["status"],
                         "AUTHENTICATED_EXECUTION_NOT_INDEPENDENT_SEMANTIC_ORACLE")
        self.assertTrue(report["real_execution_receipt_accepted"])
        self.assertFalse(report["independent_behavior_oracle_verified"])
        self.assertFalse(report["capability_promotion_allowed"])
        self.assertFalse(report["formal_product_release_qualified"])
        self.assertEqual(report["applicability_authority"], AUTHORITY_ID)
        self.assertEqual(report["applicability_claim_scope_sha256"], CLAIM_SCOPE)
        baseline = {"schema_version","case_id","evidence_id","evidence_sha256",
                    "receipt_sha256","source_sha256","target_sha256","plan_sha256",
                    "fixture_sha256","assessor_verdict","status",
                    "real_execution_receipt_accepted",
                    "independent_behavior_oracle_verified",
                    "capability_promotion_allowed","formal_product_release_qualified"}
        self.assertEqual(set(report) - baseline,
                         {"applicability_authority","applicability_claim_scope_sha256"})
        again = self._bridge()  # idempotent same-digest ledger recheck
        self.assertEqual(again, report)

    def test_n01_diverged_missing_approval_keeps_pinned_message(self):
        self._record()
        with self.assertRaisesRegex(MLAEvidenceBlocked, "applicability required"):
            self._bridge(applicability=None)

    def test_n02_diverged_missing_verifier_rejected(self):
        self._record(); self._admit()
        with self.assertRaisesRegex(MLAEvidenceBlocked, "applicability required"):
            self._bridge(applicability_verifier=None)

    def test_n03_duck_typed_fake_verifier_rejected(self):
        self._record()
        class FakeVerifier:
            def verify(self, **_): return True
        with self.assertRaisesRegex(MLAEvidenceBlocked, "applicability required"):
            self._bridge(applicability_verifier=FakeVerifier())

    def test_n04_verifier_subclass_rejected(self):
        self._record()
        class SubVerifier(ApplicabilityVerifier):
            pass
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        sub = SubVerifier(authority_key=AUTHORITY_KEY, authority_id=AUTHORITY_ID,
                          approval_db=Path(tmp.name)/"sub.sqlite")
        self.addCleanup(sub.close)
        with self.assertRaisesRegex(MLAEvidenceBlocked, "applicability required"):
            self._bridge(applicability_verifier=sub)

    def test_n05_attestation_gate_as_verifier_rejected(self):
        self._record()
        with self.assertRaisesRegex(MLAEvidenceBlocked, "applicability required"):
            self._bridge(applicability_verifier=self.gate)

    def test_n06_self_signed_wrong_authority_key_rejected(self):
        self._record()
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        impostor = ApplicabilityVerifier(authority_key=b"x"*32, authority_id=AUTHORITY_ID,
                                         approval_db=Path(tmp.name)/"imp.sqlite")
        self.addCleanup(impostor.close)
        forged = impostor.seal(make_unsigned_approval())
        impostor.admit(forged)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(applicability=forged, applicability_verifier=self.verifier)

    def test_n07_tampered_approval_record_rejected(self):
        self._record(); self._admit()
        tampered = replace(self.approval, issued_at="2027-12-31T00:00:00Z")
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(applicability=tampered)

    def test_n08_cross_case_approval_binding_rejected(self):
        self._record()
        other = self.verifier.seal(make_unsigned_approval(case_id="V04-LO-OTHER"))
        self.verifier.admit(other)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(applicability=other)

    def test_n09_approval_source_binding_rejected(self):
        self._record()
        other = self.verifier.seal(make_unsigned_approval(source_sha="0"*64))
        self.verifier.admit(other)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(applicability=other)

    def test_n10_approval_target_release_binding_rejected(self):
        self._record()
        other = self.verifier.seal(make_unsigned_approval(target_sha="0"*64))
        self.verifier.admit(other)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(applicability=other)

    def test_n11_approval_plan_binding_rejected(self):
        self._record()
        other = self.verifier.seal(make_unsigned_approval(plan_sha="0"*64))
        self.verifier.admit(other)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(applicability=other)

    def test_n12_approval_fixture_binding_rejected(self):
        self._record()
        other = self.verifier.seal(make_unsigned_approval(fixture_sha="0"*64))
        self.verifier.admit(other)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(applicability=other)

    def test_n13_same_case_conflicting_digest_fails_closed(self):
        self._record(); self._admit()
        conflicting = self.verifier.seal(make_unsigned_approval(claim_scope="8"*64))
        with self.assertRaises(ApplicabilityAdmissionError):
            self.verifier.admit(conflicting)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(applicability=conflicting)

    def test_n14_approval_after_outcome_rejected(self):
        self.evidence = make_diverged_evidence(recorded_at=POST_OUTCOME_AT)
        self.receipt = make_runner_receipt(self.evidence)
        self._record(); self._admit()
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge()

    def test_n15_unadmitted_approval_rejected_in_bridge(self):
        self._record()  # sealed but never ledger-admitted pre-outcome
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge()

    def test_n16_naked_boolean_and_dict_approval_rejected(self):
        self._record()
        with self.assertRaisesRegex(MLAEvidenceBlocked, "applicability required"):
            self._bridge(applicability=True)
        with self.assertRaisesRegex(MLAEvidenceBlocked, "applicability required"):
            self._bridge(applicability={"case_id": "V04-LO-002", "approved": True})

    def test_n17_unresolved_with_full_valid_approval_still_blocked(self):
        self._record(); self._admit()
        evidence = make_diverged_evidence()
        evidence["evidence_id"] = "ev:v04-mla-lo002-unresolved"
        evidence["target"]["mapping_relation"] = "UNRESOLVED"
        receipt = make_runner_receipt(evidence, nonce="b"*32)
        self.store.append_evidence(evidence)
        self.gate.accept(evidence, receipt)
        scope = FrozenExecutionScope(source_sha256=SOURCE, target_sha256=TARGET,
                                     plan_sha256=PLAN, fixture_sha256=FIXTURE,
                                     relation="UNRESOLVED")
        with self.assertRaisesRegex(MLAEvidenceBlocked, "applicability required"):
            self._bridge(scope=scope, evidence=evidence, receipt=receipt)


if __name__=="__main__":
    unittest.main()
