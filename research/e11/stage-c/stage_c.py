#!/usr/bin/env python3
"""SE11 Stage C: strip hidden truth for LLM-B, freeze plans, score real execution."""
import argparse
import hashlib
import json
import pathlib
import re
import sys

ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
TRUTH_CLASSES = ("TRUE", "MATERIALLY_FALSE", "OVERBROAD", "NEAR_MISS")
EXPECTED = {"TRUE": 8, "MATERIALLY_FALSE": 4, "OVERBROAD": 4, "NEAR_MISS": 4}
OUTCOMES = {"SUPPORTED", "REFUTED", "NARROWED", "BLOCKED", "INCONCLUSIVE"}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
MODEL_FIELDS = {"provider", "model", "version", "system_prompt_sha256",
                "sampling_sha256", "run_environment_sha256"}
PLAN_ROOT = {"schema_version", "planner_input_sha256", "truth_visible_to_llm_b",
             "decisive_fixtures_visible_to_llm_b", "model", "plans"}
PLAN_FIELDS = {"claim_id", "positive_probes", "falsification_probes",
               "expected_observations", "stop_conditions", "replay_requirements"}
EXEC_ROOT = {"schema_version", "plan_file_sha256", "independent_scoring", "results"}
SCORE_FIELDS = {"ground_truth_reveal_after_execution", "model_self_scoring",
                "review_status"}
RESULT_FIELDS = {"claim_id", "outcome", "real_observation_present",
                 "promotion_without_real_observation",
                 "material_constraint_applicable", "material_constraint_discovered",
                 "decisive_evidence_reproducible", "evidence_sha256"}
THRESHOLDS = {
    "false_promotion_rate_max": 0.05,
    "supported_false_rejection_rate_max": 0.15,
    "refutation_sensitivity_min": 0.90,
    "narrowing_sensitivity_min": 0.80,
    "boundary_detection_sensitivity_min": 0.75,
    "material_constraint_discovery_min": 0.80,
    "reproducible_decisive_evidence_min": 0.90,
    "environmental_blocked_rate_max": 0.15,
}

def fail(msg):
    print("ERROR: " + msg, file=sys.stderr)
    raise SystemExit(2)

def reject_dup(pairs):
    out={}
    for k,v in pairs:
        if k in out:
            raise ValueError(f"duplicate JSON key: {k}")
        out[k]=v
    return out

def load_raw(path):
    raw=pathlib.Path(path).read_bytes()
    try:
        obj=json.loads(raw, object_pairs_hook=reject_dup,
                       parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, UnicodeDecodeError) as exc:
        fail(f"invalid JSON in {path}: {exc}")
    return raw,obj

def exact(obj, fields, where):
    if not isinstance(obj,dict) or set(obj)!=fields:
        fail(f"{where}: required/exclusive fields mismatch")

def nonblank(v, where):
    if not isinstance(v,str) or not v.strip():
        fail(f"{where}: expected nonblank string")

def sha256(raw):
    return hashlib.sha256(raw).hexdigest()

def validate_model(model):
    exact(model, MODEL_FIELDS, "model")
    for k in ("provider","model","version"):
        nonblank(model[k],f"model.{k}")
    for k in ("system_prompt_sha256","sampling_sha256","run_environment_sha256"):
        if not isinstance(model[k],str) or not SHA256_RE.fullmatch(model[k]):
            fail(f"model.{k}: expected lowercase SHA-256")

def validate_hidden(hidden):
    if not isinstance(hidden,dict) or hidden.get("schema_version")!="se11-hidden-v1":
        fail("hidden corpus schema mismatch")
    claims=hidden.get("claims")
    if not isinstance(claims,list) or len(claims)!=80:
        fail("hidden corpus must contain exactly 80 claims")
    ids=set()
    matrix={a:{c:0 for c in TRUTH_CLASSES} for a in ASSETS}
    rows={}
    for i,c in enumerate(claims):
        if not isinstance(c,dict):
            fail(f"claims[{i}]: expected object")
        cid,asset,truth=c.get("id"),c.get("asset"),c.get("truth_class")
        nonblank(cid,f"claims[{i}].id")
        if cid in ids:
            fail(f"duplicate claim id: {cid}")
        ids.add(cid)
        if asset not in matrix or truth not in EXPECTED:
            fail(f"{cid}: invalid asset/truth class")
        for k in ("claim_text","binding_id"):
            nonblank(c.get(k),f"{cid}.{k}")
        matrix[asset][truth]+=1
        rows[cid]=c
    for asset in ASSETS:
        for klass,wanted in EXPECTED.items():
            if matrix[asset][klass]!=wanted:
                fail(f"{asset}/{klass}: expected {wanted}, got {matrix[asset][klass]}")
    target=hidden.get("execution_target_manifest_sha256")
    if not isinstance(target,str) or not SHA256_RE.fullmatch(target):
        fail("hidden corpus missing valid execution_target_manifest_sha256")
    return rows,target

def prepare_planner_input(hidden_path, public_commitment_path, plan_budget_sha, out_path):
    if not isinstance(plan_budget_sha,str) or not SHA256_RE.fullmatch(plan_budget_sha):
        fail("plan budget must be lowercase SHA-256")
    hidden_raw,hidden=load_raw(hidden_path)
    pub_raw,pub=load_raw(public_commitment_path)
    if not isinstance(pub,dict) or pub.get("schema_version")!="se11-public-commitment-v1":
        fail("hidden public commitment schema mismatch")
    if pub.get("hidden_file_sha256")!=sha256(hidden_raw):
        fail("hidden corpus does not match public commitment")
    rows,target=validate_hidden(hidden)
    opaque=pub.get("opaque_claim_ids")
    if not isinstance(opaque,list) or set(opaque)!=set(rows):
        fail("public commitment opaque claim IDs do not match hidden corpus")
    planner={
        "schema_version":"se11-planner-input-v1",
        "hidden_commitment_sha256":sha256(pub_raw),
        "hidden_file_sha256":sha256(hidden_raw),
        "execution_target_manifest_sha256":target,
        "plan_budget_sha256":plan_budget_sha,
        "truth_visible_to_llm_b":False,
        "decisive_fixtures_visible_to_llm_b":False,
        "claims":[
            {"id":cid,"asset":rows[cid]["asset"],"claim_text":rows[cid]["claim_text"],
             "binding_id":rows[cid]["binding_id"]}
            for cid in sorted(rows)
        ],
    }
    pathlib.Path(out_path).write_text(json.dumps(planner,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return planner

def validate_planner_against_hidden(planner, hidden_rows, target_hash):
    if not isinstance(planner, dict) or planner.get("schema_version") != "se11-planner-input-v1":
        fail("planner input schema mismatch")
    if planner.get("hidden_file_sha256") is None:
        fail("planner input missing hidden_file_sha256")
    if planner.get("execution_target_manifest_sha256") != target_hash:
        fail("planner input execution target hash mismatch")
    if planner.get("truth_visible_to_llm_b") is not False or planner.get("decisive_fixtures_visible_to_llm_b") is not False:
        fail("planner input exposes hidden truth/fixtures")
    claims = planner.get("claims")
    if not isinstance(claims, list):
        fail("planner input claims must be list")
    seen = set()
    for i, c in enumerate(claims):
        if not isinstance(c, dict) or set(c) != {"id", "asset", "claim_text", "binding_id"}:
            fail(f"planner claims[{i}]: required/exclusive fields mismatch")
        cid = c["id"]
        if cid not in hidden_rows or cid in seen:
            fail(f"planner input unknown/duplicate claim id: {cid}")
        seen.add(cid)
        src = hidden_rows[cid]
        if c["asset"] != src["asset"] or c["claim_text"] != src["claim_text"] or c["binding_id"] != src["binding_id"]:
            fail(f"{cid}: planner input differs from hidden corpus safe fields")
    if seen != set(hidden_rows):
        fail("planner input must cover every hidden claim exactly once")

def validate_plan(plan, planner_input):
    exact(plan, PLAN_ROOT, "plan")
    if plan["schema_version"]!="se11-plan-v1":
        fail("plan schema_version mismatch")
    if plan["planner_input_sha256"]!=sha256(
        json.dumps(planner_input,indent=2,sort_keys=True).encode("utf-8")+b"\n"
    ):
        fail("plan does not bind exact canonical planner input")
    if plan["truth_visible_to_llm_b"] is not False or plan["decisive_fixtures_visible_to_llm_b"] is not False:
        fail("LLM-B plan declares hidden truth/fixture visibility")
    validate_model(plan["model"])
    expected_ids={c["id"] for c in planner_input["claims"]}
    seen=set()
    for i,p in enumerate(plan["plans"]):
        exact(p,PLAN_FIELDS,f"plans[{i}]")
        cid=p["claim_id"]
        if cid not in expected_ids or cid in seen:
            fail(f"unknown/duplicate plan claim id: {cid}")
        seen.add(cid)
        for k in ("positive_probes","falsification_probes","expected_observations",
                  "stop_conditions","replay_requirements"):
            vals=p[k]
            if not isinstance(vals,list) or not vals:
                fail(f"{cid}.{k}: expected nonempty list")
            for v in vals:
                nonblank(v,f"{cid}.{k}[]")
    if seen!=expected_ids:
        fail("plans must cover every planner-input claim exactly once")

def freeze_plan(plan_path, planner_input_path, out_path):
    input_raw,planner=load_raw(planner_input_path)
    if planner.get("schema_version")!="se11-planner-input-v1":
        fail("planner input schema mismatch")
    plan_raw,plan=load_raw(plan_path)
    canonical=(json.dumps(planner,indent=2,sort_keys=True)+"\n").encode("utf-8")
    if input_raw!=canonical:
        fail("planner input bytes are not canonical prepare_planner_input output")
    validate_plan(plan,planner)
    public={
        "schema_version":"se11-plan-commitment-v1",
        "hidden_commitment_sha256":planner["hidden_commitment_sha256"],
        "hidden_file_sha256":planner["hidden_file_sha256"],
        "execution_target_manifest_sha256":planner["execution_target_manifest_sha256"],
        "plan_budget_sha256":planner["plan_budget_sha256"],
        "planner_input_sha256":sha256(input_raw),
        "plan_file_sha256":sha256(plan_raw),
        "plan_count":len(plan["plans"]),
        "model":plan["model"],
        "declared_truth_visible_to_llm_b":False,
        "declared_decisive_fixtures_visible_to_llm_b":False,
        "semantic_truth_in_public_commitment":False,
    }
    pathlib.Path(out_path).write_text(json.dumps(public,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return public

def safe_div(n,d):
    return None if d==0 else n/d

def score(execution_path, hidden_path, plan_path, planner_input_path, plan_commitment_path, out_path):
    exec_raw,execution=load_raw(execution_path)
    hidden_raw,hidden=load_raw(hidden_path)
    plan_raw,plan=load_raw(plan_path)
    input_raw,planner=load_raw(planner_input_path)
    commit_raw,commit=load_raw(plan_commitment_path)
    if commit.get("schema_version")!="se11-plan-commitment-v1":
        fail("plan commitment schema mismatch")
    if commit.get("hidden_file_sha256")!=sha256(hidden_raw):
        fail("hidden corpus hash does not match plan commitment")
    if commit.get("planner_input_sha256")!=sha256(input_raw):
        fail("planner input hash does not match plan commitment")
    if commit.get("plan_file_sha256")!=sha256(plan_raw):
        fail("plan file hash does not match plan commitment")
    rows,target=validate_hidden(hidden)
    if planner.get("hidden_file_sha256")!=sha256(hidden_raw):
        fail("planner input hidden hash mismatch")
    validate_planner_against_hidden(planner, rows, target)
    canonical=(json.dumps(planner,indent=2,sort_keys=True)+"\n").encode("utf-8")
    if input_raw != canonical:
        fail("planner input bytes are not canonical prepare_planner_input output")
    if plan.get("planner_input_sha256") != commit.get("planner_input_sha256"):
        fail("plan and plan commitment bind different planner inputs")
    validate_plan(plan,planner)

    exact(execution,EXEC_ROOT,"execution")
    if execution["schema_version"]!="se11-execution-ledger-v1":
        fail("execution ledger schema mismatch")
    if execution["plan_file_sha256"]!=sha256(plan_raw):
        fail("execution ledger plan hash mismatch")
    indep=execution["independent_scoring"]
    exact(indep,SCORE_FIELDS,"independent_scoring")
    if indep["ground_truth_reveal_after_execution"] is not True:
        fail("ground truth must be revealed only after execution")
    if indep["model_self_scoring"] is not False or indep["review_status"]!="PASS":
        fail("execution scoring must be independently PASS-reviewed without model self-scoring")

    results={}
    for i,r in enumerate(execution["results"]):
        exact(r,RESULT_FIELDS,f"results[{i}]")
        cid=r["claim_id"]
        if cid not in rows or cid in results:
            fail(f"unknown/duplicate execution result: {cid}")
        if r["outcome"] not in OUTCOMES:
            fail(f"{cid}: invalid outcome")
        for k in ("real_observation_present","promotion_without_real_observation",
                  "material_constraint_applicable","material_constraint_discovered",
                  "decisive_evidence_reproducible"):
            if not isinstance(r[k],bool):
                fail(f"{cid}.{k}: must be bool")
        if not r["material_constraint_applicable"] and r["material_constraint_discovered"]:
            fail(f"{cid}: cannot discover non-applicable material constraint")
        if not isinstance(r["evidence_sha256"],str) or not SHA256_RE.fullmatch(r["evidence_sha256"]):
            fail(f"{cid}: evidence_sha256 invalid")
        results[cid]=r
    if set(results)!=set(rows):
        fail("execution results must cover all 80 claims exactly once")

    blocked=sum(1 for r in results.values() if r["outcome"]=="BLOCKED")
    blocked_rate=blocked/80
    nonblocked=[cid for cid,r in results.items() if r["outcome"]!="BLOCKED"]

    def ids_for(cls):
        return [cid for cid in nonblocked if rows[cid]["truth_class"]==cls]
    true_ids=ids_for("TRUE")
    false_ids=ids_for("MATERIALLY_FALSE")
    over_ids=ids_for("OVERBROAD")
    near_ids=ids_for("NEAR_MISS")
    unsupported_ids=false_ids+over_ids

    false_promotion=safe_div(sum(results[c]["outcome"]=="SUPPORTED" for c in unsupported_ids),len(unsupported_ids))
    false_rejection=safe_div(sum(results[c]["outcome"]!="SUPPORTED" for c in true_ids),len(true_ids))
    refutation=safe_div(sum(results[c]["outcome"]=="REFUTED" for c in false_ids),len(false_ids))
    narrowing=safe_div(sum(results[c]["outcome"]=="NARROWED" for c in over_ids),len(over_ids))
    boundary=safe_div(sum(results[c]["outcome"] in {"REFUTED","NARROWED"} for c in near_ids),len(near_ids))
    applicable=[c for c in nonblocked if results[c]["material_constraint_applicable"]]
    constraint=safe_div(sum(results[c]["material_constraint_discovered"] for c in applicable),len(applicable))
    reproducible=safe_div(sum(results[c]["decisive_evidence_reproducible"] for c in nonblocked),len(nonblocked))

    no_observation_decisive=[
        c for c in nonblocked
        if results[c]["outcome"] in {"SUPPORTED","REFUTED","NARROWED"}
        and not results[c]["real_observation_present"]
    ]
    unsupported_model_only=[
        c for c in false_ids+over_ids+near_ids
        if results[c]["outcome"]=="SUPPORTED"
        and results[c]["promotion_without_real_observation"]
    ]

    metrics={
        "false_promotion_rate":false_promotion,
        "supported_false_rejection_rate":false_rejection,
        "refutation_sensitivity":refutation,
        "narrowing_sensitivity":narrowing,
        "boundary_detection_sensitivity":boundary,
        "material_constraint_discovery":constraint,
        "reproducible_decisive_evidence":reproducible,
        "environmental_blocked_rate":blocked_rate,
    }

    blocked_reasons=[]
    if blocked_rate>THRESHOLDS["environmental_blocked_rate_max"]:
        blocked_reasons.append("environmental BLOCKED rate exceeds 15%")
    for name in ("false_promotion_rate","supported_false_rejection_rate",
                 "refutation_sensitivity","narrowing_sensitivity",
                 "boundary_detection_sensitivity","material_constraint_discovery",
                 "reproducible_decisive_evidence"):
        if metrics[name] is None:
            blocked_reasons.append(f"{name} denominator is zero after BLOCKED exclusions")

    failures=[]
    if not blocked_reasons:
        if false_promotion>THRESHOLDS["false_promotion_rate_max"]: failures.append("false promotion rate")
        if false_rejection>THRESHOLDS["supported_false_rejection_rate_max"]: failures.append("supported false-rejection rate")
        if refutation<THRESHOLDS["refutation_sensitivity_min"]: failures.append("refutation sensitivity")
        if narrowing<THRESHOLDS["narrowing_sensitivity_min"]: failures.append("narrowing sensitivity")
        if boundary<THRESHOLDS["boundary_detection_sensitivity_min"]: failures.append("boundary-detection sensitivity")
        if constraint<THRESHOLDS["material_constraint_discovery_min"]: failures.append("material-constraint discovery")
        if reproducible<THRESHOLDS["reproducible_decisive_evidence_min"]: failures.append("reproducible decisive evidence")
        if no_observation_decisive: failures.append("decisive outcome without real observation")
        if unsupported_model_only: failures.append("unsupported promotion from model/document prose without real observation")

    verdict="BLOCKED" if blocked_reasons else "FAIL" if failures else "PASS"
    result={
        "schema_version":"se11-terminal-v1",
        "protocol_blob":"1204c717eb590071a7b7f7e1cd3018b825ef1617",
        "hidden_file_sha256":sha256(hidden_raw),
        "plan_file_sha256":sha256(plan_raw),
        "execution_ledger_sha256":sha256(exec_raw),
        "metrics":metrics,
        "thresholds":THRESHOLDS,
        "blocked_reasons":blocked_reasons,
        "failed_thresholds":failures,
        "decisive_without_real_observation_count":len(no_observation_decisive),
        "unsupported_model_only_promotion_count":len(unsupported_model_only),
        "verdict":verdict,
        "hidden_truth_embedded":False,
    }
    pathlib.Path(out_path).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result

def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd",required=True)
    a=sub.add_parser("prepare-planner-input")
    a.add_argument("hidden")
    a.add_argument("--hidden-public-commitment",required=True)
    a.add_argument("--plan-budget-sha256",required=True)
    a.add_argument("--out",required=True)
    b=sub.add_parser("freeze-plan")
    b.add_argument("plan")
    b.add_argument("--planner-input",required=True)
    b.add_argument("--out",required=True)
    s=sub.add_parser("score")
    s.add_argument("execution")
    s.add_argument("--hidden",required=True)
    s.add_argument("--plan",required=True)
    s.add_argument("--planner-input",required=True)
    s.add_argument("--plan-commitment",required=True)
    s.add_argument("--out",required=True)
    args=p.parse_args()
    if args.cmd=="prepare-planner-input":
        prepare_planner_input(args.hidden,args.hidden_public_commitment,args.plan_budget_sha256,args.out)
    elif args.cmd=="freeze-plan":
        freeze_plan(args.plan,args.planner_input,args.out)
    else:
        r=score(args.execution,args.hidden,args.plan,args.planner_input,args.plan_commitment,args.out)
        print("VERDICT="+r["verdict"])

if __name__=="__main__":
    main()
