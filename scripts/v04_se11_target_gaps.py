#!/usr/bin/env python3
"""Public read-only SE11 target candidacy gap report, NOT a final manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = Path("research/e11/execution-targets/execution-target-selection.json")
CANDIDATE_GIT_BLOB = "ee247c95eb56081e4014210f1013fb66f783345a"
ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
EXPECTED_SOURCES = {
    "FFmpeg":"f2bf7a2440d1e49023e4b3ed0e224a8806d388b8",
    "pandas":"82c18c170b9aea7cbb96ef54b8005bed07c94220",
    "MinIO":"7aac2a2c5b7c882e68c1ce017d8256be2feea27f",
    "LibreOffice":"016fd5d049256dc849111f60870f15201fcd1526",
}
EXPECTED_RELATIONS = {"FFmpeg":"SAME","pandas":"SAME","MinIO":"SAME","LibreOffice":"DIVERGED"}


class UnfrozenTarget(ValueError):
    pass


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def reject_dups(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise UnfrozenTarget("duplicate JSON key")
        out[k] = v
    return out


def report(root: Path = ROOT) -> dict:
    path = root / CANDIDATE
    if not path.is_file() or path.is_symlink():
        raise UnfrozenTarget("candidate unavailable or symlinked")
    raw = path.read_bytes()
    if git_blob(raw) != CANDIDATE_GIT_BLOB:
        raise UnfrozenTarget("candidate exact Git blob drift")
    try:
        doc = json.loads(raw, object_pairs_hook=reject_dups,
                         parse_constant=lambda _: (_ for _ in ()).throw(UnfrozenTarget("nonfinite")))
    except (UnicodeDecodeError, ValueError) as exc:
        raise UnfrozenTarget("invalid candidate JSON") from exc
    if (not isinstance(doc, dict)
            or doc.get("schema_version") != "app8-execution-target-selection-v1"
            or doc.get("status") != "CANDIDATE_FOR_FRESH_REVIEW"
            or not isinstance(doc.get("targets"), list)
            or len(doc["targets"]) != 4):
        raise UnfrozenTarget("candidate shape/status mismatch")
    by_asset = {}
    for item in doc["targets"]:
        if not isinstance(item, dict):
            raise UnfrozenTarget("invalid target entry")
        name = item.get("asset")
        if name not in ASSETS or name in by_asset:
            raise UnfrozenTarget("invalid or duplicated target asset")
        knowledge, target = item.get("knowledge_source"), item.get("execution_target")
        if not isinstance(knowledge, dict) or not isinstance(target, dict):
            raise UnfrozenTarget("target missing identity")
        if (knowledge.get("commit") != EXPECTED_SOURCES[name]
                or target.get("repository_relation") != EXPECTED_RELATIONS[name]):
            raise UnfrozenTarget("target/source identity mismatch")
        by_asset[name] = target

    result = []
    for name in ASSETS:
        candidate = by_asset[name]
        checksums = {}
        for obj in candidate.get("artifacts", []):
            checksums[obj["name"]] = obj["sha256"]
        if "sha256" in candidate:
            checksums[candidate.get("package", name)] = candidate["sha256"]
        if "installer_sha256" in candidate:
            checksums["official_installer"] = candidate["installer_sha256"]
        if not checksums or any(not isinstance(v, str) or len(v) != 64
                                or any(ch not in "0123456789abcdef" for ch in v)
                                for v in checksums.values()):
            raise UnfrozenTarget(f"{name} missing expected SHA256 artifacts")
        gaps = ["final_four_asset_manifest_review",
                "approved_target_applicability_evidence_SHA256",
                "real_execution_identity_revalidation_before_scoring"]
        if name == "pandas":
            gaps.append("freeze_exact_numpy_python_dateutil_six_dependencies")
        if name == "LibreOffice":
            gaps.append("prove_release_specific_applicability_for_DIVERGED_source")
        result.append({
            "asset":name,
            "knowledge_source_sha":EXPECTED_SOURCES[name],
            "candidate_mapping_class":candidate.get("mapping_class"),
            "candidate_repository_relation":EXPECTED_RELATIONS[name],
            "artifact_expected_sha256":checksums,
            "runtime_lane":candidate.get("runtime_lane"),
            "candidate_recorded_readiness":candidate.get("readiness"),
            "remaining_freeze_gates":gaps,
            "independent_applicability_approved":False,
        })
    return {
        "schema_version":"app8-v04-se11-public-target-gaps-v1",
        "frozen_candidate_git_blob":CANDIDATE_GIT_BLOB,
        "current_protocol_git_blob":"1204c717eb590071a7b7f7e1cd3018b825ef1617",
        "targets":result,
        "final_se11_execution_target_manifest_generated":False,
        "independent_applicability_approval_generated":False,
        "hidden_truth_generated":False,
        "se11_empirical_status":"NOT_RUN",
        "product_release_qualified":False,
    }


def main() -> int:
    parser=argparse.ArgumentParser(description="Unapproved public SE11 target gap report only")
    parser.add_argument("--repo-root",type=Path,default=ROOT)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    try:
        data=report(args.repo_root)
    except (OSError, UnfrozenTarget) as exc:
        parser.exit(2,"BLOCKED: "+str(exc)+"\n")
    args.out.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("TARGETS=4 APPROVED_FINAL_MANIFEST=NO HIDDEN_TRUTH=NO")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
