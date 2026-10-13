import hashlib
import json
import pathlib
import tempfile
import unittest
import importlib.util

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("stage_c", HERE / "stage_c.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def dump(path, obj):
    path.write_text(json.dumps(obj, sort_keys=True), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()

def model():
    z = "0"*64
    return {"provider":"test","model":"understand","version":"1","system_prompt_sha256":z,
            "sampling_sha256":z,"run_environment_sha256":z}

class StageCTest(unittest.TestCase):
    def build(self, td, ambiguous_count=0):
        td=pathlib.Path(td)
        gold_caps=[]
        n=1
        for asset in m.ASSETS:
            for _ in range(12):
                gold_caps.append({"id":f"G{n:04d}","asset":asset,"ambiguity":False})
                n+=1
        for g in gold_caps[:ambiguous_count]:
            g["ambiguity"]=True
        gold={"schema_version":"se10-gold-v1","source_pack_blob":m.SOURCE_PACK_BLOB,
              "capabilities":gold_caps}
        goldp=td/"gold.json"; goldsha=dump(goldp,gold)
        public={"schema_version":"se10-public-commitment-v1","source_pack_blob":m.SOURCE_PACK_BLOB,
                "gold_file_sha256":goldsha,"capability_count":48,
                "asset_counts":{a:12 for a in m.ASSETS}}
        pubp=td/"gold-public.json"; pubsha=dump(pubp,public)
        preds=[]
        for i,g in enumerate(gold_caps,1):
            preds.append({"id":f"P{i:04d}","asset":g["asset"],"semantic_name":"x","purpose":"x",
                          "user_job":"x","inputs":[],"outputs":[],"variants":[],"constraints":[],
                          "failure_semantics":["x"],"side_effects":[],"candidate_bindings":[],
                          "provenance_refs":["x"]})
        pred={"schema_version":"se10-prediction-v1","source_pack_blob":m.SOURCE_PACK_BLOB,
              "gold_commitment_sha256":pubsha,"predictor_gold_visibility":False,
              "model":model(),"capabilities":preds}
        predp=td/"pred.json"; predsha=dump(predp,pred)
        cp=td/"pred-commit.json"; m.freeze_prediction(predp,pubp,cp)
        judgments=[]
        for i,p in enumerate(preds,1):
            judgments.append({"prediction_id":p["id"],"classification":"MATCH",
                              "matched_gold_ids":[f"G{i:04d}"],
                              "material_failure_semantics_applicable":True,
                              "material_failure_semantics_preserved":True,
                              "materially_incompatible_confident_equivalent_merge":False})
        adj={"schema_version":"se10-adjudication-v1","prediction_file_sha256":predsha,
             "gold_file_sha256":goldsha,
             "independent_adjudication":{"primary_passes":2,
                 "third_adjudicator_on_disagreement":True,"model_self_scoring":False,
                 "review_status":"PASS"},
             "prediction_judgments":judgments,
             "gold_coverage":[{"gold_id":g["id"],"coverage":"FULL"} for g in gold_caps]}
        adjp=td/"adj.json"; dump(adjp,adj)
        return goldp,pubp,predp,cp,adjp

    def test_perfect_pass(self):
        with tempfile.TemporaryDirectory() as td:
            gold,goldpub,pred,cp,adj=self.build(td)
            out=pathlib.Path(td)/"result.json"
            r=m.score(adj,pred,gold,goldpub,cp,out)
            self.assertEqual(r["verdict"],"PASS")
            self.assertEqual(r["pooled"]["precision"],1.0)
            self.assertEqual(r["pooled"]["coverage"],1.0)

    def test_hallucination_threshold_fails(self):
        with tempfile.TemporaryDirectory() as td:
            gold,goldpub,pred,cp,adj=self.build(td)
            d=json.loads(pathlib.Path(adj).read_text())
            for j in d["prediction_judgments"][:6]:
                j["classification"]="HALLUCINATED"
                j["matched_gold_ids"]=[]
            dump(pathlib.Path(adj),d)
            out=pathlib.Path(td)/"result.json"
            r=m.score(adj,pred,gold,goldpub,cp,out)
            self.assertEqual(r["verdict"],"FAIL")
            self.assertIn("hallucination_rate",r["failed_thresholds"])

    def test_ambiguity_over_15_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            gold,goldpub,pred,cp,adj=self.build(td, ambiguous_count=8)
            ad=json.loads(pathlib.Path(adj).read_text())
            for row in ad["gold_coverage"][:8]:
                row["coverage"]="EXCLUDED_AMBIGUOUS"
            dump(pathlib.Path(adj),ad)
            out=pathlib.Path(td)/"result.json"
            r=m.score(adj,pred,gold,goldpub,cp,out)
            self.assertEqual(r["verdict"],"BLOCKED")

    def test_ambiguous_cannot_hide_nonambiguous_predictions(self):
        with tempfile.TemporaryDirectory() as td:
            gold, goldpub, pred, cp, adj = self.build(td)
            d = json.loads(pathlib.Path(adj).read_text())
            d["prediction_judgments"][0]["classification"] = "AMBIGUOUS"
            dump(pathlib.Path(adj), d)
            with self.assertRaises(SystemExit):
                m.score(adj, pred, gold, goldpub, cp, pathlib.Path(td)/"result.json")

    def test_match_requires_gold_link(self):
        with tempfile.TemporaryDirectory() as td:
            gold, goldpub, pred, cp, adj = self.build(td)
            d = json.loads(pathlib.Path(adj).read_text())
            d["prediction_judgments"][0]["matched_gold_ids"] = []
            dump(pathlib.Path(adj), d)
            with self.assertRaises(SystemExit):
                m.score(adj, pred, gold, goldpub, cp, pathlib.Path(td)/"result.json")

    def test_cross_asset_gold_match_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            gold, goldpub, pred, cp, adj = self.build(td)
            d = json.loads(pathlib.Path(adj).read_text())
            d["prediction_judgments"][0]["matched_gold_ids"] = ["G0013"]
            dump(pathlib.Path(adj), d)
            with self.assertRaises(SystemExit):
                m.score(adj, pred, gold, goldpub, cp, pathlib.Path(td)/"result.json")

    def test_full_coverage_requires_matching_prediction(self):
        with tempfile.TemporaryDirectory() as td:
            gold, goldpub, pred, cp, adj = self.build(td)
            d = json.loads(pathlib.Path(adj).read_text())
            d["prediction_judgments"][0]["classification"] = "HALLUCINATED"
            d["prediction_judgments"][0]["matched_gold_ids"] = []
            dump(pathlib.Path(adj), d)
            with self.assertRaises(SystemExit):
                m.score(adj, pred, gold, goldpub, cp, pathlib.Path(td)/"result.json")

if __name__ == "__main__":
    unittest.main()
