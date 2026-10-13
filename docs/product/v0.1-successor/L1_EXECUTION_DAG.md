# L1 Execution DAG — app8 v0.1 Successor

Status: CORE_CONVERGENCE_R2  
Phase: PRODUCT_L1_EVIDENCE  
Controller: Issue #72  
Convergence authority: Issue #80  
Formal Implementation Task DAG: NOT_YET_AUTHORIZED

This artifact defines the minimum Product/L1 path after convergence r2. Deferred studies remain linked downstream validations; they are not dropped.

## Phase boundary

```text
PRD
→ L1 core evidence (SE10 + SE11; SE09 context)
→ Final Core Product Review
→ Product Freeze
→ L1→L2 transfer
→ L2 Architecture Evidence
→ Implementation Task DAG
→ L3 implementation
→ deferred acceptance / Release Qualification
```

## Critical graph

```text
#58 human Gold
   ↓
SE10 evaluation
   ↓
SE10 terminal ───────────────────────────────┐
                                             │
#69 runtime target → #55 hidden truth        │
                         ↓                   │
                    SE11 evaluation          │
                         ↓                   │
                    SE11 terminal ───────────┤
                                             ↓
                                  Final Core Product Review
                                             ↓
                                    Product Freeze = YES
                                             ↓
                                    L1→L2 transfer audit
                                             ↓
                                    L2 Architecture Evidence
                                             ↓
                                 Implementation Task DAG
```

## Deferred validation graph

```text
SE10 + SE11 frozen subject
   ├→ SE12 → validates Q-L2-S06 projection architecture
   │      └→ SE13 → L3/Release Agent-utility acceptance
   ├→ SE14 → validates Q-L2-S09 search/retrieval behavior
   └→ SE15 → validates Q-L2-S07 binding/exportability coverage

SE16 → Product/Release adoption evidence
```

These nodes may run in parallel with L2/L3 when dependencies become available.

## Node register

| Node | Phase class | Dependency | Minimum terminal / handoff | Downstream |
|---|---|---|---|---|
| #58 / SE10 | CORE_L1 | merged SE10 tooling | sealed independent Gold + frozen prediction/evaluation terminal | Product Freeze |
| #69 | CORE_L1_ENABLER | merged target script | exact runtime identity + non-evaluative smoke | #55 / SE11 |
| #55 / SE11 | CORE_L1 | #69 target | sealed hidden truth + evaluated falsification terminal | Product Freeze |
| SE12 | L2_VALIDATION | SE10+SE11 frozen Capability/Evidence subject | one-authority/many-consumers protocol terminal | Q-L2-S06 / SE13 |
| SE13 | L3_RELEASE_VALIDATION | SE12 representative projections | paired Agent benchmark terminal | Release Qualification |
| SE14 | L2_L3_VALIDATION | real Capability subject + frozen labels/index | retrieval terminal | Q-L2-S09 + search acceptance |
| #59 / SE15 | L2_L3_VALIDATION | source sample; #69 for runtime binding | source sample / binding coverage terminal | Q-L2-S07 + coverage acceptance |
| #51 / SE16 | PRODUCT_RELEASE_VALIDATION | frozen recruitment instrument | real-user cohort terminal | adoption claim / release evidence |

## Asset preservation rule

Every completed L1 artifact must be referenced by the Adoption Matrix before new implementation work replaces it. Validated code is not automatically production code, but its contracts, tests, counterexamples and patterns are durable inputs.

## Finding classification

Only these can reopen the **core L1** path:

```text
A = EVIDENCE_VALIDITY_BLOCKER
B = EXECUTION_BLOCKER
```

```text
C = OPTIONAL_HARDENING
D = L2/L3_IMPLEMENTATION_OR_ACCEPTANCE_CONCERN
```

C/D are deferred.

## Current aggregate

```text
L1_PROTOCOLS_MERGED=7/7
CORE_L1_STUDIES_REQUIRED=SE10,SE11
CORE_L1_STUDY_GATES_PASS=0/2
DEFERRED_VALIDATION_STUDIES=SE12,SE13,SE14,SE15,SE16
PRODUCT_FREEZE=NO
L2_READY=NO
IMPLEMENTATION_TASK_DAG=NOT_AUTHORIZED
```
