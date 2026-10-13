# L1 → L2 Adoption Matrix — app8 v0.1 Successor

Status: OWNER_R3_TRANSFER_READY_WITH_EVIDENCE_RISK  
Phase: CORE_L1_CONVERGENCE  
Controller: Issue #72  
Convergence authority: Issues #80 and #92

## Current r3 reuse disposition

The SE10/SE11 original human Gold and hidden-truth studies are now optional/deferred empirical acceptance assets; they are not marked PASS. The exact Stage B/C tools, source pack, negative regressions and execution-target provenance remain first-class L2/L3 contract/test references. The model-authored design seeds in `research/design-seeds/core_capability_scenarios_v1.json` are `REFERENCE_ONLY / ILLUSTRATIVE_UNVERIFIED`, not Gold or observed Evidence. L2 may begin under owner waiver as soon as this inventory and the architecture kickoff are in place.

## Purpose

Ensure the substantial Product/L1 investment is consumed downstream instead of being discarded or rebuilt from zero.

The matrix is now populated progressively. L2 may start after core Product Freeze once core assets and deferred-study assets have explicit dispositions; deferred study terminals are not required first.

## Allowed dispositions

```text
ADOPT_AS_CONTRACT
ADOPT_AS_TEST
REUSE_CODE
REIMPLEMENT_FROM_VALIDATED_PATTERN
REFERENCE_ONLY
DROP
```

A `DROP` requires explicit reason and may not silently discard a Product invariant, counterexample, or reusable validated asset.

## Required fields

| Field | Meaning |
|---|---|
| L1_ASSET | Exact file / Issue / PR / blob / evidence terminal |
| PRODUCT_REQUIREMENT | PRD/SPCL/Product invariant |
| EVIDENCE_STATUS | PASS / FAIL / BLOCKED / retained research / deferred |
| ADOPTION_DISPOSITION | allowed disposition |
| L2_L3_RELEASE_TARGET | architecture / implementation / release target |
| REUSE_SCOPE | exact code/test/contract/pattern |
| NEGATIVE_EVIDENCE | inherited counterexamples/failure modes |
| TASK_DAG_TRACE | future task(s) consuming the asset |
| DROP_REASON | required only for DROP |

## Current transfer inventory

| L1 asset / study | Status | Default disposition | Downstream target | Preserve |
|---|---|---|---|---|
| SE10 source pack + Gold tooling (#60) | tooling retained; real empirical terminal deferred | ADOPT_AS_TEST + REIMPLEMENT_FROM_VALIDATED_PATTERN | Capability extraction/IR validation | exact source anchors, strict JSON, isolation, anti-over-splitting tests |
| SE11 Stage-A evidence + hidden tooling (#62) | tooling retained; real empirical terminal deferred | ADOPT_AS_CONTRACT + ADOPT_AS_TEST | Q-L2-S02/S05 Evidence store + execution harness | source→target mapping, hidden-truth binding, refutation/currentness counterexamples |
| #69 LibreOffice runtime freeze tooling | active real-host evidence | REIMPLEMENT_FROM_VALIDATED_PATTERN + ADOPT_AS_TEST | Q-L2-S05 deterministic execution harness | exact package identity, dependency freeze, smoke/evidence manifest patterns |
| SE12 protocol | DEFERRED_TO_L2 | ADOPT_AS_TEST | Q-L2-S06 projection/export architecture | single-authority consistency matrix and unsupported-projection semantics |
| SE13 protocol | DEFERRED_TO_L3_RELEASE | ADOPT_AS_TEST | Agent integration / Release Qualification | paired benchmark design, budgets, scorers, trial seeds |
| SE14 Stage-A corpus/query + Stage-B BM25 runner (#70) | tooling PASS; result deferred | REUSE_CODE for benchmark harness or REIMPLEMENT_FROM_VALIDATED_PATTERN | Q-L2-S09 search/index + retrieval acceptance | 64-item freeze, 48 queries, fairness matrix, label barrier, deterministic ranker tests |
| SE15 source/binding protocol + Notepad boundary | result deferred | ADOPT_AS_CONTRACT + ADOPT_AS_TEST | Q-L2-S07 binding architecture | pixel prohibition, structured-semantic boundary, top-capability freeze method, applicability rules |
| SE16 recruitment instrument (#52) | reviewed instrument; cohort deferred | REFERENCE_ONLY + ADOPT_AS_TEST for Product validation | Product/Release adoption gate | anti-adaptive sampling, dedup, fixed cohort, evidence schema |
| Model-authored 16-case seed pack (r3) | ILLUSTRATIVE_UNVERIFIED | REFERENCE_ONLY + ADOPT_AS_TEST for contract examples | Q-L2-S01/S02/S04/S05 | scenario structure + positive/negative/boundary hypotheses; never Gold |
| Fresh Review counterexamples across L1 | retained | ADOPT_AS_TEST | matching L2/L3 module | every valid A/B counterexample |
| Controller-only superseded orchestration | superseded | DROP | none | DROP only when durable authority contains same rule |

## Reuse-first rule

For each implementation concern:

```text
1. REUSE_CODE
2. REIMPLEMENT_FROM_VALIDATED_PATTERN
3. NEW_IMPLEMENTATION
```

`NEW_IMPLEMENTATION` requires an explicit rejection reason for the existing validated asset/pattern.

## Deferred-study rule

Deferral changes **when** a study blocks, not whether its useful work survives.

```text
SE12 -> L2 architecture validation
SE13 -> L3 / Release Qualification
SE14 -> L2/L3 search validation
SE15 -> L2/L3 binding validation
SE16 -> Product/Release adoption validation
```

Task DAG nodes touching those domains must cite the corresponding retained protocol/tooling/counterexamples even if the final study result has not yet run.

## Core transfer rule

Before L2 Architecture begins:

```text
CORE_LOAD_BEARING_L1_ASSETS_DISPOSITIONED=YES
DEFERRED_STUDY_ASSETS_MAPPED=YES
UNEXPLAINED_DROP_COUNT=0
CORE_COUNTEREXAMPLES_TRANSFERRED=YES
CORE_CONTRACT_CANDIDATES_MAPPED_TO_L2=YES
```

The matrix continues to accumulate exact terminal SHAs/blobs as SE10/SE11 and deferred studies finish.

## Task DAG traceability rule

Every formal Implementation Task DAG node must include:

```text
PRODUCT_REQUIREMENT=<PRD/SPCL>
L1_EVIDENCE=<exact terminal/artifact or DEFERRED_VALIDATION_REFERENCE>
L2_DECISION=<architecture authority>
REUSED_ASSET=<file/blob/module/pattern or NONE_WITH_REASON>
TEST_OR_COUNTEREXAMPLE=<exact inherited test/evidence or NONE_WITH_REASON>
```

## Terminal

```text
CURRENT_L1_TRANSFER_MATRIX=ACTIVE_R2
CORE_MATRIX_COMPLETE=YES_FOR_OWNER_R3_SCOPE_TRANSFER
DEFERRED_ASSET_MAP_COMPLETE=YES
FORMAL_TASK_DAG_TRACEABILITY_CONTRACT=DEFINED
PRODUCT_SCOPE_FREEZE=YES_OWNER_APPROVED
EVIDENCE_QUALIFIED_FREEZE=NO
L2_READY=YES_WITH_OWNER_WAIVER
```
