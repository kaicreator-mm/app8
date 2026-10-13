import copy
import unittest
from app8.projections import ProjectionError, build_projections, verify_projection_suite
from app8.readiness import Readiness

Z="0"*64


def cap():
    return {"capability_id":"cap:csvread", "revision":1,
            "semantic":{"name":"Read CSV", "purpose":"Read delimited files", "user_job":"Inspect CSV", "inputs":["path"], "outputs":["rows"],
                        "variants":[], "constraints":["UTF-8"], "negative_boundaries":["no missing files"],
                        "failure_modes":["missing path"], "side_effects":[]},
            "bindings":[{"kind":"CLI", "address":"csvread", "binding_id":"b1"}]}


def ready(value=False):
    return Readiness("EXPORT_READY" if value else "HYPOTHESIZED",value,(),())


class ProjectionTests(unittest.TestCase):
    def test_all_five_frozen_projections(self):
        result=build_projections(cap(),ready(),Z)
        self.assertEqual(set(result),{"CLI","MCP","SKILL","DOCS","SEARCH"})
        self.assertTrue(verify_projection_suite(cap(),Z,result))

    def test_model_prose_unready(self):
        result=build_projections(cap(),ready(),Z)
        self.assertTrue(all(not p["invocation_enabled"] for p in result.values()))
        self.assertTrue(all(p["status"]=="UNREADY" for p in result.values()))

    def test_verified_readiness_enables_cli_mcp_only(self):
        result=build_projections(cap(),ready(True),Z)
        self.assertTrue(result["CLI"]["invocation_enabled"])
        self.assertTrue(result["MCP"]["invocation_enabled"])
        self.assertFalse(result["SKILL"]["invocation_enabled"])

    def test_semantic_revision_tamper_detected(self):
        c=cap();result=build_projections(c,ready(),Z)
        c["revision"]=2
        self.assertFalse(verify_projection_suite(c,Z,result))

    def test_evidence_snapshot_tamper_detected(self):
        result=build_projections(cap(),ready(),Z)
        self.assertFalse(verify_projection_suite(cap(),"f"*64,result))

    def test_projection_semantic_tamper_detected(self):
        c=cap();result=build_projections(c,ready(),Z)
        result["DOCS"]["semantic"]["constraints"].append("model edit")
        self.assertFalse(verify_projection_suite(c,Z,result))

    def test_unsupported_cli_declared(self):
        c=cap();c["bindings"]=[]
        result=build_projections(c,ready(True),Z)
        self.assertEqual(result["CLI"]["status"],"UNSUPPORTED_PROJECTION")
        self.assertFalse(verify_projection_suite(c,Z,result))

    def test_pixel_binding_rejected(self):
        c=cap();c["bindings"].append({"kind":"PIXEL"})
        with self.assertRaises(ProjectionError):build_projections(c,ready(),Z)

    def test_no_evidence_snapshot_hash_rejected(self):
        with self.assertRaises(ProjectionError):build_projections(cap(),ready(),"not-a-hash")

    def test_untrusted_render_does_not_mutate_capability(self):
        c=cap();before=copy.deepcopy(c)
        build_projections(c,ready(),Z)
        self.assertEqual(c,before)

if __name__=="__main__":unittest.main()
