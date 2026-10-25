"""DIVERGED applicability admission tests; synthetic keys, NOT evaluated claims.

R17 contract: 17 negatives + 1 positive pin. R1 review (R22) additions
N18-N23. R2 review (R24) changes: chronology is anchored to a pre-run
runner-entry RESERVATION (reserve_execution before the run; the reserved
nonce is embedded as the receipt nonce; admission must strictly precede the
reservation on the ledger journal) and the post-hoc witness API is gone;
the authority root fingerprint is fixed in reviewed source (no runtime pin
function; the shipped constant fails closed, tests activate the synthetic
development root in setUpModule). N24-N25 added accordingly. The synthetic
authority root is domain-separated from the execution runner key in
test_mla_bridge and can never equal it.
"""
from __future__ import annotations

from dataclasses import replace
import hashlib
import hmac
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from app8.evidence import applicability
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
AUTHORITY_ROOT_KEY = b"r" * 32  # synthetic dev root; activates the pin below
IMPOSTOR_KEY = b"x" * 32       # attacker-chosen; never matches any pin
POLICY = "b" * 64
IMAGE = "c" * 64
SOURCE = "d" * 64
TARGET = "e" * 64
PLAN = "f" * 64
FIXTURE = "1" * 64
CLAIM_SCOPE = "9" * 64
RELEASE_COMMIT = "3" * 40
SOURCE_REVISION = "frozen-branch"
AUTHORITY_ID = "lo-mapping-authority"
FUTURE_RECORDED_AT = "2027-01-01T00:00:00Z"  # runner-supplied claim, never load-bearing
SHIPPED_PIN = None  # the reviewed-source constant, saved before activation


def setUpModule():
    # Test-only activation: the shipped reviewed-source constant has no known
    # preimage (provisioning fails closed until a reviewed deployment commit
    # replaces it); tests activate the synthetic development root.
    global SHIPPED_PIN
    SHIPPED_PIN = applicability.AUTHORITY_ROOT_FINGERPRINT_SHA256
    applicability.AUTHORITY_ROOT_FINGERPRINT_SHA256 = hashlib.sha256(
        AUTHORITY_ROOT_KEY).hexdigest()


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


def make_diverged_evidence(recorded_at=FUTURE_RECORDED_AT):
    return {
        "schema_version":"app8-evidence-v1",
        "evidence_id":"ev:v04-mla-lo002",
        "claim_id":"V04-LO-002",
        "capability_id":"cap:mla-lo-test",
        "source":{"repository":"libreoffice/core","revision":SOURCE_REVISION,
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
                           claim_scope=CLAIM_SCOPE,
                           source_revision=SOURCE_REVISION,
                           release_commit=RELEASE_COMMIT):
    return ApplicabilityApproval(
        schema_version="app8-applicability-approval-v1",
        case_id=case_id,
        authority_id=AUTHORITY_ID,
        source_revision=source_revision,
        source_content_sha256=source_sha,
        release_commit=release_commit,
        target_package_sha256=target_sha,
        claim_scope_sha256=claim_scope,
        plan_sha256=plan_sha,
        fixture_sha256=fixture_sha,
        verdict_origin="INDEPENDENT_AUTHORITY_SIGNED",
        issued_at="2026-10-26T00:00:00Z",
        mac_sha256=MAC_PLACEHOLDER,
    )


def forge_with_key(approval, key):
    """Externally MAC an approval under an attacker key (seal() is closed)."""
    mac = hmac.new(key, canonical(approval.unsigned_payload()),
                   hashlib.sha256).hexdigest()
    return replace(approval, mac_sha256=mac)


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
        self.verifier = ApplicabilityVerifier.provision(
            root_key=AUTHORITY_ROOT_KEY, authority_id=AUTHORITY_ID,
            approval_db=path/"applicability.sqlite")
        self.addCleanup(self.verifier.close)
        self.approval = self.verifier.seal(make_unsigned_approval())
        self.scope = FrozenExecutionScope(source_sha256=SOURCE, target_sha256=TARGET,
                                          plan_sha256=PLAN, fixture_sha256=FIXTURE,
                                          relation="DIVERGED")
        self.case = {"case_id":"V04-LO-002",
                     "source_verification_claim":"CANDIDATE_ONLY",
                     "oracle_visible_to_predictor":False,
                     "target_release_commit":RELEASE_COMMIT,
                     "claim_scope_sha256":CLAIM_SCOPE}
        # Default evidence/receipt carry an UNRESERVED nonce; _reserve() is
        # the protocol step that mints a reserved entry before the run.
        self.evidence = make_diverged_evidence()
        self.receipt = make_runner_receipt(self.evidence)

    def _fresh_verifier(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        verifier = ApplicabilityVerifier.provision(
            root_key=AUTHORITY_ROOT_KEY, authority_id=AUTHORITY_ID,
            approval_db=Path(tmp.name)/"applicability.sqlite")
        self.addCleanup(verifier.close)
        return verifier

    def _reserve(self):
        self.nonce = self.verifier.reserve_execution(case_id=self.case["case_id"],
                                                     scope=self.scope)
        self.evidence = make_diverged_evidence()
        self.receipt = make_runner_receipt(self.evidence, nonce=self.nonce)

    def _record(self):
        self._reserve()
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

    def test_positive_diverged_with_preoutcome_admission_reports_applicability_keys_only(self):
        self._admit(); self._record()  # admission -> reserved entry -> run
        report = self._bridge()
        self.assertEqual(report["status"],
                         "AUTHENTICATED_EXECUTION_NOT_INDEPENDENT_SEMANTIC_ORACLE")
        self.assertTrue(report["real_execution_receipt_accepted"])
        self.assertFalse(report["independent_behavior_oracle_verified"])
        self.assertFalse(report["capability_promotion_allowed"])
        self.assertFalse(report["formal_product_release_qualified"])
        self.assertEqual(report["applicability_authority"], AUTHORITY_ID)
        self.assertEqual(report["applicability_claim_scope_sha256"], CLAIM_SCOPE)
        self.assertEqual(report["applicability_release_commit"], RELEASE_COMMIT)
        self.assertEqual(report["applicability_release_binding"],
                         "EXTERNAL_PROVISIONAL_CANDIDATE")
        baseline = {"schema_version","case_id","evidence_id","evidence_sha256",
                    "receipt_sha256","source_sha256","target_sha256","plan_sha256",
                    "fixture_sha256","assessor_verdict","status",
                    "real_execution_receipt_accepted",
                    "independent_behavior_oracle_verified",
                    "capability_promotion_allowed","formal_product_release_qualified"}
        self.assertEqual(set(report) - baseline,
                         {"applicability_authority","applicability_claim_scope_sha256",
                          "applicability_release_commit","applicability_release_binding"})
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
        sub = SubVerifier(authority_key=AUTHORITY_ROOT_KEY, authority_id=AUTHORITY_ID,
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
        forged = forge_with_key(make_unsigned_approval(), IMPOSTOR_KEY)
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
        # The R2-review attack sequence: runner entry reserved and accepted
        # FIRST, approval admitted only afterwards. The reservation nonce was
        # handed out strictly before the late admission, so the journal order
        # (ADMISSION must precede RESERVATION) blocks it — even though the
        # runner-supplied recorded_at claims a far-future instant (R24 P1-01).
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

    def test_n18_self_issued_verifier_injected_rejected(self):
        # Full P1-01 attack: attacker-chosen key/db/id, self-consistent forged
        # approval, and the impostor verifier itself passed to the bridge.
        self._record()
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        impostor = ApplicabilityVerifier(authority_key=IMPOSTOR_KEY,
                                         authority_id=AUTHORITY_ID,
                                         approval_db=Path(tmp.name)/"imp.sqlite")
        self.addCleanup(impostor.close)
        forged = forge_with_key(make_unsigned_approval(), IMPOSTOR_KEY)
        with self.assertRaises(ApplicabilityAdmissionError):
            impostor.admit(forged)   # minting/ledger route closed to unprovisioned
        with self.assertRaises(ApplicabilityAdmissionError):
            impostor.verify(approval=forged, case_id="V04-LO-002", scope=self.scope,
                            evidence=self.evidence, case=self.case,
                            receipt=self.receipt)
        with self.assertRaisesRegex(MLAEvidenceBlocked, "applicability required"):
            self._bridge(applicability=forged, applicability_verifier=impostor)

    def test_n19_wrong_root_key_provisioning_rejected(self):
        self._record()
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        with self.assertRaises(ApplicabilityAdmissionError):
            ApplicabilityVerifier.provision(root_key=IMPOSTOR_KEY,
                                            authority_id=AUTHORITY_ID,
                                            approval_db=Path(tmp.name)/"x.sqlite")
        inert = ApplicabilityVerifier(authority_key=IMPOSTOR_KEY,
                                      authority_id=AUTHORITY_ID,
                                      approval_db=Path(tmp.name)/"y.sqlite")
        self.addCleanup(inert.close)
        with self.assertRaises(ApplicabilityAdmissionError):
            inert.seal(make_unsigned_approval())

    def test_n20_unreserved_runner_entry_rejected(self):
        self._admit()
        self.store.append_evidence(self.evidence)
        self.gate.accept(self.evidence, self.receipt)  # nonce never reserved
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge()

    def test_n21_approval_release_commit_swap_rejected(self):
        # Validly sealed and admitted on a fresh ledger with a valid reserved
        # and gate-accepted entry, but bound to another tagged release than
        # the case pin.
        self._record()
        other = self._fresh_verifier()
        swapped = other.seal(make_unsigned_approval(release_commit="4"*40))
        other.admit(swapped)
        nonce = other.reserve_execution(case_id=self.case["case_id"], scope=self.scope)
        receipt = make_runner_receipt(self.evidence, nonce=nonce)
        self.gate.accept(self.evidence, receipt)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(applicability=swapped, applicability_verifier=other,
                         receipt=receipt)

    def test_n22_approval_source_revision_swap_rejected(self):
        self._record()
        other = self._fresh_verifier()
        swapped = other.seal(make_unsigned_approval(source_revision="other-branch"))
        other.admit(swapped)
        nonce = other.reserve_execution(case_id=self.case["case_id"], scope=self.scope)
        receipt = make_runner_receipt(self.evidence, nonce=nonce)
        self.gate.accept(self.evidence, receipt)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(applicability=swapped, applicability_verifier=other,
                         receipt=receipt)

    def test_n23_approval_claim_scope_swap_rejected(self):
        self._record()
        other = self._fresh_verifier()
        swapped = other.seal(make_unsigned_approval(claim_scope="8"*64))
        other.admit(swapped)
        nonce = other.reserve_execution(case_id=self.case["case_id"], scope=self.scope)
        receipt = make_runner_receipt(self.evidence, nonce=nonce)
        self.gate.accept(self.evidence, receipt)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge(applicability=swapped, applicability_verifier=other,
                         receipt=receipt)

    def test_n24_reservation_scope_binding_mismatch_rejected(self):
        # A receipt nonce reserved against a DIFFERENT frozen scope must not
        # admit this execution (R24 P1-01 reservation binding).
        self._admit()
        wrong_scope = FrozenExecutionScope(source_sha256=SOURCE, target_sha256="0"*64,
                                           plan_sha256=PLAN, fixture_sha256=FIXTURE,
                                           relation="DIVERGED")
        nonce = self.verifier.reserve_execution(case_id=self.case["case_id"],
                                                scope=wrong_scope)
        self.receipt = make_runner_receipt(self.evidence, nonce=nonce)
        self.store.append_evidence(self.evidence)
        self.gate.accept(self.evidence, self.receipt)
        with self.assertRaises(MLAEvidenceBlocked):
            self._bridge()

    def test_n25_runtime_root_pin_bootstrap_removed(self):
        # R24 P1-02: no runtime first-writer pin API exists; with the shipped
        # reviewed-source constant restored, every provisioning key (including
        # the synthetic dev root) fails closed until a reviewed deployment
        # commit replaces the fingerprint.
        self._record()
        self.assertFalse(hasattr(applicability, "pin_authority_root"))
        self.assertFalse(hasattr(applicability, "_ROOT_PIN"))
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        with mock.patch.object(applicability, "AUTHORITY_ROOT_FINGERPRINT_SHA256",
                               SHIPPED_PIN):
            for key in (AUTHORITY_ROOT_KEY, IMPOSTOR_KEY):
                with self.assertRaises(ApplicabilityAdmissionError):
                    ApplicabilityVerifier.provision(
                        root_key=key, authority_id=AUTHORITY_ID,
                        approval_db=Path(tmp.name)/"p.sqlite")


if __name__=="__main__":
    unittest.main()
