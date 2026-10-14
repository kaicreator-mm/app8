"""Host-local SQLite HMAC chronology tests; synthetic events, NO real provider."""
import copy
import hashlib
from pathlib import Path
import sqlite3
import tempfile
import unittest

from app8.mla.ordered_host_ledger import OrderedMLAHostLedger, MLAChronologyBlocked

KEY = b"local-host-private-test-only!" * 2
H = "a" * 64


def freeze():
    return {
        "schema_version": "v04-mla-privileged-invocation-freeze-v1",
        "study_id": "V04-MLA-1", "source_pack_git_blob":
            "4b3c9b62b1899653524f19a286924f942605210a",
        "protocol_sha256": "b" * 64, "scorer_sha256": "c" * 64,
        "cohort_sha256": "d" * 64, "case_job_sha256": "e" * 64,
        "model_input_sha256": {
            asset: {role: hashlib.sha256((asset + role).encode()).hexdigest()
                    for role in ("P", "R", "X")}
            for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice")
        },
        "eligible_j_case_ids": ["V04-FFMPEG-001"],
        "budget": {
            "billing_currency": "USD",
            "max_total_input_tokens": 500_000, "max_total_output_tokens": 500_000,
            "max_total_cost_microunits": 500_000_000,
            "max_total_wall_ms": 500_000,
            "max_per_call_input_tokens": 10_000,
            "max_per_call_output_tokens": 10_000,
            "max_per_call_cost_microunits": 10_000_000,
            "max_per_call_wall_ms": 10_000,
        },
    }


def usage():
    return {"input_tokens": 100, "output_tokens": 200,
            "cost_microunits": 1000, "wall_ms": 400}


def call(l, manifest, *, role="P", asset="FFmpeg", case_id=None):
    request = manifest["model_input_sha256"][asset][role]
    reserve = l.reserve(role=role, asset=asset, case_id=case_id, request_sha256=request)
    return l.record_response(reserve_seq=reserve["seq"], response_sha256=H, usage=usage())


class LocalHostChronologyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "mla.db"
        self.l = OrderedMLAHostLedger(self.db, host_hmac_key=KEY)
        self.addCleanup(self.l.close)

    def test_freeze_then_provider_reception_sequenced(self):
        m = freeze()
        event = self.l.freeze(m)
        self.assertFalse(event["external_time_witness_verified"])
        response = call(self.l, m)
        self.assertFalse(response["provider_receipt_independently_authenticated"])
        audit = self.l.audit()
        self.assertEqual(audit["event_count"], 3)
        self.assertEqual(audit["reservation_count"], 1)
        self.assertEqual(audit["response_count"], 1)
        self.assertFalse(audit["formal_product_release_qualified"])

    def test_provider_reservation_requires_freeze(self):
        m = freeze()
        with self.assertRaisesRegex(MLAChronologyBlocked, "no committed"):
            self.l.reserve(role="P", asset="FFmpeg", case_id=None,
                           request_sha256=m["model_input_sha256"]["FFmpeg"]["P"])

    def test_freeze_cannot_be_changed_or_refrozen(self):
        self.l.freeze(freeze())
        with self.assertRaisesRegex(MLAChronologyBlocked, "already frozen"):
            self.l.freeze(freeze())

    def test_duplicate_model_invocation_rejected(self):
        m = freeze()
        self.l.freeze(m)
        call(self.l, m)
        with self.assertRaisesRegex(MLAChronologyBlocked, "replay"):
            self.l.reserve(role="P", asset="FFmpeg", case_id=None,
                           request_sha256=m["model_input_sha256"]["FFmpeg"]["P"])

    def test_outstanding_ambiguous_call_stops_next(self):
        m = freeze()
        self.l.freeze(m)
        self.l.reserve(role="P", asset="FFmpeg", case_id=None,
                       request_sha256=m["model_input_sha256"]["FFmpeg"]["P"])
        with self.assertRaisesRegex(MLAChronologyBlocked, "outstanding"):
            self.l.reserve(role="R", asset="FFmpeg", case_id=None,
                           request_sha256=m["model_input_sha256"]["FFmpeg"]["R"])

    def test_swapped_request_digest_fails(self):
        m = freeze()
        self.l.freeze(m)
        with self.assertRaisesRegex(MLAChronologyBlocked, "input mismatch"):
            self.l.reserve(role="P", asset="FFmpeg", case_id=None, request_sha256=H)

    def test_response_replay_fails(self):
        m = freeze()
        self.l.freeze(m)
        res = self.l.reserve(role="P", asset="FFmpeg", case_id=None,
                             request_sha256=m["model_input_sha256"]["FFmpeg"]["P"])
        self.l.record_response(reserve_seq=res["seq"], response_sha256=H, usage=usage())
        with self.assertRaisesRegex(MLAChronologyBlocked, "replayed"):
            self.l.record_response(reserve_seq=res["seq"], response_sha256=H, usage=usage())

    def test_bad_usage_is_denied_and_reservation_remains_pending(self):
        m = freeze()
        self.l.freeze(m)
        res = self.l.reserve(role="P", asset="FFmpeg", case_id=None,
                             request_sha256=m["model_input_sha256"]["FFmpeg"]["P"])
        x = usage()
        x["cost_microunits"] = 20_000_000
        with self.assertRaisesRegex(MLAChronologyBlocked, "exceeds reserved"):
            self.l.record_response(reserve_seq=res["seq"], response_sha256=H, usage=x)
        with self.assertRaisesRegex(MLAChronologyBlocked, "outstanding"):
            self.l.reserve(role="R", asset="FFmpeg", case_id=None,
                           request_sha256=m["model_input_sha256"]["FFmpeg"]["R"])

    def test_second_connection_preserves_order(self):
        m = freeze()
        self.l.freeze(m)
        call(self.l, m)
        with OrderedMLAHostLedger(self.db, host_hmac_key=KEY) as other:
            self.assertEqual(other.audit()["event_count"], 3)

    def test_modified_persisted_event_is_rejected(self):
        m = freeze()
        self.l.freeze(m)
        # Test-only bypass of SQL triggers, equivalent to attacker replacing DB.
        self.l.db.execute("DROP TRIGGER mla_host_events_no_update")
        self.l.db.execute("UPDATE mla_host_events SET payload=? WHERE seq=1",
                          (b'{"tampered":true}\n',))
        with self.assertRaisesRegex(MLAChronologyBlocked, "MAC"):
            self.l.audit()

    def test_wrong_key_detected(self):
        m = freeze()
        self.l.freeze(m)
        with OrderedMLAHostLedger(self.db, host_hmac_key=b"other-private-key" * 3) as other:
            with self.assertRaisesRegex(MLAChronologyBlocked, "MAC"):
                other.audit()

    def test_missing_budget_or_nonfinite_fails(self):
        m = freeze()
        del m["budget"]["max_total_wall_ms"]
        with self.assertRaisesRegex(MLAChronologyBlocked, "budget"):
            self.l.freeze(m)

    def test_budget_fail_closed_before_provider_reservation(self):
        m = freeze()
        m["budget"]["max_total_wall_ms"] = 10_000
        self.l.freeze(m)
        call(self.l, m)
        with self.assertRaisesRegex(MLAChronologyBlocked, "resource reservation"):
            self.l.reserve(role="R", asset="FFmpeg", case_id=None,
                           request_sha256=m["model_input_sha256"]["FFmpeg"]["R"])

    def test_j_call_requires_all_12_baseline_reservations(self):
        m = freeze()
        self.l.freeze(m)
        with self.assertRaisesRegex(MLAChronologyBlocked, "baseline"):
            self.l.reserve(role="J", asset="FFmpeg", case_id="V04-FFMPEG-001",
                           request_sha256=H)

    def test_j_after_complete_base_is_locally_ordered_not_authoritative(self):
        m = freeze()
        self.l.freeze(m)
        for role in ("P", "R", "X"):
            for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice"):
                call(self.l, m, role=role, asset=asset)
        res = self.l.reserve(role="J", asset="FFmpeg", case_id="V04-FFMPEG-001",
                             request_sha256=H)
        self.l.record_response(reserve_seq=res["seq"], response_sha256=H,
                               usage=usage())
        self.assertEqual(self.l.audit()["reservation_count"], 13)
        self.assertFalse(self.l.audit()["provider_receipt_independently_authenticated"])


if __name__ == "__main__":
    unittest.main()
