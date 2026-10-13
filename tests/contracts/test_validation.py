import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator

from app8.contracts import ContractError, parse_json, validate_contract

CAP = {"type":"object", "additionalProperties":False, "required":["schema_version", "readiness"],
       "properties":{"schema_version":{"const":"app8-capability-v1"},
                     "readiness":{"type":"object", "required":["export_ready"]}}}
EV = {"type":"object", "required":["observation", "assessment"],
      "properties":{"observation":{"type":"object", "required":["execution_status","observer"]},
                    "assessment":{"type":"object", "required":["verdict","assessor_kind"]}}}


def evidence(status="EXECUTED", verdict="SUPPORTED", assessor="DETERMINISTIC_ASSERTION_ENGINE"):
    return {"observation":{"execution_status":status, "observer":"DETERMINISTIC_EXECUTION_ADAPTER"},
            "assessment":{"verdict":verdict,"assessor_kind":assessor}}


class ContractTests(unittest.TestCase):
    def setUp(self):
        patcher = patch("app8.contracts.validation._validator", side_effect=lambda kind:
                        Draft202012Validator(CAP if kind == "capability" else EV))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_duplicate_json_rejected(self):
        with self.assertRaises(ContractError):
            parse_json('{"a":1,"a":2}')

    def test_nan_rejected(self):
        with self.assertRaises(ContractError):
            parse_json('{"a":NaN}')

    def test_wrong_root_rejected(self):
        with self.assertRaises(ContractError):
            parse_json('[]')

    def test_valid_capability_shape(self):
        c = {"schema_version":"app8-capability-v1","readiness":{"export_ready":False}}
        self.assertEqual(validate_contract("capability", c), c)

    def test_unexpected_field_rejected(self):
        with self.assertRaises(ContractError):
            validate_contract("capability", {"schema_version":"app8-capability-v1","readiness":{"export_ready":False},"extra":True})

    def test_positive_real_observation_structurally_accepted(self):
        self.assertEqual(validate_contract("evidence",evidence())["assessment"]["verdict"],"SUPPORTED")

    def test_not_run_cannot_promote(self):
        with self.assertRaises(ContractError):
            validate_contract("evidence",evidence(status="NOT_RUN"))

    def test_model_cannot_self_certify(self):
        with self.assertRaises(ContractError):
            validate_contract("evidence",evidence(assessor="MODEL_PROPOSAL_ONLY"))

    def test_refutation_not_suppressed(self):
        self.assertEqual(validate_contract("evidence",evidence(status="BLOCKED",verdict="REFUTED"))["assessment"]["verdict"],"REFUTED")

if __name__ == "__main__":
    unittest.main()
