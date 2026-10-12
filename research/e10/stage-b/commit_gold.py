#!/usr/bin/env python3
"""SE10: structurally validate PRIVATE human gold, emit only a public commitment."""
import argparse
import hashlib
import json
import pathlib
import re
import sys

ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
SOURCE_PACK_BLOB = "4b3c9b62b1899653524f19a286924f942605210a"
ID_RE = re.compile(r"G[0-9]{4,6}\Z")
SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
ROOT_FIELDS = {
    "schema_version", "source_pack_blob", "model_generated_gold",
    "predictor_gold_visibility", "human_author_declaration", "capabilities"
}
CAP_FIELDS = {
    "id", "asset", "canonical_identity", "purpose", "source_anchors",
    "variants", "constraints", "negative_boundaries", "failure_semantics",
    "binding_equivalence_group", "ambiguity"
}
ANCHOR_FIELDS = {"path", "blob"}
ARRAY_FIELDS = ("variants", "constraints", "negative_boundaries", "failure_semantics")


def fail(message):
    print("ERROR: " + message, file=sys.stderr)
    raise SystemExit(2)


def exact_fields(obj, expected, where):
    if not isinstance(obj, dict) or set(obj) != expected:
        fail(f"{where}: required/exclusive fields mismatch")


def nonblank(value, where):
    if not isinstance(value, str) or not value.strip():
        fail(f"{where}: expected nonblank string")


def load_allowlist():
    path = pathlib.Path(__file__).with_name("source_anchor_allowlist.json")
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("source_pack_blob") != SOURCE_PACK_BLOB:
        fail("source anchor allowlist is not tied to frozen source pack")
    anchors = obj.get("assets")
    if not isinstance(anchors, dict) or set(anchors) != set(ASSETS):
        fail("invalid source anchor allowlist")
    if {a: len(anchors[a]) for a in ASSETS} != {
        "FFmpeg": 14, "pandas": 21, "MinIO": 18, "LibreOffice": 23
    }:
        fail("source anchor allowlist count mismatch")
    return anchors


def validate(doc, anchors):
    exact_fields(doc, ROOT_FIELDS, "root")
    if doc["schema_version"] != "se10-gold-v1":
        fail("invalid schema_version")
    if doc["source_pack_blob"] != SOURCE_PACK_BLOB:
        fail("source_pack_blob mismatch")
    if doc["model_generated_gold"] is not False:
        fail("model_generated_gold must be false")
    if doc["predictor_gold_visibility"] is not False:
        fail("predictor_gold_visibility must be false")
    nonblank(doc["human_author_declaration"], "human_author_declaration")
    caps = doc["capabilities"]
    if not isinstance(caps, list):
        fail("capabilities must be list")

    ids, seen = [], set()
    counts = {a: 0 for a in ASSETS}
    ambiguity_count = 0
    for idx, cap in enumerate(caps):
        where = f"capabilities[{idx}]"
        exact_fields(cap, CAP_FIELDS, where)
        cid, asset = cap["id"], cap["asset"]
        if not isinstance(cid, str) or not ID_RE.fullmatch(cid):
            fail(f"{where}.id: must be opaque G0001-style ID")
        if cid in seen:
            fail(f"duplicate ID: {cid}")
        seen.add(cid)
        if asset not in counts:
            fail(f"{cid}: unknown asset")
        for key in ("canonical_identity", "purpose"):
            nonblank(cap[key], f"{cid}.{key}")
        for key in ARRAY_FIELDS:
            if not isinstance(cap[key], list):
                fail(f"{cid}.{key}: must be list")
            for val in cap[key]:
                nonblank(val, f"{cid}.{key}[]")
        group = cap["binding_equivalence_group"]
        if group is not None:
            nonblank(group, f"{cid}.binding_equivalence_group")
        if not isinstance(cap["ambiguity"], bool):
            fail(f"{cid}.ambiguity: must be bool")
        src = cap["source_anchors"]
        if not isinstance(src, list) or not src:
            fail(f"{cid}.source_anchors: expected nonempty list")
        seen_anchors = set()
        for anchor in src:
            exact_fields(anchor, ANCHOR_FIELDS, f"{cid}.source_anchors[]")
            filename, blob = anchor["path"], anchor["blob"]
            nonblank(filename, f"{cid}.anchor.path")
            if not isinstance(blob, str) or not SHA1_RE.fullmatch(blob):
                fail(f"{cid}: invalid anchor blob")
            if anchors[asset].get(filename) != blob:
                fail(f"{cid}: anchor not in frozen {asset} source pack")
            if filename in seen_anchors:
                fail(f"{cid}: duplicate anchor")
            seen_anchors.add(filename)
        ambiguity_count += int(cap["ambiguity"])
        counts[asset] += 1
        ids.append(cid)

    for asset in ASSETS:
        if counts[asset] < 12:
            fail(f"{asset}: requires >=12, found {counts[asset]}")
    return ids, counts, ambiguity_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_file", type=pathlib.Path)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()
    source, output = args.gold_file.resolve(), args.out.resolve()
    if source == output:
        fail("output cannot overwrite private gold")
    if any((parent / ".git").exists() for parent in (source.parent, *source.parents)):
        fail("private gold must be stored outside any Git repository")
    if not source.is_file():
        fail("private gold file does not exist")
    raw = source.read_bytes()
    try:
        doc = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        fail(f"invalid gold JSON: {exc}")

    ids, counts, ambiguity = validate(doc, load_allowlist())
    public = {
        "schema_version": "se10-public-commitment-v1",
        "source_pack_blob": SOURCE_PACK_BLOB,
        "gold_file_sha256": hashlib.sha256(raw).hexdigest(),
        "gold_file_bytes": len(raw),
        "capability_count": len(ids),
        "asset_counts": counts,
        "opaque_reference_ids": sorted(ids),
        "ambiguity_count": ambiguity,
        "model_generated_gold": False,
        "predictor_gold_visibility": False,
        "semantic_gold_in_public_output": False
    }
    output.write_text(json.dumps(public, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PUBLIC_COMMITMENT={output}")
    print(f"COUNT={len(ids)}")
    # The hash is printed for convenience; no private semantic data is printed.
    print(f"SHA256={public['gold_file_sha256']}")


if __name__ == "__main__":
    main()
