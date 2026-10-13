#!/usr/bin/env python3
"""Repeatable offline source/packaging preflight. Never asserts real-host Release PASS."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SUITES = ("contracts", "storage", "readiness", "discovery", "orchestration",
          "execution", "projections", "search", "integration")
SCHEMAS = ("capability-v1.schema.json", "evidence-v1.schema.json")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False,
                          timeout=90)


def preflight() -> dict:
    record = {"schema_version":"app8-local-preflight-v1",
              "python":platform.python_version(), "platform":platform.system(),
              "source_tests_pass":False,"schema_parity_pass":False,"wheel_pass":False,
              "test_count":0,"test_suites":{},"frozen_schema_sha256":{},
              "wheel_sha256":None,"real_host_sandbox_verified":False,
              "libreoffice_phase2_evidence_imported":False,
              "empirical_se10_se11_pass":False,"release_qualified":False,"errors":[]}
    for name in SCHEMAS:
        packaged=ROOT/"app8"/"contracts"/"schemas"/name
        authority=ROOT/"docs"/"architecture"/"v0.1-successor"/"contracts"/name
        if not packaged.is_file() or not authority.is_file() or digest(packaged)!=digest(authority):
            record["errors"].append(f"SCHEMA_PARITY_MISMATCH:{name}")
        else:
            record["frozen_schema_sha256"][name]=digest(authority)
    record["schema_parity_pass"]=len(record["frozen_schema_sha256"])==len(SCHEMAS)

    for suite in SUITES:
        result=run(sys.executable,"-m","unittest","discover","-s",f"tests/{suite}","-p","test_*.py","-v")
        output=result.stdout+result.stderr
        match=re.search(r"Ran (\d+) tests?",output)
        count=int(match.group(1)) if match else 0
        ok=result.returncode==0 and count>0 and "FAILED" not in output
        record["test_suites"][suite]={"pass":ok,"count":count}
        record["test_count"]+=count
        if not ok:
            record["errors"].append(f"TEST_SUITE_FAIL:{suite}")
    record["source_tests_pass"]=all(x["pass"] for x in record["test_suites"].values())

    with tempfile.TemporaryDirectory(prefix="app8-wheel-") as temp:
        wheel=run(sys.executable,"-m","pip","wheel","--disable-pip-version-check",
                  "--no-index","--no-deps","--no-build-isolation","--wheel-dir",temp,".")
        paths=list(Path(temp).glob("*.whl"))
        if wheel.returncode!=0 or len(paths)!=1:
            record["errors"].append("WHEEL_BUILD_FAILED_OFFLINE")
        else:
            archive=paths[0]
            with zipfile.ZipFile(archive) as z:
                members=set(z.namelist())
                for name in SCHEMAS:
                    path=f"app8/contracts/schemas/{name}"
                    if path not in members or hashlib.sha256(z.read(path)).hexdigest()!=record["frozen_schema_sha256"].get(name):
                        record["errors"].append(f"WHEEL_SCHEMA_NOT_FROZEN:{name}")
                entries=[name for name in members if name.endswith("entry_points.txt")]
                if len(entries)!=1 or "app8 = app8.cli.main:main" not in z.read(entries[0]).decode("utf-8"):
                    record["errors"].append("WHEEL_CLI_ENTRYPOINT_MISSING")
            if not any(e.startswith("WHEEL_") for e in record["errors"]):
                record["wheel_pass"]=True
                record["wheel_sha256"]=digest(archive)
    record["local_source_package_pass"]=(record["source_tests_pass"] and
                                           record["schema_parity_pass"] and record["wheel_pass"])
    return record


def main(argv=None) -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args(argv)
    terminal=preflight()
    Path(args.out).write_text(json.dumps(terminal,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("LOCAL_SOURCE_PACKAGE="+("PASS" if terminal["local_source_package_pass"] else "FAIL"))
    print("RELEASE_QUALIFIED=NO")
    return 0 if terminal["local_source_package_pass"] else 2


if __name__=="__main__":
    raise SystemExit(main())
