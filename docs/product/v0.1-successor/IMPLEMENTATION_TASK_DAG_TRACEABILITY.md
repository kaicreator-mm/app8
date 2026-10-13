# Implementation Task DAG Traceability Contract — app8 v0.1 Successor

Status: PRECOMMITTED_FORMAT / NOT_YET_POPULATED  
Authority inputs: Product Freeze + L1→L2 Adoption Matrix + L2 Architecture Evidence

This file defines the minimum provenance each future implementation Task DAG node must carry. It does **not** authorize implementation before L2.

## Required task fields

```text
TASK_ID
TITLE
DEPENDENCIES
PRODUCT_REQUIREMENT
L1_EVIDENCE
L2_DECISION
REUSED_ASSET
TEST_OR_COUNTEREXAMPLE
WRITE_SET
ACCEPTANCE_TESTS
FAILURE_HANDLING
VALIDATION_CLASS
DEFERRED_VALIDATION
RELEASE_GATE
```

## Inheritance rules

1. A Product invariant cannot disappear between PRD → L1 → L2 → Task DAG.
2. Validated L1 contracts/patterns/tests must be reused or explicitly dispositioned.
3. Fresh Review counterexamples become acceptance/negative regression tests when relevant.
4. Experimental code is not automatically production code; use the Adoption Matrix disposition.
5. A new implementation replacing validated reusable code/pattern requires rationale.
6. Human research data is not copied into production data stores merely because it supported a Product gate.
7. Task DAG generation must consume exact L2 authority and exact transfer matrix revision.
8. A deferred SE12-SE16 obligation must appear in the consuming task(s) as DEFERRED_VALIDATION and cannot disappear merely because it stopped blocking L2 entry.
9. Release-facing tasks must identify which still-unproven SPCL-003..SPCL-007 claims they are responsible for validating.

## Minimum task example

```text
TASK_ID=T-EXAMPLE
PRODUCT_REQUIREMENT=SPCL-002
L1_EVIDENCE=SE11 terminal + exact evidence artifacts
L2_DECISION=Q-L2-S02/Q-L2-S05 adopted architecture
REUSED_ASSET=research/e11/... validator pattern
TEST_OR_COUNTEREXAMPLE=exact prior false-promotion / target-applicability counterexamples
WRITE_SET=...
ACCEPTANCE_TESTS=...
FAILURE_HANDLING=...
```

## Gate before formal Task DAG creation

```text
PRODUCT_FREEZE=YES
L1_TO_L2_ADOPTION_MATRIX_CORE_COMPLETE=YES
DEFERRED_VALIDATION_ASSET_MAP_COMPLETE=YES
L2_ARCHITECTURE_EVIDENCE=COMPLETE
L1_TO_L2_TRANSFER_AUDIT=PASS
```

Only then may this precommitted format be instantiated as the formal Implementation Task DAG.
