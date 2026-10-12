# SE10 Protocol — Semantic Capability Extraction Quality

Status: DRAFT_FOR_FRESH_REVIEW
Execution: NOT_AUTHORIZED
Parent: Issue #25
Owning task: Issue #26
Product authority: main@908cee661f3747439bb0366b158903cb9b38b413
Pinned ADS: kaicreator-mm/ai-development-standard@7929012f36a2202dcc2edc7a414b8163adc7afbd

## 1. Falsifiable question

Can the app8 UNDERSTAND stage derive user-meaningful Capability Hypotheses from heterogeneous software knowledge with useful precision and coverage, without collapsing raw callables into capabilities or inventing unsupported semantics?

A FAIL is a Product/L1 result, not an invitation to lower thresholds after seeing outputs.

## 2. Frozen portfolio

The execution campaign must use these exact upstream source snapshots unless a pre-execution currentness amendment is independently reviewed before any prediction output exists:

| Class | Asset | Frozen source revision |
|---|---|---|
| mature CLI/application | FFmpeg/FFmpeg | f2bf7a2440d1e49023e4b3ed0e224a8806d388b8 |
| library/SDK | pandas-dev/pandas | 82c18c170b9aea7cbb96ef54b8005bed07c94220 |
| service/API | minio/minio | 7aac2a2c5b7c882e68c1ce017d8256be2feea27f |
| non-trivial application | LibreOffice/core | 016fd5d049256dc849111f60870f15201fcd1526 |

For each asset, the source pack is limited to material present at the frozen revision: README/docs/help/reference/examples/source/type/schema files selected by the frozen source-pack manifest. The manifest must be committed before Capability prediction begins.

## 3. Reference-set construction

An independent reference builder, separate from the prediction run, must create a frozen semantic Capability reference set for each asset before prediction outputs are revealed.

Reference-builder rules:

- use user-facing docs/tutorials/examples first;
- inspect source only to resolve ambiguity or binding/failure semantics;
- model user jobs, not one Capability per function/flag/endpoint;
- record each reference Capability with supporting source refs;
- record material variants, constraints, failure semantics and known alternative bindings;
- label ambiguous items separately rather than forcing a gold answer.

The reference set must contain at least 12 assessable semantic Capabilities per asset, or document why the frozen public material supports fewer. Fewer than 8 assessable Capabilities on any asset blocks that asset and requires protocol disposition before prediction.

## 4. Prediction run

The tested app8 UNDERSTAND configuration receives only the frozen source pack and the generic app8 Product instructions.

It outputs, for every proposed Capability:

- semantic name and purpose;
- user job / when-to-use;
- inputs/outputs;
- variants;
- constraints/preconditions;
- failure semantics;
- side effects;
- candidate bindings;
- provenance refs;
- confidence as non-authoritative metadata.

No reference/gold labels are available to the prediction run.

Exact model/provider/version, system prompt hash, sampling parameters and source-pack blob identities must be recorded before execution.

## 5. Adjudication

Two independent adjudication passes compare predictions with the frozen reference set. Disagreements are resolved by a third adjudicator using only frozen sources.

A predicted Capability may be:

- MATCH;
- PARTIAL_MATCH;
- HALLUCINATED;
- CALLABLE_SPAM;
- OVER_SPLIT_DUPLICATE;
- UNSUPPORTED_MERGE;
- BINDING_EQUIVALENCE_ERROR;
- FAILURE_SEMANTICS_LOSS;
- AMBIGUOUS / excluded from primary score.

PARTIAL_MATCH counts as 0.5 for precision/coverage only when the semantic user job matches but a material boundary is incomplete. Missing a material failure mode, incompatible binding or unsupported merged behavior is not a harmless partial.

## 6. Primary metrics

For each asset and pooled across assets:

- semantic precision;
- semantic reference coverage/recall;
- semantic F1;
- hallucination rate;
- callable-spam rate;
- over-splitting/duplicate-identity rate;
- unsupported-merge rate;
- binding-equivalence error rate;
- material failure-semantics preservation rate.

Mandatory #24 P2-2 coverage is explicit in the last four error families.

## 7. Frozen PASS thresholds

SE10 PASS requires all of:

- pooled semantic precision >= 0.80;
- pooled reference coverage >= 0.70;
- pooled semantic F1 >= 0.75;
- no asset precision < 0.65;
- no asset coverage < 0.55;
- hallucination rate <= 0.10;
- callable-spam rate <= 0.15;
- over-splitting/duplicate-identity rate <= 0.10;
- unsupported-merge rate <= 0.05;
- binding-equivalence error rate <= 0.10;
- material failure-semantics preservation >= 0.85;
- zero case where a materially incompatible behavior is confidently merged and then marked as an equivalent binding.

Any threshold miss is FAIL. Ambiguity exclusions must be reported and may not exceed 15% of the reference set; otherwise BLOCKED.

## 8. Anti-cheating / currentness

Before prediction:

1. freeze source-pack manifest;
2. freeze reference set;
3. freeze model/config identity;
4. freeze scorer/adjudication rules.

After prediction visibility:

- no source-pack expansion to rescue misses;
- no gold-label change without explicit erratum preserving old label and rationale;
- no threshold changes;
- no replacing a weak asset.

## 9. Evidence outputs

Execution must produce durable:

- source-pack manifest;
- reference set;
- prediction output;
- adjudication ledger;
- per-asset metrics;
- pooled metrics;
- negative/counterexamples;
- terminal PASS/FAIL/BLOCKED;
- What Was NOT Proven.

## 10. What this study cannot prove

SE10 does not prove behavioral truth, Evidence-plan quality, multi-consumer consistency, Agent utility, search advantage, non-pixel coverage, user demand, or implementation architecture. It tests only semantic Capability extraction against a frozen heterogeneous reference portfolio.

## 11. Protocol terminal

~~~text
SE10_PROTOCOL = READY_FOR_FRESH_REVIEW
SE10_EXECUTION = NOT_AUTHORIZED
PRODUCT_FREEZE = NO
L2_READY = NO
~~~
