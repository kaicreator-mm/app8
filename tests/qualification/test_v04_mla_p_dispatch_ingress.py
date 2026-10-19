"""No-network P transport+compiler orchestration tests, never live evidence."""
import hashlib
import json
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from app8.mla.ordered_host_ledger import OrderedMLAHostLedger
from app8.storage import EvidenceStore
from scripts.v04_mla_pilot_reducer import ALLOWLIST, ROOT, PilotBlocked
from scripts.v04_mla_p_dispatch_ingress import dispatch_and_ingest_p
# Local synthetic fixtures: tests/ may not be importable as an installed package.
ORIGINS = {"https://example-model-provider.com"}


def profile():
    return {
        "origin": "https://example-model-provider.com",
        "path": "/v1/chat/completions",
        "provider": "synthetic", "model_family": "synthetic-p",
        "model_id": "test-model",
        "api_key_env": "APP8_MLA_PROVIDER_TEST",
        "billing_currency": "USD",
        "input_cost_microunits_per_million_tokens": 1_000_000,
        "output_cost_microunits_per_million_tokens": 1_000_000,
    }


def request():
    return b'{"model":"test-model","messages":[{"role":"user","content":"fixture"}]}'



class SealedPIngressTests(TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.ledger = OrderedMLAHostLedger(
            Path(tmp.name) / "ledger.sqlite",
            host_hmac_key=b"no-network-synthetic-integration-test-key" * 2)
        self.addCleanup(self.ledger.close)
        self.store = EvidenceStore(Path(tmp.name) / "sealed")
        self.addCleanup(self.store.close)
        allowlist = json.loads((ROOT / ALLOWLIST).read_text(encoding="utf-8"))
        selected = sorted(allowlist["assets"]["FFmpeg"].items())[:6]
        self.slots = [{
            "case_id": f"V04-FFMPEG-{i:03d}",
            "source_anchor": {"path": path, "blob": blob}
        } for i, (path, blob) in enumerate(selected, 1)]
        self.source = b"synthetic source-only context"
        self.source_sha = hashlib.sha256(self.source).hexdigest()
        self.batch = {
            "schema_version": "v04-mla-role-batch-v1",
            "study_id": "V04-MLA-1", "asset": "FFmpeg", "role": "P",
            "source_context_sha256": self.source_sha,
            "cases": [{
                "case_id": s["case_id"],
                "source_anchor": s["source_anchor"],
                "origin": "LLM_PROPOSED",
                "kind": "P_CAPABILITY_PREDICTION",
                "proposal": "synthetic possible capability",
                "constraints": ["not measured"],
            } for s in self.slots],
        }

    def run_mocked(self, *, content_override=None):
        output = (json.dumps(self.batch, sort_keys=True) if content_override is None
                  else content_override)
        wire = json.dumps({
            "model": "test-model",
            "choices": [{
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": output}
            }],
            "usage": {"prompt_tokens": 1, "completion_tokens": 2}
        }).encode()
        response_sha = self.store.put_artifact(wire)
        from app8.mla.trusted_provider_dispatch import frozen_invocation_digest
        digest = frozen_invocation_digest(profile(), request(), approved_origins=ORIGINS)
        reference = {
            "schema_version": "v04-mla-https-dispatch-private-ref-v1",
            "role": "P", "asset": "FFmpeg",
            "request_envelope_sha256": digest,
            "response_sha256": response_sha,
            "response_event_mac": "synthetic-not-a-real-event"
        }
        with patch("scripts.v04_mla_p_dispatch_ingress.dispatch_frozen_completion",
                   return_value=reference) as dispatch:
            result = dispatch_and_ingest_p(
                ledger=self.ledger, sealed_store=self.store,
                asset="FFmpeg", profile=profile(), request_bytes=request(),
                approved_origins=ORIGINS, source_context_bytes=self.source,
                source_context_sha256=self.source_sha,
                frozen_slots=self.slots)
        return result, dispatch

    def test_sealed_provider_response_flows_to_real_app8_compiler(self):
        result, call = self.run_mocked()
        self.assertEqual(result["status"], "HOST_P_RESPONSE_COMPILED_MODEL_PROPOSAL_ONLY")
        self.assertEqual(len(result["app8_frozen_hypotheses_sha256"]), 64)
        self.assertEqual(call.call_args.kwargs["role"], "P")
        self.assertFalse(result["independent_remote_model_identity_verified"])
        self.assertFalse(result["formal_product_release_qualified"])

    def test_preflight_source_mismatch_no_provider_dispatch(self):
        with patch("scripts.v04_mla_p_dispatch_ingress.dispatch_frozen_completion") as mock:
            with self.assertRaisesRegex(PilotBlocked, "byte-bound"):
                dispatch_and_ingest_p(
                    ledger=self.ledger, sealed_store=self.store,
                    asset="FFmpeg", profile=profile(), request_bytes=request(),
                    approved_origins=ORIGINS, source_context_bytes=self.source + b"changed",
                    source_context_sha256=self.source_sha,
                    frozen_slots=self.slots)
        mock.assert_not_called()

    def test_non_json_candidate_rejected_without_gold_promotion(self):
        with self.assertRaises(PilotBlocked):
            self.run_mocked(content_override="not a candidate JSON document")

    def test_synthetic_test_still_has_no_actual_host_event_authority(self):
        result, _ = self.run_mocked()
        self.assertEqual(result["host_recorded_dispatch_event_mac"],
                         "synthetic-not-a-real-event")
        self.assertFalse(result["capability_promotion_allowed"])
