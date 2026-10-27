"""Scoped persisted Agent tool handoff: pure contract checks only (no Docker)."""
from copy import deepcopy
from pathlib import Path
from runpy import run_path
import unittest

ROOT = Path(__file__).resolve().parents[2]
checked_selection = run_path(
    str(ROOT / "examples" / "cc-mvp" / "agent_consume.py")
)["checked_selection"]
operator_job = run_path(
    str(ROOT / "tests" / "integration" / "test_cc04_host_evidence.py")
)["config"]


def admission():
    job = operator_job()
    admitted = deepcopy(job["capability"])
    admitted["evidence_refs"] = ["ev:synthetic-fixture-only"]
    return job, admitted


class PersistedAgentEntryTests(unittest.TestCase):
    def test_selected_admitted_job_keeps_frozen_args(self):
        job, cap = admission()
        config, case = checked_selection(job, cap, 1)
        self.assertEqual(config["environment_id"], "test-env")
        self.assertEqual(case["args"], ["--group-by", "category"])

    def test_operator_job_cannot_change_after_admission(self):
        job, cap = admission()
        job["capability"]["source"]["content_sha256"] = "b" * 64
        with self.assertRaises(ValueError):
            checked_selection(job, cap, 1)

    def test_case_and_environment_cannot_drift(self):
        job, cap = admission()
        with self.assertRaises(ValueError):
            checked_selection(job, cap, 2)
        job["docker"]["environment_id"] = "different-host"
        with self.assertRaises(ValueError):
            checked_selection(job, cap, 1)

    def test_cli_only_and_existing_evidence_are_required(self):
        job, cap = admission()
        cap["bindings"][0]["kind"] = "LIBRARY_API"
        job["capability"]["bindings"][0]["kind"] = "LIBRARY_API"
        with self.assertRaises(ValueError):
            checked_selection(job, cap, 1)


if __name__ == "__main__":
    unittest.main()
