#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, sys

ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
CLASSES = ("TRUE", "MATERIALLY_FALSE", "OVERBROAD", "NEAR_MISS")
EXPECTED = {"TRUE": 8, "MATERIALLY_FALSE": 4, "OVERBROAD": 4, "NEAR_MISS": 4}
REQUIRED = {
    "id", "asset", "truth_class", "claim_text", "binding_id",
    "decisive_fixture_ref", "expected_behavior", "provenance", "reset_requirements"
}

def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hidden_file", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    raw = args.hidden_file.read_bytes()
    try:
        doc = json.loads(raw)
    except Exception as e:
        fail(f"invalid JSON: {e}")

    if doc.get("schema_version") != "se11-hidden-v1":
        fail("schema_version must be se11-hidden-v1")
    if doc.get("stage_a_merge") != "0279968580d50e51843b09aa2b6e266b9967ff93":
        fail("stage_a_merge mismatch")
    if doc.get("truth_visible_to_llm_b") is not False:
        fail("truth_visible_to_llm_b must be false")
    if doc.get("decisive_fixtures_visible_to_llm_b") is not False:
        fail("decisive_fixtures_visible_to_llm_b must be false")

    claims = doc.get("claims")
    if not isinstance(claims, list) or len(claims) != 80:
        fail("claims must contain exactly 80 records")

    matrix = {a: {c: 0 for c in CLASSES} for a in ASSETS}
    ids, seen = [], set()

    for idx, claim in enumerate(claims):
        if not isinstance(claim, dict):
            fail(f"claim[{idx}] must be object")
        missing = sorted(REQUIRED - set(claim))
        if missing:
            fail(f"claim[{idx}] missing fields: {missing}")
        cid, asset, cls = claim["id"], claim["asset"], claim["truth_class"]
        if not isinstance(cid, str) or not cid:
            fail(f"claim[{idx}].id must be non-empty string")
        if cid in seen:
            fail(f"duplicate id: {cid}")
        seen.add(cid)
        if asset not in matrix:
            fail(f"unknown asset: {asset}")
        if cls not in EXPECTED:
            fail(f"unknown truth class: {cls}")
        for field in ("claim_text","binding_id","decisive_fixture_ref","expected_behavior","provenance","reset_requirements"):
            if not isinstance(claim[field], str) or not claim[field].strip():
                fail(f"{cid}: {field} must be non-empty string")
        matrix[asset][cls] += 1
        ids.append(cid)

    for asset in ASSETS:
        for cls, expected in EXPECTED.items():
            actual = matrix[asset][cls]
            if actual != expected:
                fail(f"{asset}/{cls}: expected {expected}, got {actual}")

    aggregate = {c: sum(matrix[a][c] for a in ASSETS) for c in CLASSES}
    commitment = {
        "schema_version": "se11-public-commitment-v1",
        "stage_a_merge": doc["stage_a_merge"],
        "hidden_file_sha256": hashlib.sha256(raw).hexdigest(),
        "hidden_file_bytes": len(raw),
        "claim_count": 80,
        "asset_counts": {a: sum(matrix[a].values()) for a in ASSETS},
        "aggregate_class_counts": aggregate,
        "opaque_claim_ids": sorted(ids),
        "truth_visible_to_llm_b": False,
        "decisive_fixtures_visible_to_llm_b": False,
        "semantic_truth_in_public_output": False,
    }
    args.out.write_text(json.dumps(commitment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {args.out}")
    print(f"HIDDEN_SHA256={commitment['hidden_file_sha256']}")
    print("CLAIM_COUNT=80")

if __name__ == "__main__":
    main()
