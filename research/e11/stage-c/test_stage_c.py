import hashlib
import json
import pathlib
import tempfile
import unittest
import importlib.util

HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("stage_c",HERE/"stage_c.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def dump(path,obj,pretty=False):
    text=json.dumps(obj,indent=2 if pretty else None,sort_keys=True)+( "\n" if pretty else "")
    path.write_text(text,encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()

def model():
    z="0"*64
    return {"provider":"test","model":"planner","version":"1","system_prompt_sha256":z,
            "sampling_sha256":z,"run_environment_sha256":z}

class StageCTest(unittest.TestCase):
    def build(self,td):
        td=pathlib.Path(td); z="1"*64
        claims=[]; n=0
        for asset in m.ASSETS:
            for klass,count in m.EXPECTED.items():
                for _ in range(count):
                    n+=1
                    claims.append({"id":f"H_{n:032x}","asset":asset,"truth_class":klass,
                                   "claim_text":"claim","binding_id":"binding",
                                   "decisive_fixture_ref":"secret","expected_behavior":"secret",
                                   "provenance":"secret","reset_requirements":"secret"})
        hidden={"schema_version":"se11-hidden-v1","execution_target_manifest_sha256":z,"claims":claims}
        hp=td/"hidden.json"; hsha=dump(hp,hidden)
        pub={"schema_version":"se11-public-commitment-v1","hidden_file_sha256":hsha,
             "opaque_claim_ids":sorted(c["id"] for c in claims)}
        pp=td/"hidden-public.json"; dump(pp,pub)
        inp=td/"planner-input.json"
        planner=m.prepare_planner_input(hp,pp,"2"*64,inp)
        self.assertNotIn("truth_class",inp.read_text())
        self.assertNotIn("expected_behavior",inp.read_text())
        plans=[{"claim_id":c["id"],"positive_probes":["p"],"falsification_probes":["f"],
                "expected_observations":["o"],"stop_conditions":["s"],"replay_requirements":["r"]}
               for c in planner["claims"]]
        plan={"schema_version":"se11-plan-v1","planner_input_sha256":hashlib.sha256(inp.read_bytes()).hexdigest(),
              "truth_visible_to_llm_b":False,"decisive_fixtures_visible_to_llm_b":False,
              "model":model(),"plans":plans}
        planp=td/"plan.json"; planhash=dump(planp,plan)
        cp=td/"plan-commit.json"; m.freeze_plan(planp,inp,cp)
        results=[]
        for c in claims:
            outcome={"TRUE":"SUPPORTED","MATERIALLY_FALSE":"REFUTED","OVERBROAD":"NARROWED","NEAR_MISS":"NARROWED"}[c["truth_class"]]
            results.append({"claim_id":c["id"],"outcome":outcome,"real_observation_present":True,
                            "promotion_without_real_observation":False,
                            "material_constraint_applicable":True,"material_constraint_discovered":True,
                            "decisive_evidence_reproducible":True,"evidence_sha256":"3"*64})
        execution={"schema_version":"se11-execution-ledger-v1","plan_file_sha256":planhash,
                   "independent_scoring":{"ground_truth_reveal_after_execution":True,
                                          "model_self_scoring":False,"review_status":"PASS"},
                   "results":results}
        ep=td/"execution.json"; dump(ep,execution)
        return hp,planp,inp,cp,ep

    def test_perfect_pass(self):
        with tempfile.TemporaryDirectory() as td:
            hp,planp,inp,cp,ep=self.build(td)
            out=pathlib.Path(td)/"result.json"
            r=m.score(ep,hp,planp,inp,cp,out)
            self.assertEqual(r["verdict"],"PASS")
            self.assertEqual(r["metrics"]["false_promotion_rate"],0.0)

    def test_false_promotion_fails(self):
        with tempfile.TemporaryDirectory() as td:
            hp,planp,inp,cp,ep=self.build(td)
            d=json.loads(ep.read_text())
            hidden=json.loads(hp.read_text())
            bad=[c["id"] for c in hidden["claims"] if c["truth_class"] in {"MATERIALLY_FALSE","OVERBROAD"}][:2]
            for r in d["results"]:
                if r["claim_id"] in bad:
                    r["outcome"]="SUPPORTED"
            dump(ep,d)
            out=pathlib.Path(td)/"result.json"
            r=m.score(ep,hp,planp,inp,cp,out)
            self.assertEqual(r["verdict"],"FAIL")
            self.assertIn("false promotion rate",r["failed_thresholds"])

    def test_more_than_15pct_blocked_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            hp,planp,inp,cp,ep=self.build(td)
            d=json.loads(ep.read_text())
            for r in d["results"][:13]:
                r["outcome"]="BLOCKED"
                r["real_observation_present"]=False
                r["decisive_evidence_reproducible"]=False
            dump(ep,d)
            out=pathlib.Path(td)/"result.json"
            r=m.score(ep,hp,planp,inp,cp,out)
            self.assertEqual(r["verdict"],"BLOCKED")

if __name__=="__main__":
    unittest.main()
