import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from app8.cli.main import compile_preview, main
from app8.discovery import discover_source
from app8.orchestration import freeze_hypotheses

Z="0"*64


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir=Path(self.tmp.name)
        (self.dir/"source.md").write_text("Read data",encoding="utf-8")
        h=hashlib.sha256((self.dir/"source.md").read_bytes()).hexdigest()
        src=discover_source(self.dir,"source.md",repository="example",revision="123",expected_sha256=h)
        hypotheses={"schema_version":"app8-hypotheses-v1","source_sha256":h,"source_revision":"123",
                    "hypotheses":[{"id":"CSVREAD","user_job":"Read CSV","surface":"CLI",
                                   "constraints":[],"source_anchor":"source.md:1"}]}
        (self.dir/"hyp.json").write_text(json.dumps(hypotheses),encoding="utf-8")
        frozen=freeze_hypotheses(hypotheses,src)
        plan={"schema_version":"app8-plan-v1","hypothesis_sha256":frozen["proposal_sha256"],
              "target_sha256":Z,"probes":[{"hypothesis_id":"CSVREAD","positive":["run positive"],
              "falsifying":["run negative"],"timeout_seconds":5,"network_allowed":False,"mutation_allowed":False}]}
        (self.dir/"plan.json").write_text(json.dumps(plan),encoding="utf-8")
        self.args=["--root",str(self.dir),"--path","source.md","--repository","example", "--revision","123",
                   "--source-sha256",h,"--hypotheses",str(self.dir/"hyp.json"),"--plan",str(self.dir/"plan.json"),
                   "--target","fixture", "--target-sha256",Z,"--environment","isolated"]

    def test_compile_without_fake_evidence(self):
        import argparse
        p=self.args
        args=argparse.Namespace(root=p[1],path=p[3],repository=p[5],revision=p[7],source_sha256=p[9],
                                hypotheses=p[11],plan=p[13],target=p[15],target_sha256=p[17],environment=p[19],
                                query="csv",out=None)
        output=compile_preview(args)
        self.assertEqual(output["real_execution_status"],"NOT_RUN")
        self.assertFalse(output["release_ready"])
        self.assertFalse(output["capabilities"][0]["export_ready"])
        self.assertEqual(output["search_results"],["cap:csvread"])
        self.assertEqual(output["capabilities"][0]["projection_status"]["CLI"],"UNSUPPORTED_PROJECTION")

    def test_cli_roundtrip(self):
        output=self.dir/"out.json"
        rc=main(self.args+["--out",str(output)])
        self.assertEqual(rc,0)
        self.assertEqual(json.loads(output.read_text())["evidence_status"],"NOT_AVAILABLE")

    def test_source_tamper_blocks(self):
        (self.dir/"source.md").write_text("Changed",encoding="utf-8")
        self.assertEqual(main(self.args),2)

    def test_invalid_model_plan_blocks(self):
        plan=json.loads((self.dir/"plan.json").read_text());plan["probes"][0]["falsifying"]=[]
        (self.dir/"plan.json").write_text(json.dumps(plan),encoding="utf-8")
        self.assertEqual(main(self.args),2)

    def test_overlong_capability_id_blocks(self):
        data=json.loads((self.dir/"hyp.json").read_text())
        data["hypotheses"][0]["id"]="A"*200
        (self.dir/"hyp.json").write_text(json.dumps(data),encoding="utf-8")
        self.assertEqual(main(self.args),2)

    def test_target_hash_change_blocks(self):
        bad=list(self.args);bad[17]="f"*64
        self.assertEqual(main(bad),2)

if __name__=="__main__":unittest.main()
