# L1 → L2 Adoption Matrix — app8 v0.1 Successor

Status: TEMPLATE_FROZEN_DURING_L1 / POPULATE_AT_TRANSFER  
Phase: PRODUCT_L1_EVIDENCE  
Controller: Issue #72

## Purpose

Ensure validated L1 assets are not discarded or re-designed from zero after Product Freeze.

Every load-bearing L1 artifact must receive one transfer disposition before L2 architecture work begins.

## Allowed dispositions

```text
ADOPT_AS_CONTRACT
ADOPT_AS_TEST
REUSE_CODE
REIMPLEMENT_FROM_VALIDATED_PATTERN
REFERENCE_ONLY
DROP
```

A `DROP` disposition requires an explicit reason and may not silently discard a Product/L1 invariant or counterexample.

## Required fields

| Field | Meaning |
|---|---|
| L1_ASSET | Exact file / Issue / PR / blob / evidence terminal |
| PRODUCT_REQUIREMENT | PRD/SPCL/Product invariant it supports |
| EVIDENCE_STATUS | PASS / FAIL / BLOCKED / retained research |
| ADOPTION_DISPOSITION | One allowed disposition |
| L2_TARGET | Architecture question / contract / module |
| REUSE_SCOPE | Exact file/code/test/pattern to carry forward |
| NEGATIVE_EVIDENCE | Counterexamples/failure modes that must remain testable |
| TASK_DAG_TRACE | Future task IDs that consume this asset |
| DROP_REASON | Required only for DROP |

## Initial transfer classes

| L1 asset class | Default transfer expectation |
|---|---|
| Capability semantic schema / identity rules | ADOPT_AS_CONTRACT |
| Knowledge Source / Execution Target / mapping/currentness rules | ADOPT_AS_CONTRACT |
| Evidence / provenance / refutation semantics | ADOPT_AS_CONTRACT |
| Synthetic/adversarial regression tests | ADOPT_AS_TEST |
| Validated experiment validators/runners | REUSE_CODE or REIMPLEMENT_FROM_VALIDATED_PATTERN |
| Fresh Review counterexamples | ADOPT_AS_TEST |
| Search experiment implementation | REFERENCE_ONLY unless L2 independently adopts BM25 |
| Human Gold / Hidden Truth semantic contents | REFERENCE_ONLY / evaluation asset; not production data |
| Human-curator / recruitment operational records | REFERENCE_ONLY |
| One-off controller comments / temporary orchestration | DROP when superseded by durable authority |

## Transfer rule

Before L2 Architecture Evidence starts:

```text
ALL_LOAD_BEARING_L1_ASSETS_DISPOSITIONED=YES
UNEXPLAINED_DROP_COUNT=0
COUNTEREXAMPLES_TRANSFERRED_TO_TEST_REQUIREMENTS=YES
CONTRACT_CANDIDATES_MAPPED_TO_L2_QUESTIONS=YES
```

## Task DAG traceability rule

Every formal Implementation Task DAG node must include:

```text
PRODUCT_REQUIREMENT=<PRD/SPCL>
L1_EVIDENCE=<exact terminal/artifact>
L2_DECISION=<architecture authority>
REUSED_ASSET=<file/blob/module/pattern or NONE_WITH_REASON>
TEST_OR_COUNTEREXAMPLE=<exact inherited test/evidence or NONE_WITH_REASON>
```

A task that changes an L1-derived contract must point to the authority allowing that change.

## Reuse-first rule

For each adopted implementation concern, evaluate in this order:

```text
1. REUSE_CODE
2. REIMPLEMENT_FROM_VALIDATED_PATTERN
3. NEW_IMPLEMENTATION
```

`NEW_IMPLEMENTATION` requires a short explanation of why validated L1 code/pattern is unsuitable.

## Expected examples from current L1

These are transfer candidates, not premature L2 decisions:

- Capability identity / anti-over-splitting semantics → Capability IR contract.
- Knowledge Source vs Execution Target → provenance/currentness contracts.
- Source→Execution relation/applicability guards → target resolver/evidence evaluator contracts.
- Gold/Hidden commitment strict-JSON and exact-binding counterexamples → validation/regression suites.
- SE11 evidence/refutation structure → Evidence Package / falsification interfaces.
- SE14 frozen fairness and baseline-prefix tests → search evaluation tests; BM25 itself remains an L2 choice.
- SE15 non-pixel boundary and structured semantic UI findings → binding architecture constraints.
- SE16 anti-adaptive sampling controls → Product evidence methodology; generally not production runtime code.

## Terminal

```text
CURRENT_L1_TRANSFER_TEMPLATE=FROZEN
MATRIX_FULLY_POPULATED=NO
POPULATE_WHEN=AFTER_SE10_TO_SE16_TERMINALS_BEFORE_L2
FORMAL_TASK_DAG_TRACEABILITY_CONTRACT=DEFINED
PRODUCT_FREEZE=NO
L2_READY=NO
```
