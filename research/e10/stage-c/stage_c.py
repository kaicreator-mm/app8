#!/usr/bin/env python3
"""SE10 Stage C: freeze predictor output and deterministically score human adjudication."""
import argparse
import hashlib
import json
import pathlib
import re
import sys

ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
SOURCE_PACK_BLOB = "4b3c9b62b1899653524f19a286924f942605210a"
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
PRED_ID_RE = re.compile(r"P[0-9]{4,6}\Z")
CLASSIFICATIONS = {
    "MATCH", "PARTIAL_MATCH", "HALLUCINATED", "CALLABLE_SPAM",
    "OVER_SPLIT_DUPLICATE", "UNSUPPORTED_MERGE",
    "BINDING_EQUIVALENCE_ERROR", "FAILURE_SEMANTICS_LOSS", "AMBIGUOUS"
}
ERROR_CLASSES = {
    "HALLUCINATED": "hallucination_rate",
    "CALLABLE_SPAM": "callable_spam_rate",
    "OVER_SPLIT_DUPLICATE": "over_splitting_rate",
    "UNSUPPORTED_MERGE": "unsupported_merge_rate",
    "BINDING_EQUIVALENCE_ERROR": "binding_equivalence_error_rate",
}
PRED_ROOT = {"schema_version", "source_pack_blob", "gold_commitment_sha256",
             "predictor_gold_visibility", "model", "capabilities"}
MODEL_FIELDS = {"provider", "model", "version", "system_prompt_sha256",
                "sampling_sha256", "run_environment_sha256"}
CAP_FIELDS = {"id", "asset", "semantic_name", "purpose", "user_job", "inputs",
              "outputs", "variants", "constraints", "failure_semantics",
              "side_effects", "candidate_bindings", "provenance_refs"}
ADJ_ROOT = {"schema_version", "prediction_file_sha256", "gold_file_sha256",
            "independent_adjudication", "prediction_judgments", "gold_coverage"}
INDEP_FIELDS = {"primary_passes", "third_adjudicator_on_disagreement",
                "model_self_scoring", "review_status"}
JUDGE_FIELDS = {"prediction_id", "classification", "matched_gold_ids",
                "material_failure_semantics_applicable",
                "material_failure_semantics_preserved",
                "materially_incompatible_confident_equivalent_merge"}
COVER_FIELDS = {"gold_id", "coverage"}
COVERAGE = {"FULL", "PARTIAL", "MISS", "EXCLUDED_AMBIGUOUS"}

THRESHOLDS = {
    "pooled_precision": 0.80,
    "pooled_coverage": 0.70,
    "pooled_f1": 0.75,
    "asset_precision": 0.65,
    "asset_coverage": 0.55,
    "hallucination_rate_max": 0.10,
    "callable_spam_rate_max": 0.15,
    "over_splitting_rate_max": 0.10,
    "unsupported_merge_rate_max": 0.05,
    "binding_equivalence_error_rate_max": 0.10,
    "material_failure_semantics_preservation_min": 0.85,
    "ambiguity_exclusion_rate_max": 0.15,
}

def fail(msg):
    print("ERROR: " + msg, file=sys.stderr)
    raise SystemExit(2)

def reject_dup(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f"duplicate JSON key: {k}")
        out[k] = v
    return out

def load_raw(path):
    raw = pathlib.Path(path).read_bytes()
    try:
        obj = json.loads(raw, object_pairs_hook=reject_dup,
                         parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, UnicodeDecodeError) as exc:
        fail(f"invalid JSON in {path}: {exc}")
    return raw, obj

def exact(obj, fields, where):
    if not isinstance(obj, dict) or set(obj) != fields:
        fail(f"{where}: required/exclusive fields mismatch")

def nonblank(v, where):
    if not isinstance(v, str) or not v.strip():
        fail(f"{where}: expected nonblank string")

def sha256(raw):
    return hashlib.sha256(raw).hexdigest()

def validate_model(model):
    exact(model, MODEL_FIELDS, "model")
    for k in ("provider", "model", "version"):
        nonblank(model[k], f"model.{k}")
    for k in ("system_prompt_sha256", "sampling_sha256", "run_environment_sha256"):
        if not isinstance(model[k], str) or not SHA256_RE.fullmatch(model[k]):
            fail(f"model.{k}: expected lowercase SHA-256")

def validate_prediction(doc, expected_gold_commitment_sha):
    exact(doc, PRED_ROOT, "prediction")
    if doc["schema_version"] != "se10-prediction-v1":
        fail("prediction schema_version mismatch")
    if doc["source_pack_blob"] != SOURCE_PACK_BLOB:
        fail("prediction source_pack_blob mismatch")
    if doc["gold_commitment_sha256"] != expected_gold_commitment_sha:
        fail("prediction does not bind exact Gold public commitment")
    if doc["predictor_gold_visibility"] is not False:
        fail("predictor_gold_visibility must be false")
    validate_model(doc["model"])
    caps = doc["capabilities"]
    if not isinstance(caps, list) or not caps:
        fail("prediction capabilities must be nonempty list")
    ids, counts = set(), {a: 0 for a in ASSETS}
    list_fields = ("inputs", "outputs", "variants", "constraints",
                   "failure_semantics", "side_effects",
                   "candidate_bindings", "provenance_refs")
    for i, cap in enumerate(caps):
        exact(cap, CAP_FIELDS, f"capabilities[{i}]")
        pid = cap["id"]
        if not isinstance(pid, str) or not PRED_ID_RE.fullmatch(pid):
            fail(f"capabilities[{i}].id invalid")
        if pid in ids:
            fail(f"duplicate prediction id: {pid}")
        ids.add(pid)
        if cap["asset"] not in counts:
            fail(f"{pid}: unsupported asset")
        for k in ("semantic_name", "purpose", "user_job"):
            nonblank(cap[k], f"{pid}.{k}")
        for k in list_fields:
            if not isinstance(cap[k], list):
                fail(f"{pid}.{k}: expected list")
            for item in cap[k]:
                nonblank(item, f"{pid}.{k}[]")
        counts[cap["asset"]] += 1
    return counts

def freeze_prediction(pred_path, gold_commitment_path, out_path):
    gold_raw, gold = load_raw(gold_commitment_path)
    if not isinstance(gold, dict) or gold.get("schema_version") != "se10-public-commitment-v1":
        fail("Gold public commitment schema mismatch")
    if gold.get("source_pack_blob") != SOURCE_PACK_BLOB:
        fail("Gold commitment source_pack_blob mismatch")
    gold_file_sha = gold.get("gold_file_sha256")
    if not isinstance(gold_file_sha, str) or not SHA256_RE.fullmatch(gold_file_sha):
        fail("Gold commitment missing valid gold_file_sha256")
    pred_raw, pred = load_raw(pred_path)
    gold_commit_sha = sha256(gold_raw)
    counts = validate_prediction(pred, gold_commit_sha)
    public = {
        "schema_version": "se10-prediction-commitment-v1",
        "source_pack_blob": SOURCE_PACK_BLOB,
        "gold_commitment_sha256": gold_commit_sha,
        "gold_file_sha256": gold_file_sha,
        "prediction_file_sha256": sha256(pred_raw),
        "prediction_count": sum(counts.values()),
        "asset_counts": counts,
        "model": pred["model"],
        "declared_predictor_gold_visibility": False,
        "semantic_prediction_in_public_commitment": False,
    }
    pathlib.Path(out_path).write_text(json.dumps(public, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return public

def validate_gold(gold):
    if not isinstance(gold, dict) or gold.get("schema_version") != "se10-gold-v1":
        fail("private Gold schema mismatch")
    if gold.get("source_pack_blob") != SOURCE_PACK_BLOB:
        fail("private Gold source_pack_blob mismatch")
    caps = gold.get("capabilities")
    if not isinstance(caps, list):
        fail("private Gold capabilities missing")
    refs = {}
    for cap in caps:
        if not isinstance(cap, dict):
            fail("invalid private Gold capability")
        gid, asset = cap.get("id"), cap.get("asset")
        if not isinstance(gid, str) or gid in refs or asset not in ASSETS:
            fail("invalid/duplicate Gold id or asset")
        ambiguity = cap.get("ambiguity")
        if not isinstance(ambiguity, bool):
            fail(f"{gid}: Gold ambiguity must be bool")
        refs[gid] = {"asset": asset, "ambiguity": ambiguity}
    if len(refs) < 48:
        fail("private Gold must contain at least 48 capabilities")
    return refs

def safe_div(n, d):
    return None if d == 0 else n / d

def f1(p, r):
    if p is None or r is None:
        return None
    return 0.0 if p + r == 0 else 2 * p * r / (p + r)

def score(adjudication_path, prediction_path, gold_path, gold_commitment_path, commitment_path, out_path):
    pred_raw, pred = load_raw(prediction_path)
    gold_raw, gold = load_raw(gold_path)
    gold_public_raw, gold_public = load_raw(gold_commitment_path)
    commit_raw, commit = load_raw(commitment_path)
    if commit.get("schema_version") != "se10-prediction-commitment-v1":
        fail("prediction commitment schema mismatch")
    if gold_public.get("schema_version") != "se10-public-commitment-v1":
        fail("Gold public commitment schema mismatch")
    if commit.get("gold_commitment_sha256") != sha256(gold_public_raw):
        fail("prediction commitment does not bind supplied Gold public commitment")
    if gold_public.get("gold_file_sha256") != sha256(gold_raw):
        fail("private Gold does not match supplied Gold public commitment")
    if commit.get("prediction_file_sha256") != sha256(pred_raw):
        fail("prediction file hash does not match commitment")
    if commit.get("gold_file_sha256") != sha256(gold_raw):
        fail("private Gold hash does not match committed Gold hash")
    gold_refs = validate_gold(gold)
    validate_prediction(pred, commit.get("gold_commitment_sha256"))

    adj_raw, adj = load_raw(adjudication_path)
    exact(adj, ADJ_ROOT, "adjudication")
    if adj["schema_version"] != "se10-adjudication-v1":
        fail("adjudication schema_version mismatch")
    if adj["prediction_file_sha256"] != sha256(pred_raw):
        fail("adjudication prediction hash mismatch")
    if adj["gold_file_sha256"] != sha256(gold_raw):
        fail("adjudication Gold hash mismatch")
    indep = adj["independent_adjudication"]
    exact(indep, INDEP_FIELDS, "independent_adjudication")
    if indep["primary_passes"] != 2 or indep["third_adjudicator_on_disagreement"] is not True:
        fail("adjudication independence structure mismatch")
    if indep["model_self_scoring"] is not False or indep["review_status"] != "PASS":
        fail("adjudication must be independently PASS-reviewed with no model self-scoring")

    pred_by_id = {c["id"]: c for c in pred["capabilities"]}
    judgments = {}
    for j in adj["prediction_judgments"]:
        exact(j, JUDGE_FIELDS, "prediction_judgment")
        pid = j["prediction_id"]
        if pid not in pred_by_id or pid in judgments:
            fail(f"unknown/duplicate prediction judgment: {pid}")
        if j["classification"] not in CLASSIFICATIONS:
            fail(f"{pid}: invalid classification")
        matches = j["matched_gold_ids"]
        if not isinstance(matches, list) or len(matches) != len(set(
            gid for gid in matches if isinstance(gid, str)
        )):
            fail(f"{pid}: matched_gold_ids must be an unduplicated list")
        positive = j["classification"] in {"MATCH", "PARTIAL_MATCH"}
        if (positive or j["classification"] == "AMBIGUOUS") and not matches:
            fail(f"{pid}: positive/ambiguous verdict requires frozen Gold linkage")
        for gid in matches:
            if not isinstance(gid, str) or gid not in gold_refs:
                fail(f"{pid}: unknown/non-string matched Gold id {gid}")
            ref = gold_refs[gid]
            if ref["asset"] != pred_by_id[pid]["asset"]:
                fail(f"{pid}: cross-asset Gold match {gid}")
            if positive and ref["ambiguity"]:
                fail(f"{pid}: MATCH/PARTIAL_MATCH cannot use ambiguous Gold {gid}")
            if j["classification"] == "AMBIGUOUS" and not ref["ambiguity"]:
                fail(f"{pid}: AMBIGUOUS cannot exclude non-ambiguous Gold {gid}")
        for k in ("material_failure_semantics_applicable",
                  "material_failure_semantics_preserved",
                  "materially_incompatible_confident_equivalent_merge"):
            if not isinstance(j[k], bool):
                fail(f"{pid}.{k}: must be bool")
        if not j["material_failure_semantics_applicable"] and j["material_failure_semantics_preserved"]:
            fail(f"{pid}: cannot preserve non-applicable failure semantics")
        judgments[pid] = j
    if set(judgments) != set(pred_by_id):
        fail("prediction judgments must cover every frozen prediction exactly once")

    coverage = {}
    for row in adj["gold_coverage"]:
        exact(row, COVER_FIELDS, "gold_coverage")
        gid = row["gold_id"]
        if gid not in gold_refs or gid in coverage:
            fail(f"unknown/duplicate Gold coverage id: {gid}")
        if row["coverage"] not in COVERAGE:
            fail(f"{gid}: invalid coverage")
        if gold_refs[gid]["ambiguity"] and row["coverage"] != "EXCLUDED_AMBIGUOUS":
            fail(f"{gid}: ambiguous Gold must be excluded")
        if not gold_refs[gid]["ambiguity"] and row["coverage"] == "EXCLUDED_AMBIGUOUS":
            fail(f"{gid}: non-ambiguous Gold cannot be excluded")
        coverage[gid] = row["coverage"]
    if set(coverage) != set(gold_refs):
        fail("gold_coverage must cover every Gold capability exactly once")

    # Coverage is independently adjudicated, but its declared semantic
    # credit must be supported by the frozen prediction-to-Gold link ledger.
    linked_classes = {gid: set() for gid in gold_refs}
    for judgment in judgments.values():
        for gid in judgment["matched_gold_ids"]:
            linked_classes[gid].add(judgment["classification"])
            if judgment["classification"] == "MATCH" and coverage[gid] != "FULL":
                fail(f"{gid}: MATCH linked to Gold without FULL coverage")
            if judgment["classification"] == "PARTIAL_MATCH" and coverage[gid] == "MISS":
                fail(f"{gid}: PARTIAL_MATCH linked to Gold marked MISS")
    for gid, value in coverage.items():
        classes = linked_classes[gid]
        if value == "FULL" and "MATCH" not in classes:
            fail(f"{gid}: FULL coverage has no frozen MATCH link")
        if value == "PARTIAL" and not classes.intersection({"MATCH", "PARTIAL_MATCH"}):
            fail(f"{gid}: PARTIAL coverage has no frozen positive link")

    per_asset = {}
    total_prec_num = total_prec_den = 0.0
    total_cov_num = total_cov_den = 0.0
    error_counts = {metric: 0 for metric in ERROR_CLASSES.values()}
    global_pred_den = 0
    failure_app = failure_ok = 0
    incompatible_merge_count = 0

    for asset in ASSETS:
        pnum = pden = 0.0
        cnum = cden = 0.0
        for pid, cap in pred_by_id.items():
            if cap["asset"] != asset:
                continue
            j = judgments[pid]
            cls = j["classification"]
            if cls != "AMBIGUOUS":
                pden += 1
                global_pred_den += 1
                pnum += 1.0 if cls == "MATCH" else 0.5 if cls == "PARTIAL_MATCH" else 0.0
                if cls in ERROR_CLASSES:
                    error_counts[ERROR_CLASSES[cls]] += 1
                if j["material_failure_semantics_applicable"]:
                    failure_app += 1
                    failure_ok += int(j["material_failure_semantics_preserved"])
                incompatible_merge_count += int(j["materially_incompatible_confident_equivalent_merge"])
        for gid, meta in gold_refs.items():
            if meta["asset"] != asset or coverage[gid] == "EXCLUDED_AMBIGUOUS":
                continue
            cden += 1
            cnum += 1.0 if coverage[gid] == "FULL" else 0.5 if coverage[gid] == "PARTIAL" else 0.0
        p, r = safe_div(pnum, pden), safe_div(cnum, cden)
        per_asset[asset] = {"precision": p, "coverage": r, "f1": f1(p, r),
                            "prediction_denominator": int(pden),
                            "reference_denominator": int(cden)}
        total_prec_num += pnum; total_prec_den += pden
        total_cov_num += cnum; total_cov_den += cden

    pooled_p = safe_div(total_prec_num, total_prec_den)
    pooled_r = safe_div(total_cov_num, total_cov_den)
    pooled_f1 = f1(pooled_p, pooled_r)
    ambiguity_count = sum(1 for g in gold_refs.values() if g["ambiguity"])
    ambiguity_rate = ambiguity_count / len(gold_refs)
    error_rates = {k: safe_div(v, global_pred_den) for k, v in error_counts.items()}
    failure_rate = safe_div(failure_ok, failure_app)

    blocked_reasons = []
    if ambiguity_rate > THRESHOLDS["ambiguity_exclusion_rate_max"]:
        blocked_reasons.append("Gold ambiguity exclusions exceed 15%")
    if global_pred_den == 0 or total_cov_den == 0 or failure_app == 0:
        blocked_reasons.append("required primary metric denominator is zero")

    failures = []
    if not blocked_reasons:
        if pooled_p < THRESHOLDS["pooled_precision"]: failures.append("pooled precision")
        if pooled_r < THRESHOLDS["pooled_coverage"]: failures.append("pooled coverage")
        if pooled_f1 < THRESHOLDS["pooled_f1"]: failures.append("pooled F1")
        for asset, m in per_asset.items():
            if m["precision"] is None or m["precision"] < THRESHOLDS["asset_precision"]:
                failures.append(f"{asset} precision")
            if m["coverage"] is None or m["coverage"] < THRESHOLDS["asset_coverage"]:
                failures.append(f"{asset} coverage")
        max_map = {
            "hallucination_rate": "hallucination_rate_max",
            "callable_spam_rate": "callable_spam_rate_max",
            "over_splitting_rate": "over_splitting_rate_max",
            "unsupported_merge_rate": "unsupported_merge_rate_max",
            "binding_equivalence_error_rate": "binding_equivalence_error_rate_max",
        }
        for metric, tkey in max_map.items():
            if error_rates[metric] > THRESHOLDS[tkey]:
                failures.append(metric)
        if failure_rate < THRESHOLDS["material_failure_semantics_preservation_min"]:
            failures.append("material failure-semantics preservation")
        if incompatible_merge_count:
            failures.append("materially incompatible confident equivalent merge")

    verdict = "BLOCKED" if blocked_reasons else "FAIL" if failures else "PASS"
    result = {
        "schema_version": "se10-terminal-v1",
        "protocol_blob": "08f9244a04275c780f778d50f638e332aa5807a2",
        "prediction_file_sha256": sha256(pred_raw),
        "gold_file_sha256": sha256(gold_raw),
        "adjudication_file_sha256": sha256(adj_raw),
        "per_asset": per_asset,
        "pooled": {"precision": pooled_p, "coverage": pooled_r, "f1": pooled_f1},
        "error_rates": error_rates,
        "material_failure_semantics_preservation": failure_rate,
        "ambiguity_exclusion_rate": ambiguity_rate,
        "materially_incompatible_confident_equivalent_merge_count": incompatible_merge_count,
        "thresholds": THRESHOLDS,
        "blocked_reasons": blocked_reasons,
        "failed_thresholds": failures,
        "verdict": verdict,
        "semantic_gold_embedded": False,
    }
    pathlib.Path(out_path).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze-prediction")
    f.add_argument("prediction")
    f.add_argument("--gold-commitment", required=True)
    f.add_argument("--out", required=True)
    s = sub.add_parser("score")
    s.add_argument("adjudication")
    s.add_argument("--prediction", required=True)
    s.add_argument("--gold", required=True)
    s.add_argument("--gold-commitment", required=True)
    s.add_argument("--prediction-commitment", required=True)
    s.add_argument("--out", required=True)
    a = p.parse_args()
    if a.cmd == "freeze-prediction":
        freeze_prediction(a.prediction, a.gold_commitment, a.out)
    else:
        result = score(a.adjudication, a.prediction, a.gold, a.gold_commitment, a.prediction_commitment, a.out)
        print("VERDICT=" + result["verdict"])

if __name__ == "__main__":
    main()
