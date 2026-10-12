#!/usr/bin/env python3
import argparse, hashlib, json, pathlib, sys

ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
MIN_PER_ASSET = 12
REQUIRED_CAP_FIELDS = {
    "id", "asset", "canonical_identity", "purpose", "source_anchors",
    "variants", "constraints", "negative_boundaries", "failure_semantics",
    "binding_equivalence_group", "ambiguity"
}

def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gold_file", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    args = ap.parse_args()

    raw = args.gold_file.read_bytes()
    try:
        doc = json.loads(raw)
    except Exception as e:
        fail(f"invalid JSON: {e}")

    if doc.get("schema_version") != "se10-gold-v1":
        fail("schema_version must be se10-gold-v1")
    if doc.get("source_pack_blob") != "4b3c9b62b1899653524f19a286924f942605210a":
        fail("source_pack_blob mismatch")
    if doc.get("model_generated_gold") is not False:
        fail("model_generated_gold must be false")
    if doc.get("predictor_gold_visibility") is not False:
        fail("predictor_gold_visibility must be false")

    caps = doc.get("capabilities")
    if not isinstance(caps, list):
        fail("capabilities must be a list")

    counts = {a: 0 for a in ASSETS}
    ids = []
    ambiguity_count = 0
    seen = set()

    for idx, cap in enumerate(caps):
        if not isinstance(cap, dict):
            fail(f"capability[{idx}] must be object")
        missing = sorted(REQUIRED_CAP_FIELDS - set(cap))
        if missing:
            fail(f"capability[{idx}] missing fields: {missing}")
        cid = cap["id"]
        asset = cap["asset"]
        if not isinstance(cid, str) or not cid:
            fail(f"capability[{idx}].id must be non-empty string")
        if cid in seen:
            fail(f"duplicate id: {cid}")
        seen.add(cid)
        if asset not in counts:
            fail(f"unsupported asset for {cid}: {asset}")
        anchors = cap["source_anchors"]
        if not isinstance(anchors, list) or not anchors:
            fail(f"{cid}: source_anchors must be non-empty list")
        for anchor in anchors:
            if not isinstance(anchor, dict) or not {"path", "blob"} <= set(anchor):
                fail(f"{cid}: each source anchor needs path and blob")
            if not isinstance(anchor["path"], str) or not isinstance(anchor["blob"], str) or len(anchor["blob"]) != 40:
                fail(f"{cid}: invalid source anchor")
        if not isinstance(cap["ambiguity"], bool):
            fail(f"{cid}: ambiguity must be boolean")
        ambiguity_count += int(cap["ambiguity"])
        counts[asset] += 1
        ids.append(cid)

    for asset, count in counts.items():
        if count < MIN_PER_ASSET:
            fail(f"{asset}: requires >= {MIN_PER_ASSET}, got {count}")

    commitment = {
        "schema_version": "se10-public-commitment-v1",
        "source_pack_blob": doc["source_pack_blob"],
        "gold_file_sha256": hashlib.sha256(raw).hexdigest(),
        "gold_file_bytes": len(raw),
        "capability_count": len(caps),
        "asset_counts": counts,
        "opaque_reference_ids": sorted(ids),
        "ambiguity_count": ambiguity_count,
        "model_generated_gold": False,
        "predictor_gold_visibility": False,
        "semantic_gold_in_public_output": False,
    }
    args.out.write_text(json.dumps(commitment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {args.out}")
    print(f"GOLD_SHA256={commitment['gold_file_sha256']}")
    print(f"CAPABILITY_COUNT={len(caps)}")
    print("ASSET_COUNTS=" + ",".join(f"{a}:{counts[a]}" for a in ASSETS))

if __name__ == "__main__":
    main()
