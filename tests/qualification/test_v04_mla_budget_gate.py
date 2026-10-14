"""Model call budget is source-only preflight, not provider billing proof."""
import unittest

from scripts.v04_mla_budget_gate import check_budget
from scripts.v04_mla_pilot_reducer import PilotBlocked


def config():
    return {
        "max_calls": 24, "max_j_calls": 12, "billing_currency": "USD",
        "max_total_input_tokens": 1_000_000,
        "max_total_output_tokens": 1_000_000,
        "max_total_cost_microunits": 200_000_000,
        "max_total_wall_ms": 2_000_000,
        "max_per_call_input_tokens": 100_000,
        "max_per_call_output_tokens": 100_000,
        "max_per_call_cost_microunits": 10_000_000,
        "max_per_call_wall_ms": 100_000,
    }


def cases():
    return {f"V04-{asset.upper()}-{i:03d}"
            for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice")
            for i in range(1, 7)}


def call(role, asset, case_id=None):
    return {"role": role, "asset": asset, "case_id": case_id,
            "input_tokens": 100, "output_tokens": 100,
            "cost_microunits": 1000, "wall_ms": 1000}


def base_calls():
    return [call(role, asset) for role in ("P", "R", "X")
            for asset in ("FFmpeg", "pandas", "MinIO", "LibreOffice")]


class ModelSpendPreflightTests(unittest.TestCase):
    def test_exact_12_base_are_structurally_within_caps(self):
        r = check_budget(config(), base_calls(), frozen_case_ids=cases(),
                         eligible_j_case_ids=set())
        self.assertEqual(r["base_calls_reported"], 12)
        self.assertFalse(r["trusted_usage_and_provider_identity_verified"])
        self.assertFalse(r["formal_product_release_qualified"])

    def test_missing_baseline_is_blocked(self):
        r = check_budget(config(), base_calls()[:-1],
                         frozen_case_ids=cases(), eligible_j_case_ids=set())
        self.assertEqual(r["status"], "BLOCKED_BASELINE_PROVIDER_CALLS_INCOMPLETE")

    def test_missing_numeric_budget_is_rejected(self):
        c = config()
        c.pop("max_total_wall_ms")
        with self.assertRaisesRegex(PilotBlocked, "complete"):
            check_budget(c, [], frozen_case_ids=cases(), eligible_j_case_ids=set())

    def test_boolean_budget_not_accepted_as_int(self):
        c = config()
        c["max_per_call_wall_ms"] = True
        with self.assertRaisesRegex(PilotBlocked, "fixed budget"):
            check_budget(c, [], frozen_case_ids=cases(), eligible_j_case_ids=set())

    def test_billing_currency_required_and_uppercase(self):
        c = config()
        c["billing_currency"] = "usd"
        with self.assertRaisesRegex(PilotBlocked, "fixed budget"):
            check_budget(c, [], frozen_case_ids=cases(), eligible_j_case_ids=set())

    def test_wrong_j_cap_rejected(self):
        c = config()
        c["max_j_calls"] = 24
        with self.assertRaisesRegex(PilotBlocked, "fixed budget"):
            check_budget(c, [], frozen_case_ids=cases(), eligible_j_case_ids=set())

    def test_more_than_12_j_denied(self):
        ids = sorted(cases())
        calls = base_calls() + [call("J", "FFmpeg", f"V04-FFMPEG-{i:03d}")
                                for i in range(1, 7)]
        calls += [call("J", "pandas", f"V04-PANDAS-{i:03d}")
                  for i in range(1, 7)]
        r = check_budget(config(), calls, frozen_case_ids=cases(),
                         eligible_j_case_ids=cases())
        self.assertEqual(r["j_calls_reported"], 12)
        calls.append(call("J", "MinIO", "V04-MINIO-001"))
        with self.assertRaisesRegex(PilotBlocked, "call ceiling"):
            check_budget(config(), calls, frozen_case_ids=cases(),
                         eligible_j_case_ids=cases())

    def test_duplicate_j_rejected(self):
        j = call("J", "MinIO", "V04-MINIO-001")
        with self.assertRaisesRegex(PilotBlocked, "duplicate"):
            check_budget(config(), base_calls() + [j, j],
                         frozen_case_ids=cases(), eligible_j_case_ids=cases())

    def test_noneligible_j_rejected(self):
        with self.assertRaisesRegex(PilotBlocked, "eligible"):
            check_budget(config(), base_calls() +
                         [call("J", "MinIO", "V04-MINIO-001")],
                         frozen_case_ids=cases(), eligible_j_case_ids=set())

    def test_duplicate_base_rejected(self):
        with self.assertRaisesRegex(PilotBlocked, "duplicated"):
            check_budget(config(), base_calls() + [base_calls()[0]],
                         frozen_case_ids=cases(), eligible_j_case_ids=set())

    def test_single_call_overflow_denied(self):
        calls = base_calls()
        calls[0]["output_tokens"] = 100_001
        with self.assertRaisesRegex(PilotBlocked, "per-call"):
            check_budget(config(), calls, frozen_case_ids=cases(),
                         eligible_j_case_ids=set())

    def test_aggregate_cost_overflow_denied(self):
        c = config()
        c["max_total_cost_microunits"] = 10_000_000
        calls = base_calls()
        for row in calls:
            row["cost_microunits"] = 1_000_000
        with self.assertRaisesRegex(PilotBlocked, "aggregate"):
            check_budget(c, calls, frozen_case_ids=cases(),
                         eligible_j_case_ids=set())

    def test_negative_usage_denied(self):
        calls = base_calls()
        calls[0]["wall_ms"] = -1
        with self.assertRaisesRegex(PilotBlocked, "usage invalid"):
            check_budget(config(), calls, frozen_case_ids=cases(),
                         eligible_j_case_ids=set())

    def test_private_usage_field_rejected(self):
        calls = base_calls()
        calls[0]["api_key"] = "private"
        with self.assertRaisesRegex(PilotBlocked, "private"):
            check_budget(config(), calls, frozen_case_ids=cases(),
                         eligible_j_case_ids=set())

    def test_asset_case_mismatch_rejected(self):
        with self.assertRaisesRegex(PilotBlocked, "eligible"):
            check_budget(config(), base_calls() +
                         [call("J", "pandas", "V04-MINIO-001")],
                         frozen_case_ids=cases(), eligible_j_case_ids=cases())


if __name__ == "__main__":
    unittest.main()
