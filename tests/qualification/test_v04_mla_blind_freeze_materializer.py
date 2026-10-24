"""Pre-output blind-freeze materialization tests; no provider calls, no LLM.

Targeted positives/negatives for the exact-byte binding between the persisted
pre-output freeze record and `app8/mla/blind_capture.py::verify_blind_capture`
(issue #166 Step H3): the materialized role input envelopes must be the exact
bytes the verifier later demands, bound to the exact privileged request
digest computed by the production frozen-invocation digest.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from app8.mla.blind_capture import (
    INPUT_FIELDS, SOURCE_BLOB, VIS, BlindCaptureBlocked, verify_blind_capture,
)
from app8.mla.trusted_provider_dispatch import frozen_invocation_digest
from scripts.v04_mla_blind_freeze_materializer import (
    load_materialized_freeze, materialize_blind_freeze,
)
from scripts.v04_mla_pilot_reducer import PilotBlocked

SOURCE_CONTEXT = "1" * 64
ORIGIN = "https://api.example.com"
ROLES = ("P", "R", "X")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False) + "\n").encode("utf-8")


def profile_for(role: str, *, family=None, provider=None) -> dict:
    return {
        "origin": ORIGIN,
        "path": "/v1/chat/completions",
        "provider": provider or "example",
        "model_family": family or ("family-" + role),
        "model_id": "synthetic-model-" + role,
        "api_key_env": "APP8_MLA_PROVIDER_SYNTHETIC_" + role,
        "billing_currency": "USD",
        "input_cost_microunits_per_million_tokens": 1000,
        "output_cost_microunits_per_million_tokens": 3000,
    }


def request_bytes_for(role: str, *, model=None) -> bytes:
    return canonical({
        "model": model or ("synthetic-model-" + role),
        "messages": [{"role": "user", "content": "task " + role}],
    })


def material_for(**role_overrides) -> dict:
    material = {}
    for role in ROLES:
        entry = {
            "model_family": "family-" + role,
            "provider": "example",
            "model_version": "synthetic-1",
            "prompt_sha256": sha(b"prompt-" + role.encode()),
            "sampling_sha256": sha(b"sampling-" + role.encode()),
            "task_instruction_sha256": sha(b"instruction-" + role.encode()),
            "profile": profile_for(role),
            "request_bytes": request_bytes_for(role),
        }
        if role in role_overrides:
            entry.update(role_overrides[role])
        material[role] = entry
    return material


def tmp_path(testcase) -> Path:
    directory = tempfile.TemporaryDirectory()
    testcase.addCleanup(directory.cleanup)
    return Path(directory.name)


class BlindFreezeMaterializationTests(unittest.TestCase):
    def test_materialized_record_feeds_real_verifier_end_to_end(self):
        path = tmp_path(self) / "freeze-record.json"
        result = materialize_blind_freeze(
            source_context_sha256=SOURCE_CONTEXT,
            role_material=material_for(),
            approved_origins={ORIGIN}, record_path=path)
        loaded = load_materialized_freeze(
            path.read_bytes(), expected_record_sha256=result["record_sha256"])
        outputs = {role: ("sealed-" + role).encode() for role in ROLES}
        verified = verify_blind_capture(
            loaded["freeze"], loaded["role_inputs"], outputs)
        self.assertEqual(verified["status"], "STRUCTURAL_CAPTURE_ONLY")
        for role in ROLES:
            self.assertEqual(verified["roles"][role]["input_sha256"],
                             result["role_input_sha256"][role])
        self.assertFalse(verified["trusted_provider_invocation_proven"])
        self.assertFalse(verified["empirical_qualification_pass"])

    def test_privileged_binding_uses_production_frozen_digest(self):
        path = tmp_path(self) / "freeze-record.json"
        result = materialize_blind_freeze(
            source_context_sha256=SOURCE_CONTEXT,
            role_material=material_for(),
            approved_origins={ORIGIN}, record_path=path)
        material = material_for()
        for role in ROLES:
            self.assertEqual(
                result["privileged_request_envelope_sha256"][role],
                frozen_invocation_digest(material[role]["profile"],
                                         material[role]["request_bytes"],
                                         approved_origins={ORIGIN}))
            self.assertEqual(
                result["privileged_request_body_sha256"][role],
                sha(material[role]["request_bytes"]))

    def test_record_bytes_deterministic_and_pre_output_flag_true(self):
        first = tmp_path(self) / "one.json"
        second = tmp_path(self) / "two.json"
        one = materialize_blind_freeze(
            source_context_sha256=SOURCE_CONTEXT, role_material=material_for(),
            approved_origins={ORIGIN}, record_path=first)
        two = materialize_blind_freeze(
            source_context_sha256=SOURCE_CONTEXT, role_material=material_for(),
            approved_origins={ORIGIN}, record_path=second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        record = json.loads(first.read_bytes())
        self.assertIs(record["freeze"]["frozen_before_first_response"], True)
        self.assertEqual(one["record_sha256"], two["record_sha256"])

    def test_envelope_bytes_have_exact_four_field_shape(self):
        path = tmp_path(self) / "freeze-record.json"
        result = materialize_blind_freeze(
            source_context_sha256=SOURCE_CONTEXT,
            role_material=material_for(),
            approved_origins={ORIGIN}, record_path=path)
        for role in ROLES:
            envelope = json.loads(result["role_input_envelope_bytes"][role])
            self.assertEqual(set(envelope), set(INPUT_FIELDS))
            self.assertEqual(envelope["source_pack_git_blob"], SOURCE_BLOB)
            self.assertEqual(envelope["source_context_sha256"], SOURCE_CONTEXT)
            self.assertEqual(envelope["visibility_scope"], VIS[role])

    def test_digest_anchor_mismatch_blocked(self):
        path = tmp_path(self) / "freeze-record.json"
        result = materialize_blind_freeze(
            source_context_sha256=SOURCE_CONTEXT,
            role_material=material_for(),
            approved_origins={ORIGIN}, record_path=path)
        raw = path.read_bytes()
        tampered = raw[:-1] + (b"X" if raw[-1:] != b"X" else b"Y")
        with self.assertRaisesRegex(PilotBlocked, "digest differs"):
            load_materialized_freeze(tampered,
                                     expected_record_sha256=result["record_sha256"])

    def test_embedded_envelope_tamper_blocked(self):
        path = tmp_path(self) / "freeze-record.json"
        result = materialize_blind_freeze(
            source_context_sha256=SOURCE_CONTEXT,
            role_material=material_for(),
            approved_origins={ORIGIN}, record_path=path)
        record = json.loads(path.read_bytes())
        record["role_inputs"]["P"]["task_instruction_sha256"] = sha(b"other")
        tampered = canonical(record)
        with self.assertRaisesRegex(PilotBlocked, "frozen exact bytes"):
            load_materialized_freeze(tampered, expected_record_sha256=sha(tampered))

    def test_frozen_flag_downgraded_in_record_blocked(self):
        path = tmp_path(self) / "freeze-record.json"
        materialize_blind_freeze(
            source_context_sha256=SOURCE_CONTEXT, role_material=material_for(),
            approved_origins={ORIGIN}, record_path=path)
        record = json.loads(path.read_bytes())
        record["freeze"]["frozen_before_first_response"] = False
        tampered = canonical(record)
        with self.assertRaisesRegex(PilotBlocked, "invalid embedded blind freeze"):
            load_materialized_freeze(tampered, expected_record_sha256=sha(tampered))

    def test_unknown_record_identity_blocked(self):
        path = tmp_path(self) / "freeze-record.json"
        materialize_blind_freeze(
            source_context_sha256=SOURCE_CONTEXT, role_material=material_for(),
            approved_origins={ORIGIN}, record_path=path)
        record = json.loads(path.read_bytes())
        record["schema_version"] = "v04-mla-blind-freeze-materialization-v0"
        tampered = canonical(record)
        with self.assertRaisesRegex(PilotBlocked, "unknown freeze record identity"):
            load_materialized_freeze(tampered, expected_record_sha256=sha(tampered))

    def test_privileged_profile_family_mismatch_blocked(self):
        path = tmp_path(self) / "freeze-record.json"
        with self.assertRaisesRegex(PilotBlocked, "differs from frozen role configuration"):
            materialize_blind_freeze(
                source_context_sha256=SOURCE_CONTEXT,
                role_material=material_for(
                    P={"profile": profile_for("P", family="family-OTHER")}),
                approved_origins={ORIGIN}, record_path=path)
        self.assertFalse(path.exists())

    def test_privileged_profile_provider_mismatch_blocked(self):
        path = tmp_path(self) / "freeze-record.json"
        with self.assertRaisesRegex(PilotBlocked, "differs from frozen role configuration"):
            materialize_blind_freeze(
                source_context_sha256=SOURCE_CONTEXT,
                role_material=material_for(
                    R={"profile": profile_for("R", provider="other")}),
                approved_origins={ORIGIN}, record_path=path)

    def test_invalid_precommitted_digests_blocked(self):
        path = tmp_path(self) / "freeze-record.json"
        with self.assertRaisesRegex(PilotBlocked, "must be SHA256"):
            materialize_blind_freeze(
                source_context_sha256=SOURCE_CONTEXT,
                role_material=material_for(P={"task_instruction_sha256": "not-sha"}),
                approved_origins={ORIGIN}, record_path=path)
        with self.assertRaisesRegex(PilotBlocked, "must be SHA256"):
            materialize_blind_freeze(
                source_context_sha256=SOURCE_CONTEXT,
                role_material=material_for(R={"sampling_sha256": "z" * 64}),
                approved_origins={ORIGIN}, record_path=path)
        self.assertFalse(path.exists())

    def test_missing_role_material_blocked(self):
        path = tmp_path(self) / "freeze-record.json"
        partial = material_for()
        del partial["X"]
        with self.assertRaisesRegex(PilotBlocked, "exact P/R/X"):
            materialize_blind_freeze(
                source_context_sha256=SOURCE_CONTEXT, role_material=partial,
                approved_origins={ORIGIN}, record_path=path)

    def test_request_body_not_bound_to_profile_blocked(self):
        path = tmp_path(self) / "freeze-record.json"
        with self.assertRaisesRegex(PilotBlocked, "failed frozen digest validation"):
            materialize_blind_freeze(
                source_context_sha256=SOURCE_CONTEXT,
                role_material=material_for(
                    X={"request_bytes": request_bytes_for("X", model="other-model")}),
                approved_origins={ORIGIN}, record_path=path)

    def test_verifier_rejects_divergent_input_bytes_after_freeze(self):
        path = tmp_path(self) / "freeze-record.json"
        result = materialize_blind_freeze(
            source_context_sha256=SOURCE_CONTEXT,
            role_material=material_for(),
            approved_origins={ORIGIN}, record_path=path)
        loaded = load_materialized_freeze(
            path.read_bytes(), expected_record_sha256=result["record_sha256"])
        inputs = dict(loaded["role_inputs"])
        inputs["P"] = inputs["P"] + b" "
        outputs = {role: ("sealed-" + role).encode() for role in ROLES}
        with self.assertRaisesRegex(BlindCaptureBlocked, "differs from frozen bytes"):
            verify_blind_capture(loaded["freeze"], inputs, outputs)

    def test_refuses_to_overwrite_existing_record(self):
        path = tmp_path(self) / "freeze-record.json"
        first = materialize_blind_freeze(
            source_context_sha256=SOURCE_CONTEXT, role_material=material_for(),
            approved_origins={ORIGIN}, record_path=path)
        with self.assertRaisesRegex(PilotBlocked, "refusing overwrite"):
            materialize_blind_freeze(
                source_context_sha256=SOURCE_CONTEXT,
                role_material=material_for(),
                approved_origins={ORIGIN}, record_path=path)
        self.assertEqual(sha(path.read_bytes()), first["record_sha256"])


if __name__ == "__main__":
    unittest.main()
