#!/usr/bin/env python3
"""SE14 shared deterministic BM25 over two fair representations of 64 items.

Not an experiment runner: no real labels, frozen inputs, or results are shipped.
The ranking entry point refuses to produce evaluated ranks without a pre-existing
independent relevance commitment receipt. The receipt is an attestation, not a
cryptographic proof of curator independence; the reviewer must audit that.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import unicodedata

K1 = 1.2
B = 0.75
TOP_K = 5
ASSET_PREFIX = {"FFmpeg": "F", "pandas": "P", "MinIO": "M", "LibreOffice": "L"}
EXPECTED_ITEMS = frozenset(f"{prefix}{i:02d}" for prefix in ASSET_PREFIX.values() for i in range(1, 17))
EXPECTED_QUERIES = frozenset(f"Q{i:02d}" for i in range(1, 49))
QUERY_FAMILIES = {"plain": 12, "constraint": 12, "currentness": 8, "variant": 8, "negative": 8}
BASELINE_FIELDS = (
    "operation_name", "description", "input_schema", "output_schema",
    "parameter_descriptions", "categories", "tags", "keywords", "provider",
    "software", "interface", "install_identity", "version_platform_auth_runtime",
    "help_examples", "native_errors",
)
CAPABILITY_EXTRA_FIELDS = (
    "capability_identity", "semantic_goal", "variants", "constraints",
    "negative_evidence", "readiness", "currentness", "binding_equivalence", "evidence_refs",
)
SOURCE_PACK_BLOB = "4b3c9b62b1899653524f19a286924f942605210a"
CORPUS_BLOB = "348d24670c30e9d857e97b36b9d650a245896b01"
QUERY_BLOB = "176ee9e23fcfcd051443c087523fb6d2538c5d0c"
CONFIG_BLOB = "2149627397d2a48c58bc8b5fd0d8c654fdfbc977"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def fail(message):
    raise ValueError(message)


def unique_pairs(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            fail(f"duplicate JSON key: {name}")
        result[name] = value
    return result


def json_load(path):
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique_pairs,
                      parse_constant=lambda s: fail(f"non-finite JSON constant: {s}"))


def tokenize(value):
    text = unicodedata.normalize("NFKC", value).lower()
    parts = []
    current = []
    for char in text:
        if unicodedata.category(char)[0] in ("L", "N"):
            current.append(char)
        elif current:
            parts.append("".join(current))
            current = []
    if current:
        parts.append("".join(current))
    return parts


def flatten(value):
    """Serialize ordinary metadata keys and values identically for both arms."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and math.isfinite(value):
        return str(value)
    if isinstance(value, list):
        return " ".join(flatten(v) for v in value)
    if isinstance(value, dict):
        return " ".join(f"{k} {flatten(value[k])}" for k in sorted(value))
    fail(f"unserializable metadata value of type {type(value).__name__}")


def validate_frozen_lookup(lookup):
    if not isinstance(lookup, dict) or set(lookup) != {
        "schema_version", "source_pack_blob", "corpus_blob", "query_blob",
        "config_blob", "items", "queries"
    }:
        fail("frozen input lookup fields mismatched")
    if lookup["schema_version"] != "se14-frozen-input-lookup-v1":
        fail("invalid frozen input lookup version")
    if (lookup["source_pack_blob"] != SOURCE_PACK_BLOB or
            lookup["corpus_blob"] != CORPUS_BLOB or
            lookup["query_blob"] != QUERY_BLOB or
            lookup["config_blob"] != CONFIG_BLOB):
        fail("lookup is not anchored to reviewed SE14 Stage A blobs")
    if not isinstance(lookup["items"], dict) or set(lookup["items"]) != EXPECTED_ITEMS:
        fail("frozen lookup has wrong 64-entry identities")
    if not isinstance(lookup["queries"], dict) or set(lookup["queries"]) != EXPECTED_QUERIES:
        fail("frozen lookup has wrong 48-query identities")
    return lookup


def validate_index(payload, frozen_lookup):
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "source_pack_blob", "corpus_blob", "items"}:
        fail("invalid index manifest fields")
    if payload["schema_version"] != "se14-paired-index-v1":
        fail("invalid index schema_version")
    if payload["source_pack_blob"] != SOURCE_PACK_BLOB or payload["corpus_blob"] != CORPUS_BLOB:
        fail("index references wrong frozen source/corpus")
    items = payload["items"]
    if not isinstance(items, list) or len(items) != 64:
        fail("exactly 64 identical underlying entries are required")
    lookup = validate_frozen_lookup(frozen_lookup)
    ids, docs = set(), []
    for obj in items:
        if not isinstance(obj, dict) or set(obj) != {"id", "asset", "source_anchor", "registry_fields", "capability_extra"}:
            fail("item must contain exact shared-underlying fields")
        item_id, asset = obj["id"], obj["asset"]
        if not isinstance(item_id, str) or item_id not in EXPECTED_ITEMS or item_id in ids:
            fail("invalid/duplicate item id")
        if asset not in ASSET_PREFIX or not item_id.startswith(ASSET_PREFIX[asset]):
            fail("item asset/id disagreement")
        frozen = lookup["items"][item_id]
        if asset != frozen["asset"]:
            fail(f"{item_id}: asset not frozen")
        anchor = obj["source_anchor"]
        if not isinstance(anchor, dict) or set(anchor) != {"path", "blob"}:
            fail("unfrozen source anchor representation")
        if not isinstance(anchor["path"], str) or not anchor["path"]:
            fail("source anchor path missing")
        if not isinstance(anchor["blob"], str) or not re.fullmatch("[0-9a-f]{40}", anchor["blob"]):
            fail("source anchor blob malformed")
        if anchor["path"] != frozen["source_path"] or anchor["blob"] != frozen["source_blob"]:
            fail(f"{item_id}: source anchor differs from frozen Stage-A entry")
        base, extra = obj["registry_fields"], obj["capability_extra"]
        if not isinstance(base, dict) or set(base) != set(BASELINE_FIELDS):
            fail("baseline must expose every ordinary field, including explicit null for missing")
        if not isinstance(extra, dict) or set(extra) != set(CAPABILITY_EXTRA_FIELDS):
            fail("capability arm contains missing/unauthorized extra fields")
        baseline = " ".join(f"{field} {flatten(base[field])}" for field in BASELINE_FIELDS)
        capability_extra = " ".join(f"{field} {flatten(extra[field])}" for field in CAPABILITY_EXTRA_FIELDS)
        # The ordinary baseline bytes are reused verbatim, not rebuilt independently.
        capability = baseline + " " + capability_extra
        ids.add(item_id)
        docs.append((item_id, baseline, capability))
    if ids != EXPECTED_ITEMS:
        fail("64-item universe differs from frozen F/P/M/L-01..16")
    return docs


def validate_queries(payload, frozen_lookup):
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "query_blob", "queries"}:
        fail("invalid query corpus fields")
    if payload["schema_version"] != "se14-query-corpus-v1" or payload["query_blob"] != QUERY_BLOB:
        fail("wrong frozen query corpus")
    lookup = validate_frozen_lookup(frozen_lookup)
    queries = payload["queries"]
    if not isinstance(queries, list) or len(queries) != 48:
        fail("exactly 48 queries required")
    seen, families = set(), Counter()
    for q in queries:
        if not isinstance(q, dict) or set(q) != {"id", "family", "text"}:
            fail("invalid query fields")
        if not isinstance(q["id"], str) or q["id"] not in EXPECTED_QUERIES or q["id"] in seen:
            fail("missing/duplicate query ID")
        if q["family"] not in QUERY_FAMILIES:
            fail("invalid query family")
        if not isinstance(q["text"], str) or not q["text"].strip():
            fail("empty query")
        frozen = lookup["queries"][q["id"]]
        if q["text"] != frozen["text"] or q["family"] != frozen["family"]:
            fail(f"{q['id']}: query text/family differs from frozen Stage A")
        seen.add(q["id"])
        families[q["family"]] += 1
    if seen != EXPECTED_QUERIES or dict(families) != QUERY_FAMILIES:
        fail("wrong query/family distribution")
    return queries


def bm25_rank(documents, query, k=TOP_K):
    """Identical BM25-Okapi across both arms; unweighted unique query terms."""
    if not isinstance(query, str):
        fail("query must be text")
    ids = [name for name, _ in documents]
    if len(ids) != len(set(ids)):
        fail("duplicate ranking IDs")
    terms = [tokenize(text) for _, text in documents]
    lengths = [len(tokens) for tokens in terms]
    n = len(terms)
    if n == 0:
        return []
    avg_len = sum(lengths) / n
    freqs = [Counter(tokens) for tokens in terms]
    document_frequency = Counter(token for tf in freqs for token in tf)
    query_terms = sorted(set(tokenize(query)))
    scored = []
    for item_id, tf, doc_len in zip(ids, freqs, lengths):
        score = 0.0
        for term in query_terms:
            freq = tf[term]
            if not freq:
                continue
            df = document_frequency[term]
            idf = math.log1p((n - df + 0.5) / (df + 0.5))
            norm = freq + K1 * (1 - B + B * doc_len / avg_len) if avg_len else freq + K1
            score += idf * (freq * (K1 + 1)) / norm
        scored.append((item_id, score))
    return sorted(scored, key=lambda row: (-row[1], row[0]))[:k]


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paired-index", type=Path, required=True)
    parser.add_argument("--frozen-lookup", type=Path, default=Path(__file__).with_name("frozen_input_lookup.json"))
    parser.add_argument("--query-corpus", type=Path, required=True)
    parser.add_argument("--label-freeze-receipt", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    receipt = json_load(args.label_freeze_receipt)
    if not isinstance(receipt, dict) or set(receipt) != {
        "schema_version", "independent_label_sha256", "label_freeze_review_approved",
        "index_sha256", "query_sha256", "config_blob"
    } or receipt["schema_version"] != "se14-independent-label-freeze-v1":
        fail("independent label-freeze receipt is missing/invalid")
    if receipt["label_freeze_review_approved"] is not True:
        fail("independent relevance label freeze must be reviewed BEFORE rankings")
    if not isinstance(receipt["independent_label_sha256"], str) or not SHA256.fullmatch(receipt["independent_label_sha256"]):
        fail("invalid independently committed label SHA256")
    if receipt["config_blob"] != CONFIG_BLOB:
        fail("wrong frozen retrieval config blob")
    index_raw, query_raw = args.paired_index.read_bytes(), args.query_corpus.read_bytes()
    if receipt["index_sha256"] != hashlib.sha256(index_raw).hexdigest() or receipt["query_sha256"] != hashlib.sha256(query_raw).hexdigest():
        fail("index/query data do not match reviewed label-freeze receipt")
    lookup = validate_frozen_lookup(json_load(args.frozen_lookup))
    docs = validate_index(json_load(args.paired_index), lookup)
    queries = validate_queries(json_load(args.query_corpus), lookup)
    output = {"schema_version": "se14-ranked-outputs-v1", "config_blob": CONFIG_BLOB,
              "index_sha256": receipt["index_sha256"], "query_sha256": receipt["query_sha256"],
              "label_commitment": receipt["independent_label_sha256"], "rankings": []}
    for query in sorted(queries, key=lambda item: item["id"]):
        arms = {}
        for label, idx in (("REGISTRY_BASELINE", 1), ("CAPABILITY_ARM", 2)):
            arms[label] = [item_id for item_id, _ in bm25_rank([(row[0], row[idx]) for row in docs], query["text"])]
        output["rankings"].append({"id": query["id"], "family": query["family"], "arms": arms})
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"FROZEN_RANK_OUTPUT={args.out}")
    print(f"COUNT={len(output['rankings'])}")


if __name__ == "__main__":
    try:
        run_cli()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"SE14_INPUT_GATE_BLOCKED: {exc}", file=sys.stderr)
        sys.exit(2)
