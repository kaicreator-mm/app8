# SE14 Protocol — Capability Search vs Tool/Registry Search

Status: DRAFT_FOR_FRESH_REVIEW
Execution: NOT_AUTHORIZED
Parent: Issue #25
Owning task: Issue #30
Product authority: main@908cee661f3747439bb0366b158903cb9b38b413

## 1. Falsifiable question

Does searching Evidence-backed Capability Metadata retrieve the right usable behavior materially better than an ordinary tool/CLI/MCP registry representation, especially when intent includes constraints, versions, readiness or unsupported boundaries?

This directly closes Fresh Review #24 P2-1.

## 2. Frozen evaluation corpus and fair registry baseline

Freeze >=60 entries from the same source-software inventory with exact software/source revisions and source/registry metadata blobs.

Both arms index **the same underlying software, functions/tools, capabilities and versions** and must use comparable retriever/ranker capacity. Neither arm may receive manual relevance labels, hidden gold answers or privileged task data.

**REGISTRY_BASELINE** receives all *normally available, non-app8-specific* registry/tool metadata, including when present:

- tool/CLI/MCP/API operation name and human-readable description;
- input/output and argument/parameter schema plus parameter descriptions;
- categories, tags and keywords;
- provider, software, interface type, install/package identity;
- documented version/platform and auth/runtime requirements;
- ordinary official help/usage examples exposed by registry entries;
- native error descriptions where included in ordinary schemas.

If a field is present in ordinary official registry/API schema/help data, do **not** strip it to weaken baseline. Missing source fields are noted in the manifest, not artificially generated to help either arm.

**CAPABILITY_ARM** receives the same baseline metadata, plus only app8-generated semantic Capability identities, evidence-backed variants, independently observed behavioral constraints, negative evidence, readiness/currentness and binding-equivalence semantics. No extra hand-edited retrieval hints, privileged labels or richer model generation solely for this arm.

Use identical retrieval family, embedding model, query processing, reranking, index parameters and tuning budgets. Tune both on a disjoint frozen development set or use shared default parameters. Fix the final test index/queries/labels before viewing either arm's results.

**Fairness audit:** Publish field-by-field presence matrix and baseline metadata provenance for every entry. Independent reviewer must validate that no conventional baseline field was omitted to create an artificial gain.

## 3. Query set

Freeze 48 natural-language queries, balanced across:

- 12 plain intent queries;
- 12 constraint-sensitive queries;
- 8 platform/version/currentness queries;
- 8 variant-selection queries;
- 8 negative-boundary/readiness queries.

Queries must not name the expected tool/provider unless the user job naturally requires a named asset.

At least half the queries must be cases where a name/description registry could plausibly retrieve a superficially relevant but semantically wrong item.

## 4. Relevance judgments

Independent adjudicators create graded relevance labels before search results are exposed:

- 3 = directly satisfies intent and material constraints;
- 2 = useful but incomplete/secondary;
- 1 = superficially related;
- 0 = irrelevant or contradicted by a material boundary.

A non-EVIDENCED/non-current item may not receive grade 3 for a query that explicitly requests validated/current behavior.

## 5. Metrics

Primary:

- nDCG@5;
- Recall@5;
- top-1 exact useful match rate.

Constraint/readiness diagnostics:

- constraint-satisfaction accuracy;
- version/currentness correctness;
- unsupported-boundary correctness;
- readiness misrepresentation rate.

Report by query family and pooled.

## 6. Frozen PASS thresholds

PASS requires all of:

- CAPABILITY nDCG@5 >= REGISTRY nDCG@5 + 0.10 absolute;
- CAPABILITY top-1 useful-match rate >= REGISTRY + 0.15 absolute;
- constraint-sensitive accuracy >= REGISTRY + 0.20 absolute;
- version/currentness correctness >= 0.90;
- unsupported-boundary correctness >= 0.90;
- readiness misrepresentation rate = 0 for explicit readiness queries;
- CAPABILITY Recall@5 is not worse than REGISTRY by > 0.03 absolute.

If CAPABILITY search only ties registry search within these margins, SPCL-005 FAILS as a differentiated Product claim.

## 7. Anti-cheating

Freeze:

- both index views;
- query set;
- relevance judgments/commitment;
- search/ranker configuration;
- thresholds;

before result inspection.

No query rewriting may use relevance labels.

## 8. Outputs

Produce:

- index manifests;
- query corpus;
- relevance ledger;
- exact retrieval configs;
- raw ranked outputs;
- metrics by family;
- counterexamples;
- terminal;
- What Was NOT Proven.

## 9. What this study cannot prove

SE14 does not prove broad market demand, Agent task success, extraction correctness or future production search architecture. It tests whether the Capability representation carries measurable retrieval value beyond a conventional registry baseline.

## 10. Protocol terminal

~~~text
SE14_PROTOCOL = READY_FOR_FRESH_REVIEW
SE14_EXECUTION = NOT_AUTHORIZED
PRODUCT_FREEZE = NO
L2_READY = NO
~~~
