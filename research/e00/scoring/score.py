"""E00 Issue #9 — authoritative reveal verification + frozen-prediction scoring.

Pipeline (all-or-nothing; any verification failure aborts with exit 1 and
writes no artifacts):

  1. verify every frozen input digest from #7/#8/#9 terminals against the
     exact bytes frozen at the scoring base commit (git blobs, immune to
     checkout line-ending conversion);
  2. reconstruct the canonical plaintext hidden-label manifest from the
     public blinded corpus plus the curator-held secret salt (#7 escrow),
     verify the plaintext SHA-256 and the salted commitment;
  3. score the frozen blind-run predictions per protocol blob
     84dc764846d12bc84f9f21a0ce1922c3ffa180b0 (Wilson 95% CIs, full corpus
     and independent subset separately).

Usage:
  python research/e00/scoring/score.py <path-to-reveal-escrow.json>

Outputs (the Issue #9 allowed write set):
  research/e00/reveal/reveal-escrow.json      (durable copy of curator escrow)
  research/e00/reveal/label-manifest.json     (canonical bytes, sha256 = plaintext digest)
  research/e00/reveal/reveal-verification.json
  research/e00/scoring/scoring-result.json
  research/e00/scoring/case-join.csv
"""
import csv
import datetime
import hashlib
import json
import math
import shutil
import subprocess
import sys

REPO_PROTOCOL_BLOB = "84dc764846d12bc84f9f21a0ce1922c3ffa180b0"
CORPUS_BASE_COMMIT = "f12844d8d6783910bd2b95db23197d880be7117c"
DETECTOR_MERGE_COMMIT = "6d877a9fa8fdb6c9c2a7b0df86eb114b35c1f791"

EXP = {
    "case_manifest_sha256": "a5bd20fce71c02c421a71b847358f49a3cd543464269fa74a6f53ef5e0ae5a67",
    "catalog_sha256": "7761cfe4cf5e9ea015e95b21b214b7f53ada253e429ea14e19a13f83cfc3401f",
    "cases_sha256": "fe2012c79f5171bbba00ae96bfa3b340f9d01c05b3409795f29b57e0a7aa089f",
    "hidden_label_commitment_sha256": "aac5e7811409d077e35d3115f0ca36721b093d32d84b1068f5788aeea03b246e",
    "plaintext_label_manifest_sha256": "bdcd2d61f8ade3572ea4f21382d596ec5b234a6b4d6db7a63dfa6d4e0df980a2",
    "detector_harness_config_sha256": "a0d4ba6189e505a9a07dabf064a5839a274036356bdf53a0c71a72866a6f14be",
    "predictions_output_sha256": "9cef7f828a621c63673934f7fb0f613f2d099d4ce23b12fb11f5c3e4c28fec28",
    "commitment_artifact_sha256": "29159fd713883bf6d44fe791a95574067e2c6811c48a1c4e75fdfb11dd03569b",
    "output_blob": "f260537a084612f76c6757b44bebaa2cabe04c77",
    "detector_source_blob": "5d7ed47c920a63fb3be9239d7080f88b04c9e7b5",
    "harness_blob": "8d33bab853670c5e40b2d30122ea7ba0000ec78b",
    "config_blob": "37a4826ca5a263223e206bfd9a5e2dc268d64b61",
}

DETECTOR_FILES = [
    "research/e00/detector/detector.cjs",
    "research/e00/detector/run.cjs",
    "research/e00/detector/config.json",
]
DETECTOR_BLOBS = {
    "research/e00/detector/detector.cjs": EXP["detector_source_blob"],
    "research/e00/detector/run.cjs": EXP["harness_blob"],
    "research/e00/detector/config.json": EXP["config_blob"],
}

Z95 = 1.959963984540054  # two-sided 95% normal quantile

checks = []


def check(name, ok, detail=""):
    checks.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""))
    return ok


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def canonical_blob(b):
    # run.cjs canonicalFileText rule: exclude a single trailing newline
    return b[:-1] if b.endswith(b"\n") else b


def blob(path, ref="HEAD"):
    """Exact frozen bytes committed at ref (immune to autocrlf checkout)."""
    return subprocess.run(
        ["git", "cat-file", "blob", f"{ref}:{path}"],
        capture_output=True,
        check=True,
    ).stdout


def git_rev(ref):
    return subprocess.run(
        ["git", "rev-parse", ref], capture_output=True, check=True, text=True
    ).stdout.strip()


def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def wilson(x, n):
    """Wilson score interval at 95%; returns (lower, upper)."""
    if n == 0:
        return (0.0, 0.0)
    p = x / n
    z2 = Z95 * Z95
    denom = 1 + z2 / n
    center = (p + z2 / (2 * n)) / denom
    spread = Z95 * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / denom
    return (center - spread, center + spread)


def main():
    escrow_path = sys.argv[1] if len(sys.argv) > 1 else "reveal-escrow.input.json"

    # ---------- stage 1: frozen-input verification --------------------------
    check("scoring base commit", git_rev("HEAD") == DETECTOR_MERGE_COMMIT, git_rev("HEAD"))
    check(
        "protocol blob frozen at HEAD",
        git_rev("HEAD:docs/product/v0.1/l1/E00-detector-calibration-protocol.md") == REPO_PROTOCOL_BLOB,
    )

    corpus_digests = {
        "case_manifest_sha256": sha256_bytes(canonical_blob(blob("research/e00/corpus/manifest.json"))),
        "cases_sha256": sha256_bytes(canonical_blob(blob("research/e00/corpus/cases.json"))),
        "catalog_sha256": sha256_bytes(canonical_blob(blob("research/e00/corpus/catalog.json"))),
    }
    for k, v in corpus_digests.items():
        check(f"corpus digest {k}", v == EXP[k], v)
    check(
        "commitment artifact sha256 (canonical, trailing newline excluded)",
        sha256_bytes(canonical_blob(blob("research/e00/commitments/commitment.json"))) == EXP["commitment_artifact_sha256"],
    )

    for path, want in DETECTOR_BLOBS.items():
        got = git_rev(f"HEAD:{path}")
        check(f"detector blob unchanged {path}", got == want, got)

    bundle_parts = []
    for i, p in enumerate(DETECTOR_FILES):
        bundle_parts.append(p.encode("utf-8") + b"\x00" + blob(p))
        if i < len(DETECTOR_FILES) - 1:
            bundle_parts.append(b"\x00")
    bundle_digest = sha256_bytes(b"".join(bundle_parts))
    check("detector/harness/config bundle digest", bundle_digest == EXP["detector_harness_config_sha256"], bundle_digest)

    config = json.loads(read_text("research/e00/detector/config.json"))
    run = json.loads(read_text("research/e00/runs/e00-blind-run.json"))
    check("config corpus digests == frozen corpus", config.get("corpus") == corpus_digests)
    check("config base_commit == corpus freeze", config.get("base_commit") == CORPUS_BASE_COMMIT)
    check("config protocol_blob", config.get("protocol_blob") == REPO_PROTOCOL_BLOB)
    check("run base_commit == corpus freeze", run.get("base_commit") == CORPUS_BASE_COMMIT)
    check("run protocol_blob", run.get("protocol_blob") == REPO_PROTOCOL_BLOB)
    check("run corpus == config corpus", run.get("corpus") == config.get("corpus"))
    check("run bundle digest == recomputed bundle", run.get("detector_bundle_sha256") == bundle_digest)
    check("run opaque commitments frozen", run.get("opaque_commitments") == {
        "hidden_label_commitment_sha256": EXP["hidden_label_commitment_sha256"],
        "plaintext_label_manifest_sha256": EXP["plaintext_label_manifest_sha256"],
    })
    check("run case_count 160", run.get("case_count") == 160)
    check("run unknown_count 0", run.get("unknown_count") == 0)
    check(
        "frozen output blob at HEAD",
        git_rev("HEAD:research/e00/runs/e00-blind-run.json") == EXP["output_blob"],
    )

    preds = run["predictions"]
    core = {"schema": "app8.e00.predictions.v1", "predictions": preds}
    out_digest = sha256_bytes(json.dumps(core, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    check("canonical predictions output digest", out_digest == EXP["predictions_output_sha256"], out_digest)
    check(
        "prediction row key order stable",
        all(list(r.keys()) == ["case_id", "category", "prediction", "reason"] for r in preds),
    )

    cases_doc = json.loads(blob("research/e00/corpus/cases.json").decode("utf-8"))
    catalog_doc = json.loads(blob("research/e00/corpus/catalog.json").decode("utf-8"))
    cases = cases_doc["cases"]
    catalog = {x["fixture_ref"]: x for x in catalog_doc["catalog"]}
    case_ids = [c["case_id"] for c in cases]
    check("prediction case_ids == corpus case_ids (1:1, order-preserving)", case_ids == [p["case_id"] for p in preds])
    check("case_id uniqueness", len(set(case_ids)) == 160)
    check("every case resolves fixture_ref+profile", all(
        c["fixture_ref"] in catalog and c["profile"] in catalog[c["fixture_ref"]]["profiles"] for c in cases
    ))
    check("manifest independent_subset flag", json.loads(blob("research/e00/corpus/manifest.json").decode("utf-8")).get("independent_subset") is True)
    check("manifest labels_present false", json.loads(blob("research/e00/corpus/manifest.json").decode("utf-8")).get("labels_present") is False)

    # corpus/commitments byte-identical between corpus freeze and scoring base
    for p in ("research/e00/corpus/manifest.json", "research/e00/corpus/cases.json",
              "research/e00/corpus/catalog.json", "research/e00/commitments/commitment.json"):
        a = subprocess.run(["git", "rev-parse", f"{CORPUS_BASE_COMMIT}:{p}"], capture_output=True, check=True, text=True).stdout.strip()
        b = subprocess.run(["git", "rev-parse", f"{DETECTOR_MERGE_COMMIT}:{p}"], capture_output=True, check=True, text=True).stdout.strip()
        check(f"unchanged since corpus freeze {p}", a == b, a)

    if not all(c["ok"] for c in checks):
        print("ABORT: frozen-input verification failed; no artifacts written.")
        return 1

    # ---------- stage 2: reveal ---------------------------------------------
    with open(escrow_path, "r", encoding="utf-8") as f:
        escrow = json.load(f)
    check("escrow schema", escrow.get("schema") == "app8.e00.private-reveal-escrow.v1", escrow.get("schema"))
    check("escrow curator_issue", escrow.get("curator_issue") == 7)
    check("escrow pr/tree match #7 terminal", escrow.get("pr") == 10 and escrow.get("exact_pr_head") == "55fa6a80ef6303d81f48f2b48611f133b61c560d")
    check("escrow release gate recorded", "DETECTOR_OUTPUT_FROZEN" in escrow.get("release_gate", ""))
    salt = escrow["secret_salt_hex"]
    check("secret salt is 256-bit hex", len(salt) == 64 and all(ch in "0123456789abcdef" for ch in salt.lower()))

    # per-case label derivation (escrow reconstruction rules)
    labels = []
    caseid_mismatches = []
    for c in cases:
        want_id = "c_" + hashlib.sha256(f"{c['fixture_ref']}|{c['profile']}|app8-e00-v1".encode("utf-8")).hexdigest()[:16]
        if want_id != c["case_id"]:
            caseid_mismatches.append(c["case_id"])
        safe_profile = "p" if hashlib.sha256(f"{salt}|{c['fixture_ref']}".encode("utf-8")).digest()[-1] % 2 == 0 else "q"
        truth = "SAFE" if c["profile"] == safe_profile else "MATERIAL_FALSE_SAFE"
        labels.append({"case_id": c["case_id"], "truth": truth})
    check("case_id derivation verified for all 160 cases", not caseid_mismatches, f"mismatches={len(caseid_mismatches)}")

    labels.sort(key=lambda x: x["case_id"])
    manifest_obj = {
        "case_manifest_sha256": EXP["case_manifest_sha256"],
        "labels": labels,
        "protocol_blob": REPO_PROTOCOL_BLOB,
        "schema": "app8.e00.hidden-label-manifest.v1",
    }
    canonical_manifest = json.dumps(manifest_obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    plaintext_digest = sha256_bytes(canonical_manifest)
    check("plaintext label-manifest SHA-256", plaintext_digest == EXP["plaintext_label_manifest_sha256"], plaintext_digest)

    commitment = hashlib.sha256(
        b"app8.e00.label.commitment.v1" + b"\x00" + salt.encode("ascii") + b"\x00" + canonical_manifest
    ).hexdigest()
    check("salted hidden-label commitment recompute", commitment == EXP["hidden_label_commitment_sha256"], commitment)

    commitment_doc = json.loads(blob("research/e00/commitments/commitment.json").decode("utf-8"))
    agg = {
        "SAFE": sum(1 for l in labels if l["truth"] == "SAFE"),
        "MATERIAL_FALSE_SAFE": sum(1 for l in labels if l["truth"] == "MATERIAL_FALSE_SAFE"),
    }
    check("revealed aggregate positive count == 80", agg["MATERIAL_FALSE_SAFE"] == 80, str(agg))
    check("revealed aggregate negative count == 80", agg["SAFE"] == 80, str(agg))
    by_cat = {}
    truth_by_id = {l["case_id"]: l["truth"] for l in labels}
    for c in cases:
        cat = catalog[c["fixture_ref"]]["category"]
        t = truth_by_id[c["case_id"]]
        by_cat.setdefault(cat, {"SAFE": 0, "MATERIAL_FALSE_SAFE": 0})
        by_cat[cat][t] += 1
    declared = commitment_doc["aggregate_counts"]["by_category"]
    cat_ok = all(declared[cat] == {"negative_safe": v["SAFE"], "positive_material_false_safe": v["MATERIAL_FALSE_SAFE"], "total": v["SAFE"] + v["MATERIAL_FALSE_SAFE"]} for cat, v in by_cat.items())
    check("revealed per-category counts match commitment.json", cat_ok, json.dumps(by_cat))

    if not all(c["ok"] for c in checks):
        print("ABORT: reveal verification failed; no artifacts written.")
        return 1

    # ---------- stage 3: scoring ---------------------------------------------
    def score_subset(subset_cases):
        tp = fp = tn = fn_neg = 0
        unknown = 0
        for c in subset_cases:
            truth = truth_by_id[c["case_id"]]
            pred = pred_by_id[c["case_id"]]["prediction"]
            if pred == "UNKNOWN":
                unknown += 1
            if truth == "MATERIAL_FALSE_SAFE":
                if pred == "REFUTED":
                    tp += 1
            else:
                if pred == "REFUTED":
                    fp += 1
                elif pred == "NOT_REFUTED":
                    tn += 1
        positives = sum(1 for c in subset_cases if truth_by_id[c["case_id"]] == "MATERIAL_FALSE_SAFE")
        negatives = sum(1 for c in subset_cases if truth_by_id[c["case_id"]] == "SAFE")
        sens = tp / positives
        spec = tn / negatives
        sens_lo, sens_hi = wilson(tp, positives)
        spec_lo, spec_hi = wilson(tn, negatives)
        return {
            "cases": len(subset_cases),
            "positives_material_false_safe": positives,
            "negatives_safe": negatives,
            "confusion": {
                "true_positive_REFUTED": tp,
                "false_negative_missed_positive": positives - tp,
                "false_positive_REFUTED_on_safe": fp,
                "true_negative_NOT_REFUTED": tn,
                "UNKNOWN": unknown,
            },
            "sensitivity_REFUTED_over_positives": sens,
            "specificity_NOT_REFUTED_over_negatives": spec,
            "unknown_rate": unknown / len(subset_cases),
            "sensitivity_wilson95": [sens_lo, sens_hi],
            "specificity_wilson95": [spec_lo, spec_hi],
        }

    pred_by_id = {p["case_id"]: p for p in preds}
    full = score_subset(cases)
    independent = score_subset(cases)  # all 160 cases are #7-independent (frozen manifest)

    check("feasibility cross-check: wilson(78,80) lower == #7 value",
          abs(wilson(78, 80)[0] - 0.9133556701442198) < 1e-15, repr(wilson(78, 80)[0]))

    threshold = 0.90
    conds = {
        "full_sensitivity_lb_ge_0.90": full["sensitivity_wilson95"][0] >= threshold,
        "full_specificity_lb_ge_0.90": full["specificity_wilson95"][0] >= threshold,
        "independent_sensitivity_lb_ge_0.90": independent["sensitivity_wilson95"][0] >= threshold,
        "independent_specificity_lb_ge_0.90": independent["specificity_wilson95"][0] >= threshold,
    }
    labeling_ok = all(c["ok"] for c in checks)
    execution_ok = True  # every execution-integrity check above passed; UNKNOWN=0 as frozen
    conds["no_open_P0P1_in_labeling_or_execution"] = labeling_ok and execution_ok
    gate = "PASS" if all(conds.values()) else "FAIL"

    print()
    print(f"full         sensitivity={full['sensitivity_REFUTED_over_positives']:.6f} wilson95=[{full['sensitivity_wilson95'][0]:.10f}, {full['sensitivity_wilson95'][1]:.10f}]")
    print(f"full         specificity={full['specificity_NOT_REFUTED_over_negatives']:.6f} wilson95=[{full['specificity_wilson95'][0]:.10f}, {full['specificity_wilson95'][1]:.10f}]")
    print(f"independent  sensitivity={independent['sensitivity_REFUTED_over_positives']:.6f} wilson95=[{independent['sensitivity_wilson95'][0]:.10f}, {independent['sensitivity_wilson95'][1]:.10f}]")
    print(f"independent  specificity={independent['specificity_NOT_REFUTED_over_negatives']:.6f} wilson95=[{independent['specificity_wilson95'][0]:.10f}, {independent['specificity_wilson95'][1]:.10f}]")
    print(f"confusion full: {json.dumps(full['confusion'])}")
    print(f"E00_GATE = {gate}")

    # ---------- artifacts -----------------------------------------------------
    import os
    os.makedirs("research/e00/reveal", exist_ok=True)
    shutil.copyfile(escrow_path, "research/e00/reveal/reveal-escrow.json")
    with open("research/e00/reveal/label-manifest.json", "wb") as f:
        f.write(canonical_manifest)  # exact bytes; sha256 == plaintext digest
    with open("research/e00/reveal/reveal-verification.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump({
            "schema": "app8.e00.reveal-verification.v1",
            "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "scoring_base_commit": DETECTOR_MERGE_COMMIT,
            "protocol_blob": REPO_PROTOCOL_BLOB,
            "escrow_source": "curator-held private reveal material from #7 (released after #8 DETECTOR_OUTPUT_FROZEN=YES)",
            "escrow_sha256": sha256_bytes(open("research/e00/reveal/reveal-escrow.json", "rb").read()),
            "reconstructed_label_manifest_sha256": plaintext_digest,
            "recomputed_salted_commitment_sha256": commitment,
            "expected_commitment_sha256": EXP["hidden_label_commitment_sha256"],
            "revealed_counts": {"positive_material_false_safe": agg["MATERIAL_FALSE_SAFE"], "negative_safe": agg["SAFE"], "by_category": by_cat},
            "checks": checks,
            "all_checks_passed": all(c["ok"] for c in checks),
        }, f, indent=2, ensure_ascii=False)
        f.write("\n")

    scoring_result = {
        "schema": "app8.e00.scoring-result.v1",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "protocol_blob": REPO_PROTOCOL_BLOB,
        "scoring_base_commit": DETECTOR_MERGE_COMMIT,
        "bindings": {
            "case_manifest_sha256": EXP["case_manifest_sha256"],
            "catalog_sha256": EXP["catalog_sha256"],
            "cases_sha256": EXP["cases_sha256"],
            "hidden_label_commitment_sha256": EXP["hidden_label_commitment_sha256"],
            "reconstructed_plaintext_label_manifest_sha256": EXP["plaintext_label_manifest_sha256"],
            "detector_harness_config_bundle_sha256": EXP["detector_harness_config_sha256"],
            "frozen_predictions_output_sha256": EXP["predictions_output_sha256"],
            "scoring_script_sha256": None,  # filled below
        },
        "threshold_wilson95_lower": threshold,
        "full_corpus": full,
        "independent_subset": independent,
        "independent_subset_note": "All 160 cases are #7-independent (frozen manifest independent_subset=true); the independent subset equals the full corpus.",
        "pass_conditions": conds,
        "E00_GATE": gate,
    }
    script_bytes = open(__file__, "rb").read()
    scoring_result["bindings"]["scoring_script_sha256"] = sha256_bytes(script_bytes)
    with open("research/e00/scoring/scoring-result.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(scoring_result, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open("research/e00/scoring/case-join.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "category", "fixture_ref", "profile", "truth", "prediction", "match"])
        for c in cases:
            t = truth_by_id[c["case_id"]]
            p = pred_by_id[c["case_id"]]["prediction"]
            expected = "REFUTED" if t == "MATERIAL_FALSE_SAFE" else "NOT_REFUTED"
            w.writerow([c["case_id"], catalog[c["fixture_ref"]]["category"], c["fixture_ref"], c["profile"], t, p, str(p == expected).lower()])
    print("artifacts written: research/e00/reveal/* research/e00/scoring/*")
    return 0


if __name__ == "__main__":
    sys.exit(main())
