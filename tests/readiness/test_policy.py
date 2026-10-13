import copy
import unittest
from app8.readiness import evaluate_readiness

Z="0"*64


def base():
    src={"repository":"fixture", "revision":"pinned", "content_sha256":Z}
    target={"identity":"python", "package_sha256":Z, "environment_id":"test", "mapping_relation":"SAME"}
    cap={"capability_id":"cap:0000", "source":src, "target":target,
         "bindings":[{"binding_id":"binding:1"}], "evidence_refs":["ev:1"],
         "readiness":{"export_ready":True,"lifecycle_state":"EXPORT_READY"}}
    ev={"evidence_id":"ev:1", "source":src.copy(), "target":target.copy(),
        "plan":{"binding_id":"binding:1", "assertions":["output valid"]},
        "observation":{"execution_status":"EXECUTED", "observer":"DETERMINISTIC_EXECUTION_ADAPTER", "exit_code":0},
        "assessment":{"verdict":"SUPPORTED", "assessor_kind":"DETERMINISTIC_ASSERTION_ENGINE", "reason_codes":["ASSERTIONS_PASSED"]}}
    return cap,ev


class PolicyTests(unittest.TestCase):
    def test_default_unverified_cannot_export(self):
        cap,ev=base()
        r=evaluate_readiness(cap,[])
        self.assertFalse(r.export_ready)
        self.assertIn("NO_QUALIFIED_POSITIVE_EVIDENCE",r.reason_codes)

    def test_observed_not_export_without_projections(self):
        cap,ev=base()
        r=evaluate_readiness(cap,[ev])
        self.assertEqual(r.lifecycle_state,"EVIDENCED")
        self.assertFalse(r.export_ready)

    def test_verified_evidence_and_projection(self):
        cap,ev=base()
        r=evaluate_readiness(cap,[ev],projection_verifier=lambda _:True)
        self.assertTrue(r.export_ready)
        self.assertEqual(r.qualified_evidence_ids,("ev:1",))

    def test_model_observation_disallowed(self):
        cap,ev=base(); ev["assessment"]["assessor_kind"]="MODEL_PROPOSAL_ONLY"
        self.assertFalse(evaluate_readiness(cap,[ev],projection_verifier=lambda _:True).export_ready)

    def test_not_run_disallowed(self):
        cap,ev=base(); ev["observation"]["execution_status"]="NOT_RUN"
        self.assertFalse(evaluate_readiness(cap,[ev],projection_verifier=lambda _:True).export_ready)

    def test_refutation_cannot_be_overridden(self):
        cap,ev=base()
        r=evaluate_readiness(cap,[ev],[{"kind":"REFUTED","payload":{"reason":"real counterexample"}}],projection_verifier=lambda _:True)
        self.assertEqual(r.lifecycle_state,"BLOCKED")
        self.assertFalse(r.export_ready)

    def test_stale_target_blocked(self):
        cap,ev=base(); ev["target"]["package_sha256"]="f"*64
        self.assertFalse(evaluate_readiness(cap,[ev],projection_verifier=lambda _:True).export_ready)

    def test_diverged_requires_applicability(self):
        cap,ev=base()
        cap["target"]["mapping_relation"]="DIVERGED"
        ev["target"]["mapping_relation"]="DIVERGED"
        self.assertFalse(evaluate_readiness(cap,[ev],projection_verifier=lambda _:True).export_ready)
        observed=evaluate_readiness(cap,[ev],[{"kind":"TARGET_APPLICABILITY_CONFIRMED","payload":{"package_sha256":Z}}],projection_verifier=lambda _:True)
        self.assertTrue(observed.export_ready)

    def test_exit_zero_without_assertions_not_success(self):
        cap,ev=base(); ev["plan"]["assertions"]=[]
        self.assertFalse(evaluate_readiness(cap,[ev],projection_verifier=lambda _:True).export_ready)

    def test_unlisted_binding_rejected(self):
        cap,ev=base(); ev["plan"]["binding_id"]="other"
        self.assertFalse(evaluate_readiness(cap,[ev],projection_verifier=lambda _:True).export_ready)

if __name__=="__main__":
    unittest.main()
