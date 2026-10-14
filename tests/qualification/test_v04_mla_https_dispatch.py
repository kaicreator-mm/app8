"""No-network provider adapter tests, all transport bytes are synthetic."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app8.mla.ordered_host_ledger import OrderedMLAHostLedger, MLAChronologyBlocked
from app8.mla.trusted_provider_dispatch import (
    ProviderDispatchBlocked, TrustedHTTPSCompletionClient,
    frozen_invocation_digest, dispatch_frozen_completion
)
from app8.storage import EvidenceStore

KEY = b"fake-privileged-ledger-key-for-tests" * 2
ORIGINS = {"https://example-model-provider.com"}


def profile():
    return {
        "origin": "https://example-model-provider.com",
        "path": "/v1/chat/completions",
        "provider": "synthetic",
        "model_family": "test-family",
        "model_id": "test-model",
        "api_key_env": "APP8_MLA_PROVIDER_TEST",
        "billing_currency": "USD",
        "input_cost_microunits_per_million_tokens": 1_000_000,
        "output_cost_microunits_per_million_tokens": 2_000_000,
    }


def request():
    return b'{"model":"test-model","messages":[{"role":"user","content":"fixture task"}]}'


def reply(model="test-model", output="synthetic only", finish="stop"):
    return json.dumps({
        "model": model,
        "choices": [{"finish_reason": finish,
                     "message": {"role": "assistant", "content": output}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 150},
    }).encode()


class FakeTransport:
    def __init__(self, data=None):
        self.data = reply() if data is None else data
        self.called = 0

    def send(self, url, body, key, timeout):
        self.called += 1
        assert key == "test-only-secret"
        assert url == "https://example-model-provider.com/v1/chat/completions"
        return self.data


def freeze(req_sha):
    d = {
        "schema_version": "v04-mla-privileged-invocation-freeze-v1",
        "study_id": "V04-MLA-1",
        "source_pack_git_blob": "4b3c9b62b1899653524f19a286924f942605210a",
        "protocol_sha256": "a" * 64, "scorer_sha256": "b" * 64,
        "cohort_sha256": "c" * 64, "case_job_sha256": "d" * 64,
        "campaign_nonce": "1" * 64, "human_selection_seed_sha256": "2" * 64,
        "source_selection_seed_sha256": "3" * 64,
        "r2_verdict_comment_id": 6172212383,
        "model_input_sha256": {asset: {
            role: req_sha for role in ("P", "R", "X")}
            for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice")},
        "eligible_j_case_ids": [],
        "budget": {
            "billing_currency": "USD",
            "max_total_input_tokens": 2_000_000,
            "max_total_output_tokens": 2_000_000,
            "max_total_cost_microunits": 4_000_000,
            "max_total_wall_ms": 1_000_000,
            "max_per_call_input_tokens": 100_000,
            "max_per_call_output_tokens": 100_000,
            "max_per_call_cost_microunits": 200_000,
            "max_per_call_wall_ms": 120_000,
        },
    }
    return d


class HTTPSDispatchTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.ledger = OrderedMLAHostLedger(root/"freeze.sqlite", host_hmac_key=KEY)
        self.addCleanup(self.ledger.close)
        self.store = EvidenceStore(root/"sealed")
        self.addCleanup(self.store.close)
        self.p = profile()
        self.req = request()
        self.digest = frozen_invocation_digest(self.p, self.req,
                                               approved_origins=ORIGINS)
        self.ledger.freeze(freeze(self.digest))
        self.secrets = patch.dict(os.environ, {"APP8_MLA_PROVIDER_TEST": "test-only-secret"})
        self.secrets.start()
        self.addCleanup(self.secrets.stop)

    def dispatch(self, **opts):
        simulated_https = opts.pop("transport", FakeTransport())
        args = dict(ledger=self.ledger, sealed_store=self.store,
                    role="P", asset="FFmpeg", profile=self.p,
                    request_bytes=self.req, approved_origins=ORIGINS)
        args.update(opts)
        # Isolated no-network patch, NOT an injectable production argument.
        with patch.object(TrustedHTTPSCompletionClient, "send", autospec=True,
                          side_effect=lambda _self, url, body, key, timeout:
                              simulated_https.send(url, body, key, timeout)):
            return dispatch_frozen_completion(**args)

    def test_production_api_has_no_transport_injection_argument(self):
        self.assertNotIn("transport",
                         inspect.signature(dispatch_frozen_completion).parameters)

    def test_fake_response_is_stored_but_never_provider_attested(self):
        x = self.dispatch()
        self.assertEqual(x["status"],
                         "HOST_TRANSPORT_RESULT_RECORDED_NOT_INDEPENDENTLY_ATTESTED")
        self.assertFalse(x["trusted_remote_provider_identity_independently_verified"])
        self.assertFalse(x["capability_promotion_allowed"])
        self.assertFalse(x["formal_product_release_qualified"])
        self.assertEqual(self.store.get_artifact(x["response_sha256"]), reply())
        self.assertEqual(self.ledger.audit()["reservation_count"], 1)

    def test_profile_change_after_freeze_blocked_before_transport(self):
        changed = dict(self.p, model_family="changed")
        client = FakeTransport()
        with self.assertRaisesRegex(MLAChronologyBlocked, "input mismatch"):
            self.dispatch(profile=changed, transport=client)
        self.assertEqual(client.called, 0)

    def test_request_bytes_change_after_freeze_blocked(self):
        with self.assertRaisesRegex(MLAChronologyBlocked, "input mismatch"):
            self.dispatch(request_bytes=self.req + b" ")

    def test_unapproved_origin_blocked_before_reservation(self):
        changed = dict(self.p, origin="https://127.0.0.1")
        with self.assertRaisesRegex(ProviderDispatchBlocked, "allowlisted"):
            self.dispatch(profile=changed)
        self.assertEqual(self.ledger.audit()["reservation_count"], 0)

    def test_spend_currency_mismatch_denied_before_transport(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            with OrderedMLAHostLedger(path / "currency-ledger.sqlite",
                                      host_hmac_key=KEY) as other:
                manifest = freeze(self.digest)
                manifest["budget"]["billing_currency"] = "EUR"
                other.freeze(manifest)
                fake = FakeTransport()
                with self.assertRaisesRegex(ProviderDispatchBlocked, "currency"):
                    self.dispatch(ledger=other, transport=fake)
                self.assertEqual(fake.called, 0)
                self.assertEqual(other.audit()["reservation_count"], 0)

    def test_redirect_url_paths_disallowed(self):
        changed = dict(self.p, path="/v1/../chat/completions")
        with self.assertRaisesRegex(ProviderDispatchBlocked, "API path"):
            self.dispatch(profile=changed)

    def test_missing_credential_blocked_before_reservation(self):
        with patch.dict(os.environ, {"APP8_MLA_PROVIDER_TEST": ""}):
            with self.assertRaisesRegex(ProviderDispatchBlocked, "credential"):
                self.dispatch()
        self.assertEqual(self.ledger.audit()["reservation_count"], 0)

    def test_truncated_model_response_blocks_subsequent_calls(self):
        with self.assertRaisesRegex(ProviderDispatchBlocked, "truncated"):
            self.dispatch(transport=FakeTransport(reply(finish="length")))
        self.assertEqual(self.ledger.audit()["reservation_count"], 1)
        with self.assertRaisesRegex(MLAChronologyBlocked, "outstanding"):
            self.ledger.reserve(role="P", asset="pandas", case_id=None,
                                request_sha256=self.digest)

    def test_wrong_model_response_fails_closed(self):
        with self.assertRaisesRegex(ProviderDispatchBlocked, "different-model"):
            self.dispatch(transport=FakeTransport(reply(model="surprise")))
        self.assertEqual(self.ledger.audit()["reservation_count"], 1)
        with self.assertRaisesRegex(MLAChronologyBlocked, "outstanding"):
            self.ledger.reserve(role="P", asset="pandas", case_id=None,
                                request_sha256=self.digest)

    def test_duplicate_real_invocation_denied(self):
        self.dispatch()
        with self.assertRaisesRegex(MLAChronologyBlocked, "replay"):
            self.dispatch()


if __name__ == "__main__":
    unittest.main()
