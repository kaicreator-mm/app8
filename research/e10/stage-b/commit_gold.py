#!/usr/bin/env python3
"""SE10: structurally validate PRIVATE human gold, emit only a public commitment."""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
SOURCE_PACK_BLOB = "4b3c9b62b1899653524f19a286924f942605210a"
ALLOWLIST_GIT_BLOB = "5be0ed7674fcdfd7361a57fd4f29a6f9655c1df1"
INDEPENDENCE_DECLARATION = "INDEPENDENT_HUMANS_NO_MODEL_GOLD_NO_PREDICTOR_ACCESS"
AUTHOR_CLASS = "INDEPENDENT_HUMAN_DOMAIN_CURATOR"
REVIEWER_CLASS = "INDEPENDENT_HUMAN_GOLD_REVIEWER"
PRIVATE_STORE_CLASS = "SEALED_ACCESS_CONTROLLED_OUTSIDE_DISCOVERABLE_GIT"
ID_RE = re.compile(r"G[0-9]{4,6}\Z")
SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
ROOT_FIELDS = {
    "schema_version", "source_pack_blob", "model_generated_gold",
    "predictor_gold_visibility", "human_author_declaration",
    "human_author_identity_class", "human_reviewer_identity_class",
    "independence_declaration", "isolation_statement",
    "adjudication_procedure_sha256", "adjudication_code_sha256",
    "private_store_class", "private_store_independent_reviewed",
    "capabilities"
}
CAP_FIELDS = {
    "id", "asset", "canonical_identity", "purpose", "source_anchors",
    "variants", "constraints", "negative_boundaries", "failure_semantics",
    "binding_equivalence_group", "duplicate_identity_disposition", "ambiguity"
}
ANCHOR_FIELDS = {"path", "blob"}
IDENTITY_DISPOSITIONS = {"UNIQUE", "EQUIVALENT_GROUP_MEMBER", "AMBIGUOUS_POSSIBLE_DUPLICATE"}
ARRAY_FIELDS = ("variants", "constraints", "negative_boundaries", "failure_semantics")


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
        fail(f"{where}: expected nonblank string")


def git_blob_sha1(raw):
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def load_allowlist():
    path = pathlib.Path(__file__).with_name("source_anchor_allowlist.json")
    raw = path.read_bytes()
    if git_blob_sha1(raw) != ALLOWLIST_GIT_BLOB:
        fail("source anchor allowlist bytes do not match reviewed Git blob")
    try:
        obj = strict_json_loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        fail(f"invalid source anchor allowlist JSON: {exc}")
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
    if doc["human_author_declaration"] != "I attest that this semantic Gold was authored by an independent human without model-generated Gold.":
        fail("human_author_declaration must use the frozen attestation text")
    if doc["human_author_identity_class"] != AUTHOR_CLASS:
        fail("human_author_identity_class mismatch")
    if doc["human_reviewer_identity_class"] != REVIEWER_CLASS:
        fail("human_reviewer_identity_class mismatch")
    if doc["independence_declaration"] != INDEPENDENCE_DECLARATION:
        fail("independence_declaration mismatch")
    nonblank(doc["isolation_statement"], "isolation_statement")
    for key in ("adjudication_procedure_sha256", "adjudication_code_sha256"):
        value = doc[key]
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            fail(f"{key}: expected lowercase SHA-256")
    if doc["private_store_class"] != PRIVATE_STORE_CLASS:
        fail("private_store_class mismatch")
    if doc["private_store_independent_reviewed"] is not True:
        fail("private_store_independent_reviewed must be true")
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
        disposition = cap["duplicate_identity_disposition"]
        if disposition not in IDENTITY_DISPOSITIONS:
            fail(f"{cid}.duplicate_identity_disposition invalid")
        if disposition == "UNIQUE" and group is not None:
            fail(f"{cid}: UNIQUE cannot declare binding equivalence group")
        if disposition == "EQUIVALENT_GROUP_MEMBER" and group is None:
            fail(f"{cid}: EQUIVALENT_GROUP_MEMBER requires binding equivalence group")
        if disposition == "AMBIGUOUS_POSSIBLE_DUPLICATE" and cap["ambiguity"] is not True:
            fail(f"{cid}: ambiguous duplicate disposition requires ambiguity=true")
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
    if output.exists():
        try:
            if source.samefile(output):
                fail("output cannot alias the private gold inode/file identity")
        except OSError as exc:
            fail(f"cannot verify source/output file identity: {exc}")
    if any((parent / ".git").exists() for parent in (source.parent, *source.parents)):
        fail("private gold must be stored outside any discoverable Git repository")
    try:
        git_probe = subprocess.run(
            ["git", "-C", str(source.parent), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False, timeout=10
        )
    except (OSError, subprocess.SubprocessError) as exc:
        fail(f"cannot perform Git worktree membership check: {exc}")
    if git_probe.returncode == 0:
        fail("private gold is inside a Git-discoverable worktree")
    if not source.is_file():
        fail("private gold file does not exist")
    raw = source.read_bytes()
    try:
        doc = strict_json_loads(raw)
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
        "human_author_identity_class": AUTHOR_CLASS,
        "human_reviewer_identity_class": REVIEWER_CLASS,
        "independence_declaration": INDEPENDENCE_DECLARATION,
        "isolation_statement": doc["isolation_statement"],
        "adjudication_procedure_sha256": doc["adjudication_procedure_sha256"],
        "adjudication_code_sha256": doc["adjudication_code_sha256"],
        "private_store_class": PRIVATE_STORE_CLASS,
        "private_store_independent_reviewed": True,
        "allowlist_git_blob": ALLOWLIST_GIT_BLOB,
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
