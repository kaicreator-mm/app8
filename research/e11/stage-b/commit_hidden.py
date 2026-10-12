#!/usr/bin/env python3
"""SE11: commit a sealed PRIVATE truth corpus without exposing claim semantics."""
import argparse
import hashlib
import json
import pathlib
import re
import sys
import uuid

ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
CLASSES = ("TRUE", "MATERIALLY_FALSE", "OVERBROAD", "NEAR_MISS")
EXPECTED = {"TRUE": 8, "MATERIALLY_FALSE": 4, "OVERBROAD": 4, "NEAR_MISS": 4}
ID_RE = re.compile(r"H_[0-9a-f]{32}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
ROOT_FIELDS = {
    "schema_version", "stage_a_merge", "execution_target_manifest_sha256",
    "source_execution_mapping_frozen", "truth_visible_to_llm_b",
    "decisive_fixtures_visible_to_llm_b", "curator_isolation_declaration", "claims"
}
CLAIM_FIELDS = {
    "id", "asset", "truth_class", "claim_text", "binding_id",
    "decisive_fixture_ref", "expected_behavior", "provenance",
    "reset_requirements", "target_applicability_evidence_ref"
}
STAGE_A = "0279968580d50e51843b09aa2b6e266b9967ff93"


def fail(message):
    print("ERROR: " + message, file=sys.stderr)
    raise SystemExit(2)


def exact_fields(obj, expected, where):
    if not isinstance(obj, dict) or set(obj) != expected:
        fail(f"{where}: required/exclusive fields mismatch")


def nonblank(value, where):
    if not isinstance(value, str) or not value.strip():
        fail(f"{where}: must be nonblank string")


def validate(doc):
    exact_fields(doc, ROOT_FIELDS, "root")
    if doc["schema_version"] != "se11-hidden-v1":
        fail("invalid schema_version")
    if doc["stage_a_merge"] != STAGE_A:
        fail("Stage A identity mismatch")
    target = doc["execution_target_manifest_sha256"]
    if not isinstance(target, str) or not SHA256_RE.fullmatch(target):
        fail("execution_target_manifest_sha256 must be lowercase SHA-256")
    if doc["source_execution_mapping_frozen"] is not True:
        fail("source_execution_mapping_frozen must be true")
    if doc["truth_visible_to_llm_b"] is not False:
        fail("truth_visible_to_llm_b must be false")
    if doc["decisive_fixtures_visible_to_llm_b"] is not False:
        fail("decisive_fixtures_visible_to_llm_b must be false")
    nonblank(doc["curator_isolation_declaration"], "curator_isolation_declaration")
    claims = doc["claims"]
    if not isinstance(claims, list) or len(claims) != 80:
        fail("exactly 80 claims required")

    matrix = {a: {c: 0 for c in CLASSES} for a in ASSETS}
    ids, seen = [], set()
    for index, claim in enumerate(claims):
        exact_fields(claim, CLAIM_FIELDS, f"claims[{index}]")
        cid, asset, category = claim["id"], claim["asset"], claim["truth_class"]
        if not isinstance(cid, str) or not ID_RE.fullmatch(cid):
            fail("claim ID must be opaque H_<UUID4-hex> identifier")
        parsed_id = uuid.UUID(hex=cid[2:])
        if parsed_id.version != 4 or parsed_id.variant != uuid.RFC_4122:
            fail("claim ID must use a random UUIDv4 rather than sequence-derived IDs")
        if cid in seen:
            fail(f"duplicate claim ID: {cid}")
        seen.add(cid)
        if asset not in matrix:
            fail(f"{cid}: unsupported asset")
        if category not in EXPECTED:
            fail(f"{cid}: unsupported truth category")
        for field in (
            "claim_text", "binding_id", "decisive_fixture_ref",
            "expected_behavior", "provenance", "reset_requirements",
            "target_applicability_evidence_ref"
        ):
            nonblank(claim[field], f"{cid}.{field}")
        matrix[asset][category] += 1
        ids.append(cid)

    for asset in ASSETS:
        for category, wanted in EXPECTED.items():
            if matrix[asset][category] != wanted:
                fail(f"{asset}/{category}: expected {wanted}, got {matrix[asset][category]}")
    return ids, matrix, target


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hidden_file", type=pathlib.Path)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()
    source, output = args.hidden_file.resolve(), args.out.resolve()
    if source == output:
        fail("public output cannot overwrite private corpus")
    if any((parent / ".git").exists() for parent in (source.parent, *source.parents)):
        fail("private hidden corpus must be outside any Git repository")
    if not source.is_file():
        fail("private hidden corpus does not exist")
    raw = source.read_bytes()
    try:
        doc = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        fail(f"invalid hidden JSON: {exc}")

    ids, matrix, target = validate(doc)
    public = {
        "schema_version": "se11-public-commitment-v1",
        "stage_a_merge": STAGE_A,
        "execution_target_manifest_sha256": target,
        "source_execution_mapping_frozen": True,
        "hidden_file_sha256": hashlib.sha256(raw).hexdigest(),
        "hidden_file_bytes": len(raw),
        "claim_count": len(ids),
        "asset_counts": {a: sum(matrix[a].values()) for a in ASSETS},
        "aggregate_class_counts": {
            category: sum(matrix[a][category] for a in ASSETS)
            for category in CLASSES
        },
        "opaque_claim_ids": sorted(ids),
        "truth_visible_to_llm_b": False,
        "decisive_fixtures_visible_to_llm_b": False,
        "semantic_truth_in_public_output": False
    }
    output.write_text(json.dumps(public, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PUBLIC_COMMITMENT={output}")
    print(f"CLAIM_COUNT={len(ids)}")
    print(f"SHA256={public['hidden_file_sha256']}")


if __name__ == "__main__":
    main()
