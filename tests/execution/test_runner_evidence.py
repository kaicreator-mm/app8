"""Runner-produced Evidence chain: sign -> ingress -> readiness, plus forgery negatives."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from app8.evidence.attestation import AttestationError, AttestationGate
from app8.evidence.ingress import import_signed_observation
from app8.execution.docker_runner import RealDockerRunner, RunnerBlocked, freeze_execution_plan
from app8.readiness import evaluate_readiness
from app8.storage import EvidenceStore

from test_docker_runner import (
    FAKE_DOCKER,
    IMAGE,
    IMAGE_DIGEST,
    KEY,
    POLICY,
    RunnerCase,
)


def _canonical(doc):
    return (json.dumps(doc, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


SOURCE = {"repository": "kaicreator-mm/app8", "revision": "test-pin", "content_sha256": "d" * 64}
FIXTURE = {"content_sha256": "e" * 64, "input_description": "no stdin",
           "reset_procedure": "tmpfs-only ephemeral container"}
BINDING = "binding:real-runner-test"


class ChainCase(RunnerCase):
    def setUp(self):
        super().setUp()
        root = Path(self.tmp.name)
        self.store = EvidenceStore(root / "store")
        self.addCleanup(self.store.close)
        self.gate = AttestationGate(verification_key=KEY, runner_id="test-runner",
                                    policy_sha256=POLICY, image_sha256=IMAGE_DIGEST,
                                    nonce_db=root / "nonces.sqlite3")
        self.addCleanup(self.gate.close)

    def target(self):
        return {"identity": IMAGE, "package_sha256": IMAGE_DIGEST,
                "environment_id": "test-env", "mapping_relation": "SAME"}

    def run_case(self, mode, assertions, wall=10, cap=65536):
        plan = freeze_execution_plan(BINDING, assertions, self.req(wall=wall, cap=cap))
        env = {**self.env, "FAKE_RUN_MODE": mode}
        with mock.patch.dict(os.environ, env):
            return self.runner().execute_attest(
                self.req(wall=wall, cap=cap), claim_id="claim:smoke",
                capability_id="cap:real-runner-smoke", source=SOURCE,
                target=self.target(), fixture=FIXTURE, plan=plan)

    def capability(self, evidence):
        return {"capability_id": "cap:real-runner-smoke", "source": evidence["source"],
                "target": evidence["target"], "bindings": [{"binding_id": BINDING}],
                "evidence_refs": [evidence["evidence_id"]],
                "readiness": {"lifecycle_state": "EXPORT_READY", "export_ready": True,
                              "derived_by_policy": True, "policy_revision": "caller",
                              "reason_codes": ["CALLER_CLAIM"]}}


class SigningChainTests(ChainCase):
    def test_real_run_signed_ingested_and_artifact_verified(self):
        receipt = self.run_case("ok", ["exit_code==0", "stdout_contains:app8-ok"])
        ev, att = receipt.evidence, receipt.attestation
        self.assertEqual(ev["assessment"]["verdict"], "SUPPORTED")
        result = import_signed_observation(self.store, self.gate, ev, att)
        self.assertFalse(result.capability_export_ready)
        stored = self.store.get_evidence(ev["evidence_id"])
        self.assertEqual(stored, ev)
        self.assertEqual(self.store.put_artifact(receipt.stdout),
                         ev["observation"]["stdout_sha256"])
        history = self.store.history(ev["evidence_id"])
        self.assertEqual(history[0]["kind"], "RUNNER_RECEIPT_AUTHENTICATED")

    def test_scoped_export_ready_only_with_gate_and_projection(self):
        receipt = self.run_case("ok", ["exit_code==0"])
        ev, att = receipt.evidence, receipt.attestation
        import_signed_observation(self.store, self.gate, ev, att)
        cap = self.capability(ev)
        ready = evaluate_readiness(cap, [ev], projection_verifier=lambda _: True,
                                   attestation_gate=self.gate,
                                   signed_attestations={ev["evidence_id"]: att})
        self.assertEqual(ready.lifecycle_state, "EXPORT_READY")
        self.assertTrue(ready.export_ready)

    def test_unauthorized_export_ready_denied(self):
        receipt = self.run_case("ok", ["exit_code==0"])
        ev, att = receipt.evidence, receipt.attestation
        import_signed_observation(self.store, self.gate, ev, att)
        cap = self.capability(ev)  # caller-claimed export_ready=True is noise
        bare = evaluate_readiness(cap, [ev], projection_verifier=lambda _: True)
        self.assertFalse(bare.export_ready)
        self.assertIn("UNAUTHENTICATED_EXECUTION_EVIDENCE", bare.reason_codes)
        no_projection = evaluate_readiness(
            cap, [ev], attestation_gate=self.gate,
            signed_attestations={ev["evidence_id"]: att})
        self.assertEqual(no_projection.lifecycle_state, "EVIDENCED")
        self.assertFalse(no_projection.export_ready)

    def test_tampered_evidence_rejected_and_never_ready(self):
        receipt = self.run_case("ok", ["exit_code==0"])
        ev, att = receipt.evidence, receipt.attestation
        import_signed_observation(self.store, self.gate, ev, att)
        tampered = json.loads(json.dumps(ev))
        tampered["observation"]["stdout_sha256"] = "1" * 64
        with self.assertRaises(AttestationError):
            import_signed_observation(self.store, self.gate, tampered, att)
        ready = evaluate_readiness(self.capability(tampered), [tampered],
                                   projection_verifier=lambda _: True,
                                   attestation_gate=self.gate,
                                   signed_attestations={tampered["evidence_id"]: att})
        self.assertFalse(ready.export_ready)

    def test_replay_rejected(self):
        receipt = self.run_case("ok", ["exit_code==0"])
        import_signed_observation(self.store, self.gate, receipt.evidence, receipt.attestation)
        with self.assertRaises(AttestationError):
            import_signed_observation(self.store, self.gate, receipt.evidence, receipt.attestation)

    def test_forged_mac_rejected(self):
        receipt = self.run_case("ok", ["exit_code==0"])
        forged = dict(receipt.attestation, mac_sha256="f" * 64)
        with self.assertRaises(AttestationError):
            import_signed_observation(self.store, self.gate, receipt.evidence, forged)

    def test_wrong_verification_key_rejected(self):
        receipt = self.run_case("ok", ["exit_code==0"])
        evil = AttestationGate(verification_key=b"x" * 32, runner_id="test-runner",
                               policy_sha256=POLICY, image_sha256=IMAGE_DIGEST,
                               nonce_db=Path(self.tmp.name) / "evil.sqlite3")
        self.addCleanup(evil.close)
        with self.assertRaises(AttestationError):
            import_signed_observation(self.store, evil, receipt.evidence, receipt.attestation)

    def test_model_self_certification_rejected_even_with_valid_mac(self):
        from app8.contracts import ContractError
        receipt = self.run_case("ok", ["exit_code==0"])
        ev = json.loads(json.dumps(receipt.evidence))
        ev["assessment"]["assessor_kind"] = "MODEL_PROPOSAL_ONLY"
        att = {"schema_version": "app8-attested-evidence-v2",
               "evidence_sha256": hashlib.sha256(_canonical(ev)).hexdigest(),
               "runner_id": "test-runner", "policy_sha256": POLICY,
               "image_sha256": IMAGE_DIGEST, "nonce": "0" * 32}
        att["mac_sha256"] = hmac.new(KEY, _canonical(att), hashlib.sha256).hexdigest()
        with self.assertRaises(ContractError):  # schema ingress fires first
            import_signed_observation(self.store, self.gate, ev, att)
        ev["assessment"]["verdict"] = "REFUTED"  # passes schema; gate must still refuse
        att["evidence_sha256"] = hashlib.sha256(_canonical(ev)).hexdigest()
        att["mac_sha256"] = hmac.new(KEY, _canonical(att), hashlib.sha256).hexdigest()
        with self.assertRaises(AttestationError):
            import_signed_observation(self.store, self.gate, ev, att)

    def test_refuted_is_signed_honestly_but_never_qualifies(self):
        receipt = self.run_case("exit3", ["exit_code==0"])
        ev, att = receipt.evidence, receipt.attestation
        self.assertEqual(ev["assessment"]["verdict"], "REFUTED")
        self.assertIn("FAILED:exit_code==0", ev["assessment"]["reason_codes"])
        import_signed_observation(self.store, self.gate, ev, att)  # refutation preserved
        ready = evaluate_readiness(self.capability(ev), [ev],
                                   projection_verifier=lambda _: True,
                                   attestation_gate=self.gate,
                                   signed_attestations={ev["evidence_id"]: att})
        self.assertFalse(ready.export_ready)

    def test_wall_limit_evidence_carries_enforcement(self):
        receipt = self.run_case("sleep", ["exit_code==0"], wall=1)
        ev = receipt.evidence
        self.assertEqual(ev["assessment"]["verdict"], "BLOCKED")
        self.assertIn("EXECUTION_INCOMPLETE", ev["assessment"]["reason_codes"])
        self.assertIn("WALL_LIMIT_ENFORCED", ev["assessment"]["reason_codes"])
        self.assertIsInstance(ev["observation"]["exit_code"], int)
        import_signed_observation(self.store, self.gate, ev, receipt.attestation)

    def test_mutated_plan_sha256_blocked_before_any_spawn(self):
        plan = freeze_execution_plan(BINDING, ["exit_code==0"], self.req())
        plan["plan_sha256"] = "f" * 64
        with mock.patch.dict(os.environ, self.env):
            with self.assertRaisesRegex(RunnerBlocked, "FROZEN_PLAN_REQUEST_HASH_MISMATCH"):
                self.runner().execute_attest(
                    self.req(), claim_id="claim:x", capability_id="cap:real-runner-smoke",
                    source=SOURCE, target=self.target(), fixture=FIXTURE, plan=plan)
        self.assertEqual(self.ps_ids(), [])

    def test_stale_plan_changed_args_blocked_before_spawn(self):
        plan = freeze_execution_plan(BINDING, ["exit_code==0"], self.req(args=("-V",)))
        with mock.patch.dict(os.environ, self.env):
            with self.assertRaisesRegex(RunnerBlocked, "FROZEN_PLAN_REQUEST_HASH_MISMATCH"):
                self.runner().execute_attest(
                    self.req(args=("-c", "print('different')")),
                    claim_id="claim:x", capability_id="cap:real-runner-smoke",
                    source=SOURCE, target=self.target(), fixture=FIXTURE, plan=plan)
        self.assertEqual(self.ps_ids(), [])

    def test_limit_aborted_matching_exit_never_supports_claim(self):
        receipt = self.run_case("sleep", ["exit_code==137"], wall=1)
        ev = receipt.evidence
        self.assertEqual(ev["assessment"]["verdict"], "BLOCKED")
        self.assertIn("EXECUTION_INCOMPLETE", ev["assessment"]["reason_codes"])
        import_signed_observation(self.store, self.gate, ev, receipt.attestation)
        ready = evaluate_readiness(
            self.capability(ev), [ev], projection_verifier=lambda _: True,
            attestation_gate=self.gate,
            signed_attestations={ev["evidence_id"]: receipt.attestation})
        self.assertFalse(ready.export_ready)

    def test_runner_never_signs_unallowlisted(self):
        plan = freeze_execution_plan(BINDING, ["exit_code==0"], self.req())
        with mock.patch.dict(os.environ, self.env):
            with self.assertRaises(RunnerBlocked):
                self.runner().execute_attest(
                    self.req(command="/bin/ls"), claim_id="claim:x",
                    capability_id="cap:real-runner-smoke", source=SOURCE,
                    target=self.target(), fixture=FIXTURE, plan=plan)
        self.assertEqual(self.ps_ids(), [])

    def test_environment_mismatch_never_signed(self):
        plan = freeze_execution_plan(BINDING, ["exit_code==0"], self.req())
        target = {**self.target(), "environment_id": "someone-else"}
        with mock.patch.dict(os.environ, self.env):
            with self.assertRaises(RunnerBlocked):
                self.runner().execute_attest(
                    self.req(), claim_id="claim:x", capability_id="cap:real-runner-smoke",
                    source=SOURCE, target=target, fixture=FIXTURE, plan=plan)

    def test_unknown_assertion_blocked_before_any_execution(self):
        plan = freeze_execution_plan(BINDING, ["trust_me_bro"], self.req())
        with mock.patch.dict(os.environ, self.env):
            with self.assertRaises(RunnerBlocked):
                self.runner().execute_attest(
                    self.req(), claim_id="claim:x", capability_id="cap:real-runner-smoke",
                    source=SOURCE, target=self.target(), fixture=FIXTURE, plan=plan)
        self.assertEqual(self.ps_ids(), [])


if __name__ == "__main__":
    unittest.main()
