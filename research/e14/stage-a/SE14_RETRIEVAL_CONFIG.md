# SE14 Stage A — Frozen Retrieval Configuration

Status: CANDIDATE_FOR_FRESH_REVIEW
Owning issue: #49
Protocol blob: 177c70ffa6c7e89da45d438738a809523e44c0d3

## Shared retrieval family

Both arms use the same deterministic BM25-Okapi implementation and the same query/index normalization. No embedding model, reranker or LLM query rewrite is used in the primary comparison.

Tokenizer:
1. Unicode NFKC;
2. lowercase;
3. split on non-letter/non-number boundaries;
4. discard empty tokens only;
5. no stemming, synonym expansion, stop-word deletion or arm-specific normalization.

BM25 parameters: `k1=1.2`, `b=0.75`.

IDF for term `t`: `ln(1 + (N - n_t + 0.5)/(n_t + 0.5))`.

Score = sum of standard BM25 term scores over the single concatenated document text. Tie-break: ascending canonical entry ID. Return top 5.

## Document construction

REGISTRY_BASELINE document = deterministic concatenation of all ordinary baseline metadata retained under the protocol fairness rule.

CAPABILITY_ARM document = the exact same baseline text plus app8-only semantic/evidence/currentness fields. Common-field ordering is identical. No arm-specific handcrafted keywords are permitted.

## Tuning

Primary configuration above is frozen with **no test-set tuning**. If a development set is later used for a secondary analysis, it must be disjoint and the same tuning budget must apply to both arms; it cannot replace this frozen primary result.

## Metrics

Compute exactly: nDCG@5, Recall@5, top-1 useful-match rate, constraint-satisfaction accuracy, version/currentness correctness, unsupported-boundary correctness and readiness misrepresentation rate, pooled and by query family.

## Current state

```text
RETRIEVER=DETERMINISTIC_BM25_OKAPI
CONFIG_FROZEN_CANDIDATE=YES
INDEX_VIEWS=NOT_BUILT
RELEVANCE_LABELS=NOT_CREATED
SEARCH_RESULTS=NOT_RUN
PRODUCT_FREEZE=NO
L2_READY=NO
```
