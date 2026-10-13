import copy
import hashlib
import json
import unittest

from app8.discovery import SourceDocument
from app8.orchestration import PlanError, freeze_hypotheses, freeze_falsification_plan

SHA="0"*64
SRC=SourceDocument("fixture", "rev1", "docs/readme.md", SHA, "Sample")


def hypothesis():
    return {"schema_version":"app8-hypotheses-v1", "source_sha256":SHA,"source_revision":"rev1",
            "hypotheses":[{"id":"H1","user_job":"Read data","surface":"CLI", "constraints":["readonly"],"source_anchor":"docs/readme.md:1"}]}


def plan(frozen):
    return {"schema_version":"app8-plan-v1", "hypothesis_sha256":frozen["proposal_sha256"],
            "target_sha256":SHA, "probes":[{"hypothesis_id":"H1", "positive":["run in sandbox"],
            "falsifying":["run invalid input"],"timeout_seconds":30,
            "network_allowed":False,"mutation_allowed":False}]}


class PlanTests(unittest.TestCase):
    def test_hypothesis_provenance_and_no_evidence(self):
        f=freeze_hypotheses(hypothesis(),SRC)
        self.assertEqual(f["origin"],"MODEL_PROPOSAL_ONLY")
        self.assertFalse(f["evidence_claimed"])

    def test_source_mismatch_rejected(self):
        bad=hypothesis();bad["source_sha256"]="f"*64
        with self.assertRaises(PlanError):freeze_hypotheses(bad,SRC)

    def test_duplicate_hypothesis_rejected(self):
        bad=hypothesis();bad["hypotheses"].append(bad["hypotheses"][0])
        with self.assertRaises(PlanError):freeze_hypotheses(bad,SRC)

    def test_hidden_gold_key_rejected(self):
        bad=hypothesis();bad["hypotheses"][0]["truth_class"]="TRUE"
        with self.assertRaises(PlanError):freeze_hypotheses(bad,SRC)

    def test_plan_is_frozen_not_executed(self):
        f=freeze_hypotheses(hypothesis(),SRC)
        frozen=freeze_falsification_plan(plan(f),f,SHA)
        self.assertFalse(frozen["real_execution_observed"])
        self.assertEqual(frozen["origin"],"MODEL_PROPOSAL_ONLY")

    def test_plan_wrong_target_rejected(self):
        f=freeze_hypotheses(hypothesis(),SRC)
        with self.assertRaises(PlanError):freeze_falsification_plan(plan(f),f,"f"*64)

    def test_plan_truth_leak_rejected(self):
        f=freeze_hypotheses(hypothesis(),SRC);p=plan(f);p["ground_truth"]="hidden"
        with self.assertRaises(PlanError):freeze_falsification_plan(p,f,SHA)

    def test_plan_missing_falsifying_case_rejected(self):
        f=freeze_hypotheses(hypothesis(),SRC);p=plan(f);p["probes"][0]["falsifying"]=[]
        with self.assertRaises(PlanError):freeze_falsification_plan(p,f,SHA)

    def test_plan_budget_out_of_range_rejected(self):
        f=freeze_hypotheses(hypothesis(),SRC);p=plan(f);p["probes"][0]["timeout_seconds"]=301
        with self.assertRaises(PlanError):freeze_falsification_plan(p,f,SHA)

    def test_nonnumeric_budget_rejected(self):
        f=freeze_hypotheses(hypothesis(),SRC);p=plan(f);p["probes"][0]["timeout_seconds"]="30"
        with self.assertRaises(PlanError):freeze_falsification_plan(p,f,SHA)

    def test_boolean_budget_rejected(self):
        f=freeze_hypotheses(hypothesis(),SRC);p=plan(f);p["probes"][0]["timeout_seconds"]=True
        with self.assertRaises(PlanError):freeze_falsification_plan(p,f,SHA)

    def test_duplicate_json_key_rejected(self):
        raw='{"schema_version":"app8-hypotheses-v1","schema_version":"app8-hypotheses-v1"}'
        with self.assertRaises(ValueError):freeze_hypotheses(raw,SRC)

if __name__=="__main__":unittest.main()
