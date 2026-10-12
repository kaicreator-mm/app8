#!/usr/bin/env python3
"""SE11: commit a sealed PRIVATE truth corpus without exposing claim semantics."""
import argparse
import hashlib
import hmac
import json
import pathlib
import re
import sys

ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
CLASSES = ("TRUE", "MATERIALLY_FALSE", "OVERBROAD", "NEAR_MISS")
EXPECTED = {"TRUE": 8, "MATERIALLY_FALSE": 4, "OVERBROAD": 4, "NEAR_MISS": 4}
ID_RE = re.compile(r"H_[0-9a-f]{32}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
ROOT_FIELDS = {
    "schema_version", "stage_a_merge", "execution_target_manifest_sha256",
    "source_execution_mapping_frozen", "source_execution_mappings",
    "id_scheme", "id_secret_hex", "truth_visible_to_llm_b",
    "decisive_fixtures_visible_to_llm_b", "curator_isolation_declaration", "claims"
}
CLAIM_FIELDS = {
    "id", "id_nonce", "asset", "truth_class", "claim_text", "binding_id",
    "decisive_fixture_ref", "expected_behavior", "provenance",
    "reset_requirements", "target_applicability"
}
MAPPING_FIELDS = {"execution_target_ref", "relation", "applicability_review_sha256", "applicability_review_status"}
APPLICABILITY_FIELDS = {"mapping_relation", "evidence_kind", "evidence_sha256", "independent_review_status"}
RELATIONS = {"SAME", "KNOWLEDGE_SOURCE_ANCESTOR", "KNOWLEDGE_SOURCE_DESCENDANT", "DIVERGED", "UNRESOLVED"}
EVIDENCE_KINDS = {"EXACT_SOURCE_IDENTITY", "RELEASE_SPECIFIC_SOURCE", "DETERMINISTIC_TARGET_PROBE"}
ID_SCHEME = "HMAC_SHA256_UUIDV4_V1"
STAGE_A = "0279968580d50e51843b09aa2b6e266b9967ff93"


def fail(message):
    print("ERROR: " + message, file=sys.stderr)
    raise SystemExit(2)


def reject_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def reject_nonfinite(value):
    raise ValueError(f"unsupported JSON constant: {value}")


def strict_json_loads(raw):
    return json.loads(
        raw,
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_nonfinite,
    )


def exact_fields(obj, expected, where):
    if not isinstance(obj, dict) or set(obj) != expected:
        fail(f"{where}: required/exclusive fields mismatch")


def nonblank(value, where):
    if not isinstance(value, str) or not value.strip():
        fail(f"{where}: must be nonblank string")


def derive_claim_id(secret_hex, nonce):
    if not isinstance(secret_hex, str) or not SHA256_RE.fullmatch(secret_hex):
        fail("id_secret_hex must be 256-bit lowercase hex")
    nonblank(nonce, "id_nonce")
    digest = bytearray(hmac.new(bytes.fromhex(secret_hex), nonce.encode("utf-8"), hashlib.sha256).digest()[:16])
    digest[6] = (digest[6] & 0x0F) | 0x40
    digest[8] = (digest[8] & 0x3F) | 0x80
    return "H_" + bytes(digest).hex()


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
    if doc["id_scheme"] != ID_SCHEME:
        fail("id_scheme mismatch")
    secret = doc["id_secret_hex"]
    if not isinstance(secret, str) or not SHA256_RE.fullmatch(secret):
        fail("id_secret_hex must be 256-bit lowercase hex")
    mappings = doc["source_execution_mappings"]
    if not isinstance(mappings, dict) or set(mappings) != set(ASSETS):
        fail("source_execution_mappings must contain exactly four assets")
    for asset, mapping in mappings.items():
        exact_fields(mapping, MAPPING_FIELDS, f"source_execution_mappings.{asset}")
        nonblank(mapping["execution_target_ref"], f"{asset}.execution_target_ref")
        if mapping["relation"] not in RELATIONS:
            fail(f"{asset}: invalid source/execution relation")
        review_sha = mapping["applicability_review_sha256"]
        if not isinstance(review_sha, str) or not SHA256_RE.fullmatch(review_sha):
            fail(f"{asset}: applicability review must be SHA-256")
        if mapping["applicability_review_status"] != "PASS":
            fail(f"{asset}: applicability review must PASS before hidden freeze")
        if mapping["relation"] == "UNRESOLVED":
            fail(f"{asset}: UNRESOLVED mapping cannot enter hidden corpus freeze")
    if doc["truth_visible_to_llm_b"] is not False:
        fail("truth_visible_to_llm_b must be false")
    if doc["decisive_fixtures_visible_to_llm_b"] is not False:
        fail("decisive_fixtures_visible_to_llm_b must be false")
    nonblank(doc["curator_isolation_declaration"], "curator_isolation_declaration")
    claims = doc["claims"]
    if not isinstance(claims, list) or len(claims) != 80:
        fail("exactly 80 claims required")

    matrix = {a: {c: 0 for c in CLASSES} for a in ASSETS}
    ids, seen, nonces = [], set(), set()
    for index, claim in enumerate(claims):
        exact_fields(claim, CLAIM_FIELDS, f"claims[{index}]")
        cid, nonce, asset, category = claim["id"], claim["id_nonce"], claim["asset"], claim["truth_class"]
        if not isinstance(cid, str) or not ID_RE.fullmatch(cid):
            fail("claim ID must be opaque H_<UUID4-hex> identifier")
        expected_id = derive_claim_id(secret, nonce)
        if cid != expected_id:
            fail("claim ID must be HMAC-derived from the private corpus secret and nonce")
        if nonce in nonces:
            fail("duplicate id_nonce")
        nonces.add(nonce)
        if cid in seen:
            fail(f"duplicate claim ID: {cid}")
        seen.add(cid)
        if asset not in matrix:
            fail(f"{cid}: unsupported asset")
        if category not in EXPECTED:
            fail(f"{cid}: unsupported truth category")
        for field in (
            "claim_text", "binding_id", "decisive_fixture_ref",
            "expected_behavior", "provenance", "reset_requirements"
        ):
            nonblank(claim[field], f"{cid}.{field}")
        applicability = claim["target_applicability"]
        exact_fields(applicability, APPLICABILITY_FIELDS, f"{cid}.target_applicability")
        relation = mappings[asset]["relation"]
        if applicability["mapping_relation"] != relation:
            fail(f"{cid}: target applicability relation does not match frozen asset mapping")
        if applicability["evidence_kind"] not in EVIDENCE_KINDS:
            fail(f"{cid}: invalid applicability evidence kind")
        evidence_sha = applicability["evidence_sha256"]
        if not isinstance(evidence_sha, str) or not SHA256_RE.fullmatch(evidence_sha):
            fail(f"{cid}: applicability evidence must be SHA-256")
        if applicability["independent_review_status"] != "PASS":
            fail(f"{cid}: applicability evidence must be independently PASS-reviewed")
        if relation in {"DIVERGED", "KNOWLEDGE_SOURCE_ANCESTOR", "KNOWLEDGE_SOURCE_DESCENDANT"} and applicability["evidence_kind"] == "EXACT_SOURCE_IDENTITY":
            fail(f"{cid}: non-SAME mapping requires release-specific source or deterministic target evidence")
        matrix[asset][category] += 1
        ids.append(cid)

    for asset in ASSETS:
        for category, wanted in EXPECTED.items():
            if matrix[asset][category] != wanted:
                fail(f"{asset}/{category}: expected {wanted}, got {matrix[asset][category]}")
    return ids, matrix, target, secret, mappings


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
        doc = strict_json_loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        fail(f"invalid hidden JSON: {exc}")

    ids, matrix, target, secret, mappings = validate(doc)
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
        "id_scheme": ID_SCHEME,
        "id_secret_sha256": hashlib.sha256(bytes.fromhex(secret)).hexdigest(),
        "source_execution_relations": {asset: mappings[asset]["relation"] for asset in ASSETS},
        "source_execution_applicability_review_sha256": {
            asset: mappings[asset]["applicability_review_sha256"] for asset in ASSETS
        },
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
