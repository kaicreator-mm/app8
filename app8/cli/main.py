"""Compile source hypotheses into disabled preview projections, not fake Evidence."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

from app8.contracts import ContractError
from app8.discovery import SourceError, discover_source
from app8.orchestration import PlanError, freeze_hypotheses, freeze_falsification_plan
from app8.projections import build_projections
from app8.readiness import evaluate_readiness
from app8.search import CapabilityIndex


def _candidate_capability(item: dict, *, source, target: str, target_hash: str, environment: str) -> dict:
    # Inputs/outputs/bindings not observed. Do not promote model assertions.
    cid = "cap:" + re.sub(r"[^a-z0-9._-]", "-", item["id"].lower()).strip("-")
    if len(cid) < 8:
        cid += "-0000"
    if len(cid) > 128:
        raise PlanError("model-supplied Capability ID exceeds contract length")
    return {
        "schema_version":"app8-capability-v1", "capability_id":cid, "revision":1,
        "semantic":{"name":item["user_job"], "purpose":item["user_job"], "user_job":item["user_job"],
                    "inputs":[],"outputs":[],"variants":[],"constraints":item["constraints"],
                    "negative_boundaries":[],"failure_modes":[],"side_effects":[]},
        "source":{"repository":source.repository,"revision":source.revision,"content_sha256":source.content_sha256,
                  "license_disposition":"UNKNOWN"},
        "target":{"identity":target,"package_sha256":target_hash,"environment_id":environment,
                  "mapping_relation":"UNRESOLVED"},
        "bindings":[],"evidence_refs":[],
        "readiness":{"lifecycle_state":"HYPOTHESIZED","export_ready":False,
                     "derived_by_policy":True,"policy_revision":"t03-v1","reason_codes":["REAL_EXECUTION_NOT_RUN"]},
        "projection_refs":[]
    }


def compile_preview(args: argparse.Namespace) -> dict:
    source = discover_source(args.root, args.path, repository=args.repository, revision=args.revision,
                             expected_sha256=args.source_sha256)
    proposal = freeze_hypotheses(Path(args.hypotheses).read_bytes(),source)
    plan = freeze_falsification_plan(Path(args.plan).read_bytes(),proposal,args.target_sha256)
    evidence_snapshot_sha256 = sha256(b"[]\n").hexdigest()
    packages = []
    search_items = []
    ids = set()
    for item in proposal["hypotheses"]:
        cap = _candidate_capability(item,source=source,target=args.target,
                                    target_hash=args.target_sha256,environment=args.environment)
        if cap["capability_id"] in ids:
            raise PlanError("normalized Capability identities collide")
        ids.add(cap["capability_id"])
        status = evaluate_readiness(cap,())
        projections = build_projections(cap,status,evidence_snapshot_sha256)
        packages.append({"capability":cap,"readiness_status":status.lifecycle_state,
                         "projection_status":{k:v["status"] for k,v in projections.items()},
                         "export_ready":False})
        search_items.append((cap,status))
    index = CapabilityIndex(search_items)
    query_results = [v.capability_id for v in index.search(args.query)] if args.query else []
    return {"schema_version":"app8-preview-v1","output_class":"ILLUSTRATIVE_UNVERIFIED",
            "source_sha256":source.content_sha256,"hypothesis_sha256":proposal["proposal_sha256"],
            "plan_sha256":plan["plan_sha256"],"real_execution_status":"NOT_RUN",
            "evidence_status":"NOT_AVAILABLE","release_ready":False,
            "capabilities":packages,"search_results":query_results}


def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(prog="app8",description="Preview compiler, not release-qualified")
    p.add_argument("--root",required=True);p.add_argument("--path",required=True)
    p.add_argument("--repository",required=True);p.add_argument("--revision",required=True)
    p.add_argument("--source-sha256",required=True);p.add_argument("--hypotheses",required=True)
    p.add_argument("--plan",required=True);p.add_argument("--target",required=True)
    p.add_argument("--target-sha256",required=True);p.add_argument("--environment",required=True)
    p.add_argument("--query",default="");p.add_argument("--out")
    args=p.parse_args(argv)
    try:
        result=compile_preview(args)
    except (SourceError, PlanError, ContractError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc)}),file=sys.stderr)
        return 2
    raw=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        Path(args.out).write_text(raw,encoding="utf-8")
    else:
        print(raw,end="")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
