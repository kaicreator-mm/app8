"""v0.3 complete-ledger pilot tests. Signing here is synthetic, not real host."""
import hashlib
import hmac
import json
from pathlib import Path
import tempfile
import unittest

from app8.evidence.attestation import AttestationGate
from app8.evidence.ingress import import_signed_observation
from app8.qualification import qualify_stored_capability, verify_evidence_link, EvidenceLinkError
from app8.storage import EvidenceStore

HEX0 = "0" * 64
RUNNER_KEY = b"unit-test-credential-not-for-production"  # synthetic ONLY


def canonical(data):
    return (json.dumps(data, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def capability(refs):
    return {
        "schema_version": "app8-capability-v1", "capability_id": "cap:json-parse",
        "revision": 1,
        "semantic": {
            "name": "Parse JSON", "purpose": "Decode well-formed JSON",
            "user_job": "Read structured data", "inputs": ["json"],
            "outputs": ["value"], "variants": [], "constraints": ["UTF-8"],
            "negative_boundaries": ["malformed JSON"], "failure_modes": ["parse error"],
            "side_effects": []
        },
        "source": {"repository": "python/cpython", "revision": "test-pin",
                   "content_sha256": HEX0, "license_disposition": "REVIEWED_COMPATIBLE"},
        "target": {"identity": "library/python@sha256:" + "b" * 64,
                   "package_sha256": "b" * 64, "mapping_relation": "SAME",
                   "environment_id": "test-linux"},
        "bindings": [{"binding_id": "binding:json", "kind": "CLI",
                      "address": "/usr/local/bin/python", "preconditions": [],
                      "side_effects": []}],
        "evidence_refs": refs,
        "readiness": {"lifecycle_state": "EXPORT_READY", "export_ready": True,
                      "derived_by_policy": True, "policy_revision": "caller",
                      "reason_codes": ["SELF_ASSERTED"]},
        "projection_refs": [],
    }


def evidence(identifier, verdict="SUPPORTED"):
    cap = capability([identifier])
    return {
        "schema_version": "app8-evidence-v1", "evidence_id": identifier,
        "claim_id": "claim:parse", "capability_id": cap["capability_id"],
        "source": {key: cap["source"][key] for key in ("repository", "revision", "content_sha256")},
        "target": dict(cap["target"]),
        "fixture": {"content_sha256": HEX0, "input_description": "unit fixture",
                    "reset_procedure": "ephemeral"},
        "plan": {"plan_sha256": HEX0, "binding_id": "binding:json",
                 "assertions": ["exit_code==0"],
                 "budget": {"wall_seconds": 10, "max_output_bytes": 4096,
                            "network_allowed": False, "mutation_allowed": False}},
        "observation": {"observer": "DETERMINISTIC_EXECUTION_ADAPTER",
                        "execution_status": "EXECUTED", "invocation_sha256": HEX0,
                        "exit_code": 0 if verdict == "SUPPORTED" else 3,
                        "stdout_sha256": HEX0, "stderr_sha256": HEX0,
                        "artifacts": [], "recorded_at": "2026-10-14T12:00:00Z"},
        "assessment": {"verdict": verdict,
                       "assessor_kind": "DETERMINISTIC_ASSERTION_ENGINE",
                       "reason_codes": ["ASSERTIONS_PASSED" if verdict == "SUPPORTED"
                                        else "ASSERTIONS_FAILED"]},
        "replay": {"manifest_sha256": HEX0,
                   "artifact_location": "LOCAL_CONTENT_ADDRESSED"},
    }


def signed(ev, n):
    obj = {
        "schema_version": "app8-attested-evidence-v2",
        "evidence_sha256": hashlib.sha256(canonical(ev)).hexdigest(),
        "runner_id": "unit-runner", "policy_sha256": "a" * 64,
        "image_sha256": "b" * 64, "nonce": f"{n:032x}",
    }
    obj["mac_sha256"] = hmac.new(RUNNER_KEY, canonical(obj), hashlib.sha256).hexdigest()
    return obj


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = EvidenceStore(Path(self.tmp.name) / "ledger")
        self.addCleanup(self.store.close)
        self.gate = AttestationGate(
            verification_key=RUNNER_KEY, runner_id="unit-runner",
            policy_sha256="a" * 64, image_sha256="b" * 64,
            nonce_db=Path(self.tmp.name) / "nonces.sqlite3")
        self.addCleanup(self.gate.close)
        self.sidecars = {}

    def add(self, ev, counter):
        receipt = signed(ev, counter)
        import_signed_observation(self.store, self.gate, ev, receipt)
        self.sidecars[ev["evidence_id"]] = receipt

    def qualify(self, cap):
        return qualify_stored_capability(
            cap, store=self.store, attestation_gate=self.gate,
            signed_attestations=self.sidecars)

    def test_signed_positive_scoped_ready(self):
        ev = evidence("ev:positive")
        self.add(ev, 1)
        result = self.qualify(capability([ev["evidence_id"]]))
        self.assertEqual(result.status, "SCOPED_EXPORT_READY")
        self.assertTrue(result.readiness.export_ready)
        self.assertFalse(result.release_qualified)
        self.assertTrue(result.projections["CLI"]["invocation_enabled"])

    def test_caller_claim_cannot_make_unobserved_ready(self):
        result = self.qualify(capability([]))
        self.assertEqual(result.status, "BLOCKED")
        self.assertFalse(result.readiness.export_ready)

    def test_positive_cannot_hide_signed_refutation(self):
        pos, neg = evidence("ev:positive"), evidence("ev:negative", "REFUTED")
        self.add(pos, 1)
        self.add(neg, 2)
        result = self.qualify(capability(["ev:positive"]))
        self.assertEqual(result.readiness.reason_codes, ("EVIDENCE_REFERENCE_SET_NOT_COMPLETE",))
        self.assertFalse(result.readiness.export_ready)

    def test_declared_refuted_still_blocks(self):
        self.add(evidence("ev:positive"), 1)
        self.add(evidence("ev:negative", "REFUTED"), 2)
        result = self.qualify(capability(["ev:positive", "ev:negative"]))
        self.assertEqual(result.readiness.reason_codes, ("MATERIAL_NEGATIVE_OR_CURRENTNESS_EVENT",))
        self.assertFalse(result.readiness.export_ready)

    def test_missing_or_invalid_attestation_blocks(self):
        ev = evidence("ev:positive")
        self.add(ev, 1)
        self.sidecars.clear()
        self.assertEqual(self.qualify(capability(["ev:positive"])).status, "BLOCKED")

    def test_target_drift_blocks(self):
        self.add(evidence("ev:positive"), 1)
        cap = capability(["ev:positive"])
        cap["target"]["package_sha256"] = "f" * 64
        self.assertFalse(self.qualify(cap).readiness.export_ready)

    def test_currentness_event_blocks(self):
        self.add(evidence("ev:positive"), 1)
        self.store.append_event("cap:json-parse", "STALE", {"reason": "release changed"})
        self.assertFalse(self.qualify(capability(["ev:positive"])).readiness.export_ready)

    def test_unsafe_license_blocks(self):
        self.add(evidence("ev:positive"), 1)
        cap = capability(["ev:positive"])
        cap["source"]["license_disposition"] = "UNKNOWN"
        result = self.qualify(cap)
        self.assertEqual(result.readiness.reason_codes, ("LICENSE_DISPOSITION_NOT_REVIEWED",))

    def test_unresolved_mapping_blocks(self):
        self.add(evidence("ev:positive"), 1)
        cap = capability(["ev:positive"])
        cap["target"]["mapping_relation"] = "UNRESOLVED"
        self.assertFalse(self.qualify(cap).readiness.export_ready)

    def test_unsupported_cli_binding_cannot_promote(self):
        self.add(evidence("ev:positive"), 1)
        cap = capability(["ev:positive"])
        cap["bindings"] = []
        self.assertFalse(self.qualify(cap).readiness.export_ready)

    def test_bounded_scan_refuses_partial_ledger(self):
        self.add(evidence("ev:positive"), 1)
        with self.assertRaises(ValueError):
            self.store.list_evidence_for_capability("cap:json-parse", max_records=0)
        with self.assertRaises(Exception):
            self.store.list_evidence_for_capability("cap:json-parse", max_records=True)



    def test_cc02_existing_signed_receipt_links_without_promoting(self):
        ev = evidence("ev:positive")
        self.add(ev, 1)
        result = verify_evidence_link(capability(["ev:positive"]), ev, self.sidecars["ev:positive"], self.gate)
        self.assertEqual(result.status, "AUTHENTICATED_LINK_NOT_RELEASE_QUALIFIED")
        self.assertFalse(result.export_ready)
        self.assertEqual(result.binding_id, "binding:json")

    def test_cc02_unsigned_and_forged_sidecar_fail(self):
        ev = evidence("ev:positive")
        self.add(ev, 1)
        with self.assertRaises(EvidenceLinkError):
            verify_evidence_link(capability(["ev:positive"]), ev, {}, self.gate)
        fake = dict(self.sidecars["ev:positive"])
        fake["mac_sha256"] = "0" * 64
        with self.assertRaises(EvidenceLinkError):
            verify_evidence_link(capability(["ev:positive"]), ev, fake, self.gate)

    def test_cc02_identity_mismatch_fails(self):
        ev = evidence("ev:positive")
        self.add(ev, 1)
        original = capability(["ev:positive"])
        changed = capability(["ev:positive"])
        changed["target"]["environment_id"] = "wrong-host"
        with self.assertRaises(EvidenceLinkError):
            verify_evidence_link(changed, ev, self.sidecars["ev:positive"], self.gate)
        changed = capability(["ev:positive"])
        changed["bindings"][0]["binding_id"] = "binding:other"
        with self.assertRaises(EvidenceLinkError):
            verify_evidence_link(changed, ev, self.sidecars["ev:positive"], self.gate)
        changed = capability([])
        with self.assertRaises(EvidenceLinkError):
            verify_evidence_link(changed, ev, self.sidecars["ev:positive"], self.gate)

    def test_cc02_receipt_is_not_authority_for_license(self):
        ev = evidence("ev:positive")
        self.add(ev, 1)
        changed = capability(["ev:positive"])
        changed["source"]["license_disposition"] = "UNKNOWN"
        # Link check only: full-ledger qualification remains BLOCKED.
        linked = verify_evidence_link(changed, ev, self.sidecars["ev:positive"], self.gate)
        self.assertFalse(linked.export_ready)
        qualified = self.qualify(changed)
        self.assertEqual(qualified.status, "BLOCKED")
        self.assertEqual(qualified.readiness.reason_codes, ("LICENSE_DISPOSITION_NOT_REVIEWED",))

if __name__ == "__main__":
    unittest.main()
