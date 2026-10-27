"""CC03 CLI bridge unit tests. Synthetic qualifier and runner receipts, NOT real Host."""
import hashlib
import hmac
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app8.cli.consumer import run_agent_cli, AgentConsumerBlocked
from app8.evidence.attestation import AttestationGate
from app8.evidence.ingress import import_signed_observation
from app8.execution.docker_policy import ContainerRequest
from app8.execution.docker_runner import RealDockerRunner, RunnerConfig, RunnerObservation, freeze_execution_plan
from app8.qualification.service import Qualification
from app8.readiness.policy import Readiness
from app8.storage import EvidenceStore

SHA = "a" * 64
IMAGE = "registry.example/fixtures@sha256:" + SHA


def cap():
    return {
        "capability_id": "cap:ffmpeg-inspect",
        "revision": 1,
        "source": {"content_sha256": "f" * 64},
        "target": {"identity": IMAGE, "package_sha256": SHA,
                   "environment_id": "fixture-env"},
        "bindings": [{"binding_id": "binding:ffmpeg", "kind": "CLI",
                      "address": "/usr/bin/ffmpeg", "side_effects": []}],
    }


def qualifier(ready=True):
    rd = Readiness("EXPORT_READY" if ready else "HYPOTHESIZED",
                   ready, (), ("ev:1",) if ready else ())
    return Qualification("SCOPED_EXPORT_READY" if ready else "UNREADY",
                         rd, "b" * 64, 1, {})


def observed():
    return RunnerObservation(
        "EXECUTED", 0, b"ok", b"", False, False,
        5, "c" * 64, SHA, "d" * 64,
        "fixture-version", True,
    )


class ConsumerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = EvidenceStore(Path(self.temp.name) / "evidence")
        self.addCleanup(self.store.close)
        self.gate = AttestationGate(
            verification_key=b"synthetic-test-key-only".ljust(32, b"x"),
            runner_id="fixture-runner", policy_sha256="a" * 64,
            image_sha256=SHA, nonce_db=Path(self.temp.name) / "nonces.db")
        self.addCleanup(self.gate.close)
        conf = RunnerConfig(
            runner_id="fixture-runner", policy_sha256="a" * 64,
            client_argv_head=("/nonexistent/docker",),
            environment_id="fixture-env",
            allowlist=frozenset({(IMAGE, "/usr/bin/ffmpeg")}),
        )
        self.runner = RealDockerRunner(conf, signing_key=b"k" * 32)
        self.approved_plan = freeze_execution_plan(
            "binding:ffmpeg", ["exit_code==0"],
            ContainerRequest(image_ref=IMAGE, command="/usr/bin/ffmpeg",
                             args=("-version",), docker_cli_sha256="f" * 64),
        )

    def run_case(self, doc=None, *, session="task-A", binding="binding:ffmpeg",
                 args=("-version",), plan=None):
        # Real qualification authenticates the complete stored ledger. The
        # isolated unit tests mock qualification and its accepted plan only.
        record = {"plan": self.approved_plan if plan is None else plan,
                  "assessment": {"verdict": "SUPPORTED"}}
        with patch.object(self.store, "list_evidence_for_capability", return_value=[record]):
            return run_agent_cli(
                cap() if doc is None else doc,
                store=self.store, gate=self.gate, signed_attestations={},
                runner=self.runner, binding_id=binding, docker_cli_sha256="f" * 64,
                args=args, session_id=session,
            )

    def test_scoped_tool_invocation_and_existing_store_event(self):
        with patch("app8.cli.consumer.qualify_stored_capability", return_value=qualifier()), \
             patch.object(self.runner, "execute", return_value=observed()) as exec_run:
            result = self.run_case()
        exec_run.assert_called_once()
        req = exec_run.call_args.args[0]
        self.assertEqual(req.command, "/usr/bin/ffmpeg")
        self.assertEqual(req.image_ref, IMAGE)
        self.assertEqual(req.args, ("-version",))
        self.assertEqual(result.execution_status, "EXECUTED")
        self.assertEqual(result.session_id, "task-A")
        self.assertEqual(result.evidence_snapshot_sha256, "b" * 64)
        self.assertEqual(result.stdout_base64, "b2s=")
        self.assertEqual(result.stderr_base64, "")
        self.assertFalse(result.stdout_truncated)
        self.assertFalse(result.stderr_truncated)
        history = self.store.history("cap:ffmpeg-inspect")
        self.assertNotEqual(history, [])
        self.assertNotIn("stdout_base64", str(history))
        self.assertNotIn("stderr_base64", str(history))

    def test_two_session_reuse_preserves_identity_without_recompilation(self):
        """Synthetic caller sessions only; real Agent provenance is CC04."""
        with patch("app8.cli.consumer.qualify_stored_capability", return_value=qualifier()) as qualify, \
             patch.object(self.runner, "execute", return_value=observed()) as run:
            first = self.run_case(session="agent-task-001")
            second = self.run_case(session="agent-task-002")
        self.assertEqual(qualify.call_count, 2)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(first.capability_id, second.capability_id)
        self.assertEqual(first.evidence_snapshot_sha256, second.evidence_snapshot_sha256)
        self.assertNotEqual(first.session_id, second.session_id)
        self.assertEqual(len(self.store.history(first.capability_id)), 2)

    def test_not_ready_does_not_execute(self):
        with patch("app8.cli.consumer.qualify_stored_capability", return_value=qualifier(False)), \
             patch.object(self.runner, "execute") as exec_run:
            with self.assertRaises(AgentConsumerBlocked):
                self.run_case()
        exec_run.assert_not_called()

    def test_wrong_binding_rejected(self):
        with patch("app8.cli.consumer.qualify_stored_capability", return_value=qualifier()), \
             patch.object(self.runner, "execute") as exec_run:
            with self.assertRaises(AgentConsumerBlocked):
                self.run_case(binding="binding:other")
        exec_run.assert_not_called()

    def test_wrong_image_digest_or_environment_rejected(self):
        for kind in ("target", "environment"):
            document = cap()
            if kind == "target":
                document["target"]["package_sha256"] = "c" * 64
            else:
                document["target"]["environment_id"] = "wrong-env"
            with patch("app8.cli.consumer.qualify_stored_capability", return_value=qualifier()), \
                 patch.object(self.runner, "execute") as exec_run:
                with self.assertRaises(AgentConsumerBlocked):
                    self.run_case(document)
            exec_run.assert_not_called()

    def test_side_effect_binding_rejected(self):
        document = cap()
        document["bindings"][0]["side_effects"] = ["writes to host"]
        with patch("app8.cli.consumer.qualify_stored_capability", return_value=qualifier()), \
             patch.object(self.runner, "execute") as exec_run:
            with self.assertRaises(AgentConsumerBlocked):
                self.run_case(document)
        exec_run.assert_not_called()

    def test_unobserved_cli_args_do_not_inherit_observed_readiness(self):
        with patch("app8.cli.consumer.qualify_stored_capability", return_value=qualifier()), \
             patch.object(self.runner, "execute") as exec_run:
            with self.assertRaisesRegex(AgentConsumerBlocked, "signed, scoped"):
                self.run_case(args=("-hide_banner", "-version"))
        exec_run.assert_not_called()

    def test_tampered_frozen_plan_does_not_authorize_cli(self):
        plan = {**self.approved_plan, "plan_sha256": "0" * 64}
        with patch("app8.cli.consumer.qualify_stored_capability", return_value=qualifier()), \
             patch.object(self.runner, "execute") as exec_run:
            with self.assertRaisesRegex(AgentConsumerBlocked, "signed, scoped"):
                self.run_case(plan=plan)
        exec_run.assert_not_called()

    def test_genuine_accepted_ledger_runs_two_scoped_reuses(self):
        """Exercise REAL local HMAC acceptance + complete ledger, mock Docker only.

        This never claims real Docker or an independently authenticated Agent.
        Unlike other CC03 tests, qualification is NOT patched.
        """
        source = {"repository": "FFmpeg/FFmpeg", "revision": "pinned-unit-source",
                  "content_sha256": "f" * 64, "license_disposition": "REVIEWED_COMPATIBLE"}
        target = {**cap()["target"], "mapping_relation": "SAME"}
        binding = {**cap()["bindings"][0], "preconditions": []}
        capability = {
            "schema_version": "app8-capability-v1",
            "capability_id": "cap:ffmpeg-inspect", "revision": 1,
            "semantic": {
                "name": "Read FFmpeg version", "purpose": "Inspect pinned runtime",
                "user_job": "Read a pinned tool version without side effects",
                "inputs": ["version argument"], "outputs": ["version text"],
                "variants": [], "constraints": ["exact frozen argv"],
                "negative_boundaries": ["different argv not admitted"],
                "failure_modes": ["runtime unavailable"], "side_effects": [],
            },
            "source": source, "target": target, "bindings": [binding],
            "evidence_refs": ["ev:cc03-real-ledger-fixture"],
            "readiness": {
                "lifecycle_state": "HYPOTHESIZED", "export_ready": False,
                "derived_by_policy": True, "policy_revision": "unit-synthetic",
                "reason_codes": ["NOT_YET_DERIVED"],
            }, "projection_refs": [],
        }
        record_plan = {
            key: value for key, value in self.approved_plan.items()
            if key != "request_sha256"
        }
        ev = {
            "schema_version": "app8-evidence-v1",
            "evidence_id": "ev:cc03-real-ledger-fixture",
            "claim_id": "claim:ffmpeg-version", "capability_id": capability["capability_id"],
            "source": {k: source[k] for k in ("repository", "revision", "content_sha256")},
            "target": target,
            "fixture": {"content_sha256": "0" * 64,
                        "input_description": "fixed -version",
                        "reset_procedure": "synthetic unit fixture"},
            "plan": record_plan,
            "observation": {
                "observer": "DETERMINISTIC_EXECUTION_ADAPTER",
                "execution_status": "EXECUTED",
                "invocation_sha256": "c" * 64, "exit_code": 0,
                "stdout_sha256": hashlib.sha256(b"ok").hexdigest(),
                "stderr_sha256": hashlib.sha256(b"").hexdigest(),
                "artifacts": [], "recorded_at": "2026-10-27T00:00:00Z",
            },
            "assessment": {
                "verdict": "SUPPORTED",
                "assessor_kind": "DETERMINISTIC_ASSERTION_ENGINE",
                "reason_codes": ["ASSERTIONS_PASSED"],
            },
            "replay": {"manifest_sha256": "d" * 64,
                       "artifact_location": "LOCAL_CONTENT_ADDRESSED"},
        }

        def canonical(x):
            return (json.dumps(x, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False) + "\\n").encode("utf-8")

        att = {
            "schema_version": "app8-attested-evidence-v2",
            "evidence_sha256": hashlib.sha256(canonical(ev)).hexdigest(),
            "runner_id": "fixture-runner", "policy_sha256": "a" * 64,
            "image_sha256": SHA, "nonce": "1" * 32,
        }
        att["mac_sha256"] = hmac.new(
            b"synthetic-test-key-only".ljust(32, b"x"),
            canonical(att), hashlib.sha256,
        ).hexdigest()
        import_signed_observation(self.store, self.gate, ev, att)
        kwargs = dict(store=self.store, gate=self.gate,
                      signed_attestations={ev["evidence_id"]: att},
                      runner=self.runner, binding_id="binding:ffmpeg",
                      docker_cli_sha256="f" * 64, args=("-version",))
        with patch.object(self.runner, "execute", return_value=observed()) as execute:
            first = run_agent_cli(capability, session_id="fixture-task-A", **kwargs)
            second = run_agent_cli(capability, session_id="fixture-task-B", **kwargs)
            self.assertEqual(execute.call_count, 2)
            self.assertEqual(first.evidence_snapshot_sha256,
                             second.evidence_snapshot_sha256)
            self.assertEqual(first.stdout_base64, "b2s=")
            self.assertEqual(second.stdout_base64, "b2s=")
            self.assertNotEqual(first.session_id, second.session_id)

        self.store.append_event(capability["capability_id"], "STALE",
                                {"reason": "synthetic drift veto"})
        with patch.object(self.runner, "execute") as denied:
            with self.assertRaises(AgentConsumerBlocked):
                run_agent_cli(capability, session_id="fixture-task-C", **kwargs)
        denied.assert_not_called()

    def test_wrong_trust_objects_and_unbounded_session_fail(self):
        with self.assertRaises(AgentConsumerBlocked):
            run_agent_cli(cap(), store=None, gate=self.gate,
                          signed_attestations={}, runner=self.runner,
                          binding_id="binding:ffmpeg", docker_cli_sha256=SHA,
                          args=(), session_id="task-A")
        with self.assertRaises(AgentConsumerBlocked):
            self.run_case(session="task name with whitespace")


if __name__ == "__main__":
    unittest.main()
