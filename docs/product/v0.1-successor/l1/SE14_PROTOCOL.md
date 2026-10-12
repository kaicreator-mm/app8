# SE14 Protocol — Capability Search vs Tool/Registry Search

Status: DRAFT_FOR_FRESH_REVIEW
Execution: NOT_AUTHORIZED
Parent: Issue #25
Owning task: Issue #30
Product authority: main@908cee661f3747439bb0366b158903cb9b38b413

## 1. Falsifiable question

Does searching Evidence-backed Capability Metadata retrieve the right usable behavior materially better than an ordinary tool/CLI/MCP registry representation, especially when intent includes constraints, versions, readiness or unsupported boundaries?

This directly closes Fresh Review #24 P2-1.

## 2. Frozen evaluation corpus

Before execution, build a frozen index of at least 60 entries derived from the same underlying software inventory.

Create two views over the same underlying items:

- CAPABILITY view: semantic Capability metadata, variants, constraints, readiness/currentness and material negative boundaries;
- REGISTRY baseline view: conventional tool/export name, short description, provider/software name and interface type, without privileged Capability/Evidence fields.

Use the same retrieval engine family and comparable embedding/lexical configuration for both views so the comparison tests representation/value rather than a stronger search stack.

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
