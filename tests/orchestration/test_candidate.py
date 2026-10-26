"""CC01: a model-derived proposal must never become trusted execution evidence."""
import unittest

from app8.discovery import SourceDocument
from app8.orchestration import (
    PlanError, assemble_typed_candidate, freeze_hypotheses,
)
from app8.contracts import validate_contract

SHA = "f" * 64


def source(name="pandas"):
    return SourceDocument(name, "revision-1", "docs/reference.md", SHA,
                          "A documented software user task.")


def frozen(src, identifier):
    return freeze_hypotheses({
        "schema_version": "app8-hypotheses-v1",
        "source_sha256": SHA,
        "source_revision": src.revision,
        "hypotheses": [{
            "id": identifier,
            "user_job": "Safely inspect a user dataset",
            "surface": "CLI",
            "constraints": ["version pinned"],
            "source_anchor": "docs/reference.md:1",
        }],
    }, src)


def semantics():
    return {
        "name": "Inspect dataset",
        "purpose": "Read shape and constraints",
        "user_job": "Safely inspect a user dataset",
        "inputs": ["input file"],
        "outputs": ["metadata"],
        "variants": [],
        "constraints": ["version pinned"],
        "negative_boundaries": ["missing file"],
        "failure_modes": ["file not found"],
        "side_effects": [],
    }


def binding():
    return {
        "binding_id": "binding:inspect",
        "kind": "CLI",
        "address": "/trusted/bin/inspector",
        "preconditions": ["read-only"],
        "side_effects": [],
    }


def assemble(src, identifier, semantic=None, cli=None):
    return assemble_typed_candidate(
        frozen(src, identifier), src, identifier,
        semantics() if semantic is None else semantic,
        binding() if cli is None else cli,
        target_identity="official-release-v1",
        target_package_sha256=SHA, environment_id="isolated-fixture",
    )


class CandidateCompilerTests(unittest.TestCase):
    def test_two_software_classes_typed_but_never_ready(self):
        for name, case in (("ffmpeg", "FFMPEG004"), ("pandas", "PANDAS002")):
            with self.subTest(name=name):
                env = assemble(source(name), case)
                cap = validate_contract("capability", env["capability"])
                self.assertEqual(env["origin"], "MODEL_PROPOSAL_ONLY")
                self.assertEqual(env["binding_origin"], "UNTRUSTED_PROPOSAL")
                self.assertFalse(env["capability_promotion_allowed"])
                self.assertEqual(env["real_execution_status"], "NOT_RUN")
                self.assertEqual(cap["readiness"]["lifecycle_state"], "HYPOTHESIZED")
                self.assertFalse(cap["readiness"]["export_ready"])
                self.assertEqual(cap["source"]["license_disposition"], "UNKNOWN")
                self.assertEqual(cap["target"]["mapping_relation"], "UNRESOLVED")
                self.assertEqual(cap["evidence_refs"], [])
                self.assertEqual(cap["bindings"][0]["kind"], "CLI")

    def test_model_cannot_add_authoritative_readiness(self):
        sem = semantics()
        sem["export_ready"] = True
        with self.assertRaises(PlanError):
            assemble(source(), "PANDAS002", semantic=sem)

    def test_model_cannot_add_trust_to_binding(self):
        bind = binding()
        bind["verified_by"] = "MODEL"
        with self.assertRaises(PlanError):
            assemble(source(), "PANDAS002", cli=bind)

    def test_sdk_only_pandas_is_rejected(self):
        bind = binding()
        bind["kind"] = "LIBRARY_API"
        with self.assertRaises(PlanError):
            assemble(source(), "PANDAS002", cli=bind)

    def test_hypothesis_identity_mismatch_is_rejected(self):
        src = source()
        with self.assertRaises(PlanError):
            assemble_typed_candidate(
                frozen(src, "PANDAS002"), src, "DIFFERENT", semantics(), binding(),
                target_identity="release", target_package_sha256=SHA,
                environment_id="isolated",
            )

    def test_source_revision_change_blocks(self):
        src = source()
        f = frozen(src, "PANDAS002")
        altered = SourceDocument(src.repository, "unreviewed-revision",
                                 src.relative_path, src.content_sha256, src.text)
        with self.assertRaises(PlanError):
            assemble_typed_candidate(
                f, altered, "PANDAS002", semantics(), binding(),
                target_identity="release", target_package_sha256=SHA,
                environment_id="isolated",
            )

    def test_semantics_cannot_delete_frozen_constraint(self):
        sem = semantics()
        sem["constraints"] = []
        with self.assertRaises(PlanError):
            assemble(source(), "PANDAS002", semantic=sem)

    def test_job_cannot_change_after_frozen_proposal(self):
        sem = semantics()
        sem["user_job"] = "Execute unrestricted code"
        with self.assertRaises(PlanError):
            assemble(source(), "PANDAS002", semantic=sem)

    def test_unbounded_input_rejected(self):
        sem = semantics()
        sem["inputs"] = ["input"] * 31
        with self.assertRaises(PlanError):
            assemble(source(), "PANDAS002", semantic=sem)

    def test_target_digest_is_exact(self):
        src = source()
        with self.assertRaises(PlanError):
            assemble_typed_candidate(
                frozen(src, "PANDAS002"), src, "PANDAS002", semantics(), binding(),
                target_identity="release", target_package_sha256="nohash",
                environment_id="isolated",
            )

    def test_control_char_binding_rejected(self):
        bind = binding()
        bind["address"] = "tool\\nignored"
        bind["address"] = bind["address"].replace("\\n", "\n")
        with self.assertRaises(PlanError):
            assemble(source(), "PANDAS002", cli=bind)


if __name__ == "__main__":
    unittest.main()
