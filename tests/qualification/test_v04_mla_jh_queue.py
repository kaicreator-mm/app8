"""Synthetic J/H queue checks; all reviewer submissions remain unverified."""
import hashlib
import json
import unittest

from scripts.v04_mla_jh_queue import build_jh_candidate_queue
from scripts.v04_mla_pilot_reducer import ALLOWLIST, ROOT, SOURCE_BLOB, PilotBlocked, assess


def sha(x):
    return hashlib.sha256(x).hexdigest()


def fixture():
    anchors = json.loads((ROOT / ALLOWLIST).read_text(encoding="utf-8"))["assets"]
    cases = []
    for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice"):
        path, blob = sorted(anchors[asset].items())[0]
        for i in range(6):
            cases.append({
                "case_id": "V04-" + asset.upper() + "-" + str(i + 1).zfill(3),
                "asset": asset, "source_anchor": {"path": path, "blob": blob},
                "model_prediction_sha256": "a" * 64,
                "reference_proposer_sha256": "b" * 64,
                "adversarial_challenger_sha256": "c" * 64,
                "source_verification_claim": "CANDIDATE_ONLY",
                "behavior_observation_sha256": None,
                "high_impact_unresolved": False,
                "oracle_visible_to_predictor": False, "model_consensus": False,
            })
    return {
        "schema_version": "v04-mla-pilot-public-v1",
        "study_id": "V04-MLA-1", "source_pack_git_blob": SOURCE_BLOB,
        "reference_origin": "LLM_PROPOSED",
        "frozen_before_model_outputs": True,
        "human_selection_seed_sha256": sha(b"frozen-jh-seed"),
        "cases": cases,
    }


def hrow(cid, decision="CONFIRM"):
    return {
        "case_id": cid, "decision": decision,
        "decision_origin": "HUMAN_SELF_REPORT_UNVERIFIED",
        "reviewer_id_sha256": "1" * 64,
        "evidence_ref_sha256": "2" * 64,
        "submission_sha256": "3" * 64,
    }


def jrow(cid):
    return {
        "case_id": cid, "reference_origin": "LLM_PROPOSED",
        "model_family": "independent-fixture", "provider": "test-only",
        "prompt_sha256": "4" * 64, "config_sha256": "5" * 64,
        "response_sha256": "6" * 64,
    }


class JHQueueTests(unittest.TestCase):
    def test_missing_h_cards_blocked(self):
        r = build_jh_candidate_queue(fixture(), [], [])
        self.assertEqual(r["status"], "BLOCKED_HUMAN_REVIEW_PENDING_OR_DEFERRED")
        self.assertEqual(len(r["missing_human_case_ids"]), 4)
        self.assertFalse(r["capability_promotion_allowed"])

    def test_full_self_reports_still_provisional(self):
        p = fixture()
        selected = assess(ROOT, p)["human_sample_case_ids"]
        r = build_jh_candidate_queue(p, [], [hrow(cid) for cid in selected])
        self.assertEqual(r["status"], "PROVISIONAL_H_SUBMISSIONS_UNVERIFIED")
        self.assertFalse(r["human_identity_and_decision_verified"])
        self.assertFalse(r["formal_product_release_qualified"])

    def test_defer_is_blocked(self):
        p = fixture()
        selected = assess(ROOT, p)["human_sample_case_ids"]
        reports = [hrow(cid) for cid in selected]
        reports[0]["decision"] = "DEFER"
        r = build_jh_candidate_queue(p, [], reports)
        self.assertEqual(r["status"], "BLOCKED_HUMAN_REVIEW_PENDING_OR_DEFERRED")
        self.assertEqual(len(r["deferred_human_case_ids"]), 1)

    def test_unselected_h_submission_fails(self):
        p = fixture()
        selected = set(assess(ROOT, p)["human_sample_case_ids"])
        missing = next(c["case_id"] for c in p["cases"] if c["case_id"] not in selected)
        with self.assertRaisesRegex(PilotBlocked, "outside"):
            build_jh_candidate_queue(p, [], [hrow(missing)])

    def test_h_cannot_assert_verified_authority(self):
        p = fixture()
        cid = assess(ROOT, p)["human_sample_case_ids"][0]
        row = hrow(cid)
        row["decision_origin"] = "INDEPENDENT_HUMAN_GOLD"
        with self.assertRaisesRegex(PilotBlocked, "claimed-authoritative"):
            build_jh_candidate_queue(p, [], [row])

    def test_non_string_h_decision_fails_closed(self):
        p = fixture()
        cid = assess(ROOT, p)["human_sample_case_ids"][0]
        row = hrow(cid)
        row["decision"] = {"malformed": "CONFIRM"}
        with self.assertRaisesRegex(PilotBlocked, "invalid or claimed-authoritative"):
            build_jh_candidate_queue(p, [], [row])

    def test_hidden_h_truth_rejected(self):
        p = fixture()
        cid = assess(ROOT, p)["human_sample_case_ids"][0]
        row = hrow(cid)
        row["hidden_oracle_truth"] = True
        with self.assertRaisesRegex(PilotBlocked, "leakage"):
            build_jh_candidate_queue(p, [], [row])

    def test_duplicate_h_card_rejected(self):
        p = fixture()
        cid = assess(ROOT, p)["human_sample_case_ids"][0]
        with self.assertRaisesRegex(PilotBlocked, "duplicate"):
            build_jh_candidate_queue(p, [], [hrow(cid), hrow(cid)])

    def test_j_must_be_predeclared_conflict(self):
        p = fixture()
        with self.assertRaisesRegex(PilotBlocked, "predeclared conflict"):
            build_jh_candidate_queue(p, [jrow(p["cases"][0]["case_id"])], [])

    def test_j_one_pass_on_conflict_never_oracle(self):
        p = fixture()
        p["cases"][0]["high_impact_unresolved"] = True
        r = build_jh_candidate_queue(p, [jrow(p["cases"][0]["case_id"])], [])
        self.assertEqual(len(r["reported_j_escalation_case_ids"]), 1)
        self.assertFalse(r["judge_transcripts_authoritative"])

    def test_j_cannot_self_certify_human_gold(self):
        p = fixture()
        p["cases"][0]["high_impact_unresolved"] = True
        row = jrow(p["cases"][0]["case_id"])
        row["reference_origin"] = "INDEPENDENT_HUMAN_GOLD"
        with self.assertRaisesRegex(PilotBlocked, "cannot claim oracle"):
            build_jh_candidate_queue(p, [row], [])

    def test_j_hard_limit_12(self):
        p = fixture()
        for c in p["cases"][:13]:
            c["high_impact_unresolved"] = True
        judges = [jrow(c["case_id"]) for c in p["cases"][:13]]
        with self.assertRaisesRegex(PilotBlocked, "J escalation budget"):
            build_jh_candidate_queue(p, judges, [])

    def test_j_duplicate_forbidden(self):
        p = fixture()
        p["cases"][0]["high_impact_unresolved"] = True
        row = jrow(p["cases"][0]["case_id"])
        with self.assertRaisesRegex(PilotBlocked, "one eligible"):
            build_jh_candidate_queue(p, [row, row], [])

    def test_h_budget_overflow_remains_blocked(self):
        p = fixture()
        for c in p["cases"][:16]:
            c["high_impact_unresolved"] = True
        r = build_jh_candidate_queue(p, [], [])
        self.assertEqual(r["status"], "BLOCKED_HUMAN_REVIEW_BUDGET")
        self.assertGreater(len(r["required_human_case_ids"]), 12)
        self.assertFalse(r["capability_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
