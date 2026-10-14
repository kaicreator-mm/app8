"""No network: simulate GitHub comment reads for fail-closed witness gate."""
import copy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import os

from app8.mla.ordered_host_ledger import OrderedMLAHostLedger
from app8.mla.github_freeze_witness import (
    ExternalFreezeWitnessBlocked, freeze_witness_body,
    admission_subject_sha256, verify_github_freeze_witness
)

KEY = b"synthetic-test-only-secret-ledger-key!" * 2
NONCE = "f" * 64
COMMENT_ID = 888801
REVIEW_ID = 777701
LOGIN = "witness-operator"
REVIEWER = "independent-agent"


def sample_manifest():
    return {
        "schema_version": "v04-mla-privileged-invocation-freeze-v1",
        "study_id": "V04-MLA-1",
        "source_pack_git_blob": "4b3c9b62b1899653524f19a286924f942605210a",
        "protocol_sha256": "a" * 64,
        "scorer_sha256": "b" * 64,
        "cohort_sha256": "c" * 64,
        "case_job_sha256": "d" * 64,
        "campaign_nonce": NONCE,
        "human_selection_seed_sha256": "1" * 64,
        "source_selection_seed_sha256": "2" * 64,
        "r2_verdict_comment_id": REVIEW_ID,
        "model_input_sha256": {
            asset: {role: "e" * 64 for role in ("P", "R", "X")}
            for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice")
        },
        "eligible_j_case_ids": [],
        "budget": {
            "billing_currency": "USD",
            "max_total_input_tokens": 240_000,
            "max_total_output_tokens": 240_000,
            "max_total_cost_microunits": 240_000,
            "max_total_wall_ms": 240_000,
            "max_per_call_input_tokens": 10_000,
            "max_per_call_output_tokens": 10_000,
            "max_per_call_cost_microunits": 10_000,
            "max_per_call_wall_ms": 10_000,
        },
    }


def fake_responses(ledger, *, edited=False, duplicate=False, verdict=True, review_edited=False, mismatched_subject=False):
    events = ledger._load()
    manifest = events[0]["data"]
    body = freeze_witness_body(manifest, events[0]["mac"])
    ts = "2026-10-15T01:00:00Z"
    row = {"id": COMMENT_ID, "node_id": "I_fakeid",
           "body": body, "created_at": ts, "updated_at": ts,
           "user": {"login": LOGIN}}
    expected_subject = admission_subject_sha256(manifest)
    supplied_subject = ("e" * 64 if mismatched_subject else expected_subject)
    review = {"id": REVIEW_ID, "node_id": "I_reviewid", "body": (
        ("VERDICT=PASS_FOR_PILOT_PROVISIONAL_ONLY\n"
         + "ADMISSION_SUBJECT_SHA256=" + supplied_subject + "\n")
        if verdict else
        "VERDICT=NEEDS_REVISION\n"),
        "created_at": "2026-10-14T00:00:00Z",
        "updated_at": "2026-10-14T00:00:00Z",
        "user": {"login": REVIEWER}}
    graph = {"data": {"node": {
        "id": "I_fakeid", "createdAt": ts, "lastEditedAt": ts if edited else None,
        "author": {"login": LOGIN},
        "userContentEdits": {"totalCount": 1 if edited else 0},
    }}}
    review_graph = {"data": {"node": {
        "id": "I_reviewid",
        "createdAt": "2026-10-14T00:00:00Z",
        "lastEditedAt": "2026-10-14T00:02:00Z" if review_edited else None,
        "author": {"login": REVIEWER},
        "userContentEdits": {"totalCount": 1 if review_edited else 0},
    }}}
    matches = [row]
    if duplicate:
        matches.append(dict(row, id=COMMENT_ID + 1))
    def fetch(url, token, graphql=None):
        if url.endswith("/issues/comments/" + str(COMMENT_ID)):
            return row
        if url.endswith("/issues/comments/" + str(REVIEW_ID)):
            return review
        if graphql is not None:
            return (review_graph if graphql.get("variables", {}).get("id")
                    == "I_reviewid" else graph)
        if "per_page=100" in url:
            return matches
        raise AssertionError("unexpected synthetic URL " + url)
    return fetch


class WitnessTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.ledger = OrderedMLAHostLedger(Path(tmp.name) / "events.sqlite",
                                            host_hmac_key=KEY)
        self.addCleanup(self.ledger.close)
        self.ledger.freeze(sample_manifest())
        self.env = patch.dict(os.environ, {
            "APP8_MLA_GITHUB_WITNESS_COMMENT_ID": str(COMMENT_ID),
            "APP8_MLA_GITHUB_WITNESS_AUTHOR": LOGIN,
            "APP8_MLA_GITHUB_REVIEWER_AUTHOR": REVIEWER,
            "APP8_MLA_GITHUB_WITNESS_TOKEN": "fake-witness-github-token-for-tests",
        })
        self.env.start()
        self.addCleanup(self.env.stop)

    def verified(self, **opts):
        with patch("app8.mla.github_freeze_witness._request_json",
                   side_effect=fake_responses(self.ledger, **opts)):
            return verify_github_freeze_witness(self.ledger)

    def test_public_unedited_exact_witness_allows_only_chronology_status(self):
        report = self.verified()
        self.assertEqual(report["witness_comment_id"], COMMENT_ID)
        self.assertTrue(report["external_public_commitment_observed_before_this_dispatch"])
        self.assertFalse(report["provider_identity_independently_attested"])
        self.assertFalse(report["formal_product_release_qualified"])

    def test_edit_history_blocks_even_when_rest_body_matches(self):
        with self.assertRaisesRegex(ExternalFreezeWitnessBlocked, "edit history"):
            self.verified(edited=True)

    def test_unedited_pass_from_different_campaign_blocks(self):
        with self.assertRaisesRegex(ExternalFreezeWitnessBlocked, "reviewer"):
            self.verified(mismatched_subject=True)

    def test_admission_subject_changes_with_model_input_and_budget(self):
        m = sample_manifest()
        expected = admission_subject_sha256(m)
        modified = copy.deepcopy(m)
        modified["model_input_sha256"]["pandas"]["R"] = "f" * 64
        self.assertNotEqual(expected, admission_subject_sha256(modified))
        modified = copy.deepcopy(m)
        modified["budget"]["max_total_input_tokens"] += 1
        self.assertNotEqual(expected, admission_subject_sha256(modified))
        modified = copy.deepcopy(m)
        modified["r2_verdict_comment_id"] = REVIEW_ID + 42
        self.assertEqual(expected, admission_subject_sha256(modified))

    def test_reviewer_edit_from_needs_revision_to_pass_blocks(self):
        with self.assertRaisesRegex(ExternalFreezeWitnessBlocked, "reviewer comment"):
            self.verified(review_edited=True)

    def test_duplicate_campaign_witness_blocks(self):
        with self.assertRaisesRegex(ExternalFreezeWitnessBlocked, "duplicate"):
            self.verified(duplicate=True)

    def test_review_needs_revision_blocks(self):
        with self.assertRaisesRegex(ExternalFreezeWitnessBlocked, "reviewer"):
            self.verified(verdict=False)

    def test_missing_token_blocks_before_any_network_call(self):
        with patch.dict(os.environ, {"APP8_MLA_GITHUB_WITNESS_TOKEN": ""}):
            with self.assertRaisesRegex(ExternalFreezeWitnessBlocked, "config"):
                verify_github_freeze_witness(self.ledger)


if __name__ == "__main__":
    unittest.main()
