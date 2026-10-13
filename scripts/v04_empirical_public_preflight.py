#!/usr/bin/env python3
"""Read-only preflight for SE10/SE11 PUBLIC identities; never reads sealed truth.

A metadata check is NOT evidence of independent humans, real execution,
empirical PASS or product Release qualification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
PINS = {
    "se10_protocol": ("docs/product/v0.1-successor/l1/SE10_PROTOCOL.md",
                      "08f9244a04275c780f778d50f638e332aa5807a2"),
    "se10_source_pack": ("docs/product/v0.1-successor/l1/SE10_SOURCE_PACK_MANIFEST.md",
                         "4b3c9b62b1899653524f19a286924f942605210a"),
    "se10_allowlist": ("research/e10/stage-b/source_anchor_allowlist.json",
                       "5be0ed7674fcdfd7361a57fd4f29a6f9655c1df1"),
    "se10_scorer": ("research/e10/stage-c/stage_c.py",
                    "d443ef5e1d50c011935be682ae0513e695683990"),
    "se11_protocol": ("docs/product/v0.1-successor/l1/SE11_PROTOCOL.md",
                      "1204c717eb590071a7b7f7e1cd3018b825ef1617"),
    "se11_scorer": ("research/e11/stage-c/stage_c.py",
                    "50c9569746d5a6b9bdabfee6b9369cc1da3e3ae5"),
}
SE10_PUBLIC_FIELDS = {
    "schema_version", "source_pack_blob", "gold_file_sha256",
    "independent_attestation_sha256", "human_independence_requires_external_review",
    "gold_file_bytes", "capability_count", "asset_counts", "opaque_reference_ids",
    "ambiguity_count", "human_author_identity_class", "human_reviewer_identity_class",
    "independence_declaration", "isolation_statement", "adjudication_procedure_sha256",
    "adjudication_code_sha256", "private_store_class", "private_store_independent_reviewed",
    "allowlist_git_blob", "declared_model_generated_gold", "declared_predictor_gold_visibility",
    "semantic_gold_in_public_output",
}
SE11_PUBLIC_FIELDS = {
    "schema_version", "stage_a_merge", "execution_target_manifest_sha256",
    "source_execution_mapping_frozen", "hidden_file_sha256", "hidden_file_bytes",
    "claim_count", "asset_counts", "aggregate_class_counts", "opaque_claim_ids",
    "id_scheme", "id_secret_sha256", "source_execution_relations",
    "source_execution_applicability_review_sha256", "truth_visible_to_llm_b",
    "decisive_fixtures_visible_to_llm_b", "semantic_truth_in_public_output",
}
CLASS_COUNTS = {"TRUE": 32, "MATERIALLY_FALSE": 16, "OVERBROAD": 16, "NEAR_MISS": 16}


def _git_blob(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def _nodup(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("duplicate JSON key")
        result[k] = v
    return result


def _strict_read(path: Path | None, label: str, blockers: list[str]):
    if path is None:
        blockers.append(f"{label}:PUBLIC_ARTIFACT_MISSING")
        return None, None
    if path.is_symlink() or not path.is_file():
        blockers.append(f"{label}:NOT_A_REGULAR_FILE")
        return None, None
    try:
        raw = path.read_bytes()
        if len(raw) > 2_000_000:
            raise ValueError("oversized public metadata")
        parsed = json.loads(raw, object_pairs_hook=_nodup,
                            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite number")))
        if not isinstance(parsed, dict):
            raise ValueError("public metadata is not a JSON object")
        return raw, parsed
    except (OSError, UnicodeDecodeError, ValueError):
        blockers.append(f"{label}:INVALID_PUBLIC_JSON")
        return None, None


def _pins(repo: Path, blockers: list[str]) -> dict:
    observed = {}
    for label, (relative, expected) in PINS.items():
        path = repo / relative
        try:
            if path.is_symlink() or not path.is_file():
                raise OSError("not a regular file")
            actual = _git_blob(path.read_bytes())
        except OSError:
            blockers.append(f"{label}:PIN_FILE_UNAVAILABLE")
            continue
        observed[label] = actual
        if actual != expected:
            blockers.append(f"{label}:EXACT_GIT_BLOB_DRIFT")
    return observed


def _se10(gold_path: Path | None, prediction_path: Path | None, blockers: list[str]):
    raw, gold = _strict_read(gold_path, "SE10_GOLD_COMMITMENT", blockers)
    pred_raw, pred = _strict_read(prediction_path, "SE10_PREDICTION_COMMITMENT", blockers)
    if gold is not None:
        counts = gold.get("asset_counts")
        if (set(gold) != SE10_PUBLIC_FIELDS
                or gold.get("schema_version") != "se10-public-commitment-v1"
                or gold.get("source_pack_blob") != PINS["se10_source_pack"][1]
                or gold.get("allowlist_git_blob") != PINS["se10_allowlist"][1]
                or not _is_sha(gold.get("gold_file_sha256"))
                or not _is_sha(gold.get("independent_attestation_sha256"))
                or not _is_sha(gold.get("adjudication_procedure_sha256"))
                or not _is_sha(gold.get("adjudication_code_sha256"))
                or gold.get("human_author_identity_class") != "INDEPENDENT_HUMAN_DOMAIN_CURATOR"
                or gold.get("human_reviewer_identity_class") != "INDEPENDENT_HUMAN_GOLD_REVIEWER"
                or gold.get("independence_declaration") !=
                   "INDEPENDENT_HUMANS_NO_MODEL_GOLD_NO_PREDICTOR_ACCESS"
                or gold.get("private_store_class") !=
                   "SEALED_ACCESS_CONTROLLED_OUTSIDE_DISCOVERABLE_GIT"
                or not isinstance(gold.get("isolation_statement"), str)
                or not gold["isolation_statement"].strip()
                or type(gold.get("gold_file_bytes")) is not int or gold["gold_file_bytes"] <= 0
                or gold.get("human_independence_requires_external_review") is not True
                or gold.get("declared_model_generated_gold") is not False
                or gold.get("declared_predictor_gold_visibility") is not False
                or gold.get("semantic_gold_in_public_output") is not False
                or not isinstance(counts, dict) or set(counts) != set(ASSETS)
                or any(type(counts[k]) is not int or counts[k] < 12 for k in ASSETS)
                or gold.get("capability_count") != sum(counts.values())
                or not isinstance(gold.get("opaque_reference_ids"), list)
                or len(gold["opaque_reference_ids"]) != gold["capability_count"]
                or len(set(map(str, gold["opaque_reference_ids"]))) != gold["capability_count"]
                or not all(isinstance(x, str) and re.fullmatch(r"G[0-9]{4,6}", x)
                           for x in gold["opaque_reference_ids"])
                or type(gold.get("ambiguity_count")) is not int
                or gold["ambiguity_count"] < 0
                or gold["ambiguity_count"] > gold["capability_count"]
                or gold.get("private_store_independent_reviewed") is not True):
            blockers.append("SE10_GOLD_COMMITMENT:INVALID_FROZEN_METADATA")
    if pred is not None:
        if (pred.get("schema_version") != "se10-prediction-commitment-v1"
                or raw is None
                or pred.get("gold_commitment_sha256") != _sha(raw)
                or not _is_sha(pred.get("prediction_file_sha256"))
                or not _is_sha(pred.get("gold_file_sha256"))
                or gold is None or pred.get("gold_file_sha256") != gold.get("gold_file_sha256")):
            blockers.append("SE10_PREDICTION_COMMITMENT:PIN_OR_SCHEMA_MISMATCH")
    return bool(gold is not None and pred is not None)


def _se11(manifest_path: Path | None, hidden_path: Path | None, blockers: list[str]):
    manifest_raw, manifest = _strict_read(manifest_path, "SE11_TARGET_MANIFEST", blockers)
    hidden_raw, hidden = _strict_read(hidden_path, "SE11_HIDDEN_COMMITMENT", blockers)
    if manifest is not None:
        mappings = manifest.get("source_execution_mappings")
        if (manifest.get("schema_version") != "se11-execution-target-manifest-v1"
                or not isinstance(mappings, dict) or set(mappings) != set(ASSETS)):
            blockers.append("SE11_TARGET_MANIFEST:UNAPPROVED_OR_INCOMPLETE")
        else:
            for asset, mapping in mappings.items():
                approved = mapping.get("approved_applicability_evidence") if isinstance(mapping, dict) else None
                if (not isinstance(mapping, dict)
                        or set(mapping) != {"execution_target_ref", "relation", "applicability_review_sha256",
                                            "applicability_review_status", "approved_applicability_evidence"}
                        or mapping.get("relation") not in {"SAME", "KNOWLEDGE_SOURCE_ANCESTOR",
                                                            "KNOWLEDGE_SOURCE_DESCENDANT", "DIVERGED"}
                        or not isinstance(mapping.get("execution_target_ref"), str)
                        or not mapping["execution_target_ref"].strip()
                        or not _is_sha(mapping.get("applicability_review_sha256"))
                        or mapping.get("applicability_review_status") != "PASS"
                        or not isinstance(approved, list) or not approved
                        or any(not isinstance(x, dict)
                               or x.get("evidence_kind") not in
                                   {"EXACT_SOURCE_IDENTITY", "RELEASE_SPECIFIC_SOURCE", "DETERMINISTIC_TARGET_PROBE"}
                               or not _is_sha(x.get("evidence_sha256")) for x in approved)):
                    blockers.append(f"SE11_TARGET_MANIFEST:{asset}:UNAPPROVED_APPLICABILITY")
    if hidden is not None:
        counts = hidden.get("asset_counts")
        classes = hidden.get("aggregate_class_counts")
        claim_ids = hidden.get("opaque_claim_ids")
        if (set(hidden) != SE11_PUBLIC_FIELDS
                or hidden.get("schema_version") != "se11-public-commitment-v1"
                or manifest_raw is None
                or hidden.get("execution_target_manifest_sha256") != _sha(manifest_raw)
                or hidden.get("stage_a_merge") != "0279968580d50e51843b09aa2b6e266b9967ff93"
                or not _is_sha(hidden.get("hidden_file_sha256"))
                or not _is_sha(hidden.get("id_secret_sha256"))
                or hidden.get("id_scheme") != "HMAC_SHA256_UUIDV4_V1"
                or hidden.get("source_execution_mapping_frozen") is not True
                or type(hidden.get("hidden_file_bytes")) is not int
                or hidden["hidden_file_bytes"] <= 0
                or not isinstance(hidden.get("source_execution_relations"), dict)
                or not isinstance(hidden.get("source_execution_applicability_review_sha256"), dict)
                or manifest is None
                or set(hidden["source_execution_relations"]) != set(ASSETS)
                or set(hidden["source_execution_applicability_review_sha256"]) != set(ASSETS)
                or any(hidden["source_execution_relations"][a] !=
                           manifest.get("source_execution_mappings", {}).get(a, {}).get("relation")
                       for a in ASSETS)
                or any(not _is_sha(hidden["source_execution_applicability_review_sha256"][a])
                       or hidden["source_execution_applicability_review_sha256"][a] !=
                           manifest.get("source_execution_mappings", {}).get(a, {}).get("applicability_review_sha256")
                       for a in ASSETS)
                or hidden.get("claim_count") != 80
                or not isinstance(counts, dict)
                or set(counts) != set(ASSETS)
                or any(type(counts[k]) is not int or counts[k] != 20 for k in ASSETS)
                or classes != CLASS_COUNTS
                or not isinstance(claim_ids, list) or len(claim_ids) != 80
                or len(set(map(str, claim_ids))) != 80
                or not all(isinstance(x, str) and re.fullmatch(r"H_[0-9a-f]{32}", x) for x in claim_ids)
                or hidden.get("truth_visible_to_llm_b") is not False
                or hidden.get("decisive_fixtures_visible_to_llm_b") is not False
                or hidden.get("semantic_truth_in_public_output") is not False):
            blockers.append("SE11_HIDDEN_COMMITMENT:PIN_OR_SCHEMA_MISMATCH")
    return bool(manifest is not None and hidden is not None)


def assess(repo: Path, se10_gold: Path | None = None, se10_prediction: Path | None = None,
           se11_target: Path | None = None, se11_hidden: Path | None = None) -> dict:
    """Safe public-metadata preflight only, never read or expose private Gold/truth."""
    blockers: list[str] = []
    actual = _pins(repo, blockers)
    start_10 = len(blockers)
    _se10(se10_gold, se10_prediction, blockers)
    se10_issues = blockers[start_10:]
    start_11 = len(blockers)
    _se11(se11_target, se11_hidden, blockers)
    se11_issues = blockers[start_11:]
    return {
        "schema_version": "app8-v04-public-preflight-v1",
        "se10": "BLOCKED_PRE_EVALUATION" if se10_issues or len(actual) != len(PINS)
                or any(actual.get(x) != pin for x, (_, pin) in PINS.items())
                else "PUBLIC_METADATA_PRESENT_UNVERIFIED_INDEPENDENCE",
        "se11": "BLOCKED_PRE_EVALUATION" if se11_issues or len(actual) != len(PINS)
                or any(actual.get(x) != pin for x, (_, pin) in PINS.items())
                else "PUBLIC_METADATA_PRESENT_UNVERIFIED_INDEPENDENCE",
        "blocked_reasons": blockers,
        "repo_pin_git_blobs": actual,
        "se10_empirical": "NOT_PROVEN",
        "se11_empirical": "NOT_PROVEN",
        "independent_truth_and_real_execution_verified": False,
        "formal_product_release_qualified": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Public-only SE10/SE11 preflight; NOT empirical scoring")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--se10-gold-public", type=Path)
    parser.add_argument("--se10-prediction-public", type=Path)
    parser.add_argument("--se11-target-manifest", type=Path)
    parser.add_argument("--se11-hidden-public", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = assess(args.repo_root, args.se10_gold_public, args.se10_prediction_public,
                    args.se11_target_manifest, args.se11_hidden_public)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("SE10=" + result["se10"] + " SE11=" + result["se11"])
    return 2 if result["blocked_reasons"] else 0


if __name__ == "__main__":
    sys.exit(main())
