# SE14 Stage B — Fair Paired BM25 Runner

Status: `IMPLEMENTED_TOOLING_CANDIDATE_FOR_FRESH_REVIEW`  
Owning issue: #49  
Required upstream Stage-A input freeze: PR #56 / Independent Review #57  
Stage-A PR HEAD used: `6c3ea68c8f1c50766895088dc3a2092b457bb5aa`

## Scope

This directory contains a machine-readable snapshot of exactly **64 frozen source-anchored entries** and **48 frozen natural-language query texts**, and the same deterministic BM25 ranker for both arms.

- `frozen_input_lookup.json`: derives strictly from Stage-A PR #56 source paths/blobs and query texts; MUST be refreshed/re-reviewed if #56 changes.
- `bm25_fair.py`: deterministic NFKC, lowercase, letter/digit tokenizer, BM25-Okapi `k1=1.2` / `b=0.75`, top 5, canonical ID tie-break. Only **values** of ordinary fields are used, not handcrafted arm-specific keywords.
- `test_bm25_fair.py`: synthetic structural tests only.

No graded relevance labels, ordinary baseline metadata extraction, app8 Capability metadata, real search rankings, scores, or experiment result exist in this PR.

## Fairness construction

A paired index must contain exactly 64 records with *one source anchor and one ordinary registry metadata object per item*. Both arms reuse the same ordinary metadata string **byte for byte**. The Capability arm appends only the explicit app8-only extra fields; it cannot replace the baseline text or remove baseline fields.

All **15 ordinary registry fields** are mandatory keys, with explicit `null` for genuinely missing upstream data. This is a shape check, not provenance proof: real metadata values and legitimate absence must be independently sourced and audited before the paired index is frozen.

The **9 Capability-extra fields** are the only appended fields. Neither arm gets labels, result-dependent keywords, a distinct retriever, or additional query processing.

The runner rejects changed source path/blob, item ID, query text/family, duplicate IDs, missing/extra fields, duplicate JSON keys, non-finite constants, altered frozen-source blob references, and incorrect corpus size.

## Evaluation barrier

The CLI demands an *existing independent label-freeze receipt* that identifies:

```text
schema_version=se14-independent-label-freeze-v1
independent_label_sha256=<64 lowercase hex>
label_freeze_review_approved=true
index_sha256=<exact bytes of paired-index JSON>
query_sha256=<exact bytes of query JSON>
config_blob=2149627397d2a48c58bc8b5fd0d8c654fdfbc977
```

The CLI checks the receipt and exact paired-index/query bytes before producing any ranked output. **This flag/receipt alone cannot prove independent label construction**: human independent adjudicators and reviewer must verify the freeze event, original private relevance ledger, fixed ranking inputs and temporal ordering. Never fabricate the receipt.

A label-freeze receipt is **not** provided. Without it, the CLI refuses evaluated ranking.

When all L1 gates legitimately authorize an evaluated run, use:

```bash
python research/e14/stage-b/bm25_fair.py \
  --paired-index /private/frozen-paired-index.json \
  --query-corpus /private/frozen-queries.json \
  --label-freeze-receipt /private/independently-reviewed-label-freeze.json \
  --out /private/se14-rankings.json
```

No private relevance ledger should be passed to the ranker; only an approved commitment. The CLI outputs item IDs for each query/arm, with no metric scoring or access to relevance labels.

## Tests

```bash
python -m unittest discover -s research/e14/stage-b -p 'test_*.py' -v
```

Author-side isolated Linux Python 3.13.5 previously passed **14/14** before the registry-key preservation hardening. The current candidate adds two regressions (16 total) for schema-key indexing and byte-identical baseline prefix; **the latest 16-test set has not yet been rerun in this author context**. Independent reviewer must execute the exact current files and conduct fresh adversarial attacks.

## Hard Gate

```text
STAGE_A_INPUT_REVIEW_57=REQUIRED
FROZEN_QUERY_OR_METADATA_SUBSTITUTION=FORBIDDEN
INDEPENDENT_RELEVANCE_LABELS=NOT_CREATED
EVALUATED_RANKINGS=NOT_RUN
SE14_GATE_PASS=NO
PRODUCT_FREEZE=NO
L2_READY=NO
```

## What was not proven

This code does not establish paired-index metadata accuracy, ordinary baseline fairness in the actual 64 records, relevance judgments, search quality, readiness correctness, nDCG or Agent utility. Those need separate real Stage-B/Stage-C evidence and independent review.
