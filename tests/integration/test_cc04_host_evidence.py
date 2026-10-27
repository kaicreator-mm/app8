"""CC04 Host join preflight tests: pure validation, no Docker or signed Host claims."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from runpy import run_path
import sys
import unittest

module = run_path(str(Path(__file__).resolve().parents[2] /
                      "examples" / "cc-mvp" / "host_evidence.py"))
validate_job = module["validate_job"]
CC04Blocked = module["CC04Blocked"]

SHA = "a" * 64
IMAGE = "registry.example/cc04@sha256:" + SHA


def config():
    return {
        "capability": {
            "schema_version": "app8-capability-v1",
            "capability_id": "cap:cc04-fixture",
            "revision": 1,
            "semantic": {
                "name": "Summarize pinned CSV", "purpose": "Read-only scoped report",
                "user_job": "Summarize immutable fixture", "inputs": ["immutable CSV"],
                "outputs": ["JSON counts"], "variants": [],
                "constraints": ["no network"], "negative_boundaries": ["bad option"],
                "failure_modes": ["parse error"], "side_effects": [],
            },
            "source": {
                "repository": "pandas-dev/pandas", "revision": "fixture",
                "content_sha256": SHA, "license_disposition": "REVIEWED_COMPATIBLE",
            },
            "target": {
                "identity": IMAGE, "package_sha256": SHA,
                "mapping_relation": "SAME", "environment_id": "test-env",
            },
            "bindings": [{
                "binding_id": "binding:csv", "kind": "CLI",
                "address": "/opt/ccmvp/pandas-job",
                "preconditions": [], "side_effects": [],
            }],
            "evidence_refs": [],
            "readiness": {
                "lifecycle_state": "HYPOTHESIZED", "export_ready": False,
                "derived_by_policy": True, "policy_revision": "cc01-candidate-v1",
                "reason_codes": ["REAL_EVIDENCE_NOT_ADMITTED"],
            },
            "projection_refs": [],
        },
        "docker": {
            "client_path": str(Path(sys.executable).resolve()),
            "client_sha256": SHA,
            "runner_id": "trusted-fixture",
            "environment_id": "test-env",
        },
        "cases": [{
            "claim_id": "claim:csv-summary",
            "args": ["--group-by", "category"],
            "assertions": ["exit_code==0"],
            "fixture": {
                "content_sha256": SHA,
                "input_description": "pinned four-row CSV",
                "reset_procedure": "ephemeral read-only container",
            },
        }],
    }


class CC04HostPreflightTests(unittest.TestCase):
    def test_well_formed_reviewed_job_can_reach_real_host_boundary(self):
        cap, cases = validate_job(config())
        self.assertEqual(cap["capability_id"], "cap:cc04-fixture")
        self.assertEqual(len(cases), 1)
        self.assertEqual(cap["evidence_refs"], [])

    def test_unreviewed_license_and_unproven_mapping_block(self):
        for field, value in (("license", "UNKNOWN"), ("mapping", "UNRESOLVED")):
            job = deepcopy(config())
            if field == "license":
                job["capability"]["source"]["license_disposition"] = value
            else:
                job["capability"]["target"]["mapping_relation"] = value
            with self.subTest(field=field), self.assertRaises(CC04Blocked):
                validate_job(job)

    def test_preexisting_evidence_or_unscoped_binding_block(self):
        for field in ("refs", "sdk", "mutation"):
            job = deepcopy(config())
            if field == "refs":
                job["capability"]["evidence_refs"] = ["ev:fake"]
            elif field == "sdk":
                job["capability"]["bindings"][0]["kind"] = "LIBRARY_API"
            else:
                job["capability"]["bindings"][0]["side_effects"] = ["file write"]
            with self.subTest(field=field), self.assertRaises(CC04Blocked):
                validate_job(job)

    def test_environment_or_case_shape_drift_blocks(self):
        for field in ("environment", "case_extra"):
            job = deepcopy(config())
            if field == "environment":
                job["docker"]["environment_id"] = "another-host"
            else:
                job["cases"][0]["untrusted"] = "extra"
            with self.subTest(field=field), self.assertRaises(CC04Blocked):
                validate_job(job)


if __name__ == "__main__":
    unittest.main()
