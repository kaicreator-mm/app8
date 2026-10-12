# L1 Execution DAG — app8 v0.1 Successor

Status: ACTIVE_CONVERGENCE  
Phase: PRODUCT_L1_EVIDENCE  
Controller: Issue #72  
Formal Implementation Task DAG: NOT_YET_AUTHORIZED

This artifact makes the existing Product/L1 execution graph explicit. It is **not** the implementation Task DAG.

## Phase boundary

```text
CURRENT:
PRD
→ L1 Evidence protocols
→ L1 Execution DAG
→ study execution / terminals
→ Final Product Review
→ Product Freeze

NEXT, only after Product Freeze:
L2 Architecture Evidence
→ L1→L2 transfer / architecture freeze
→ Implementation Task DAG
→ L3 / implementation
```

## Critical graph

```text
SE10: #61/#60 -> #58 human Gold -> SE10 evaluation -> SE10 terminal
SE11: #66/#62 + #68/#67 -> #69 target freeze -> #55 hidden truth -> SE11 terminal

SE14 preparation:
  #71/#70 -> independent labels may start early
  SE10 terminal + SE11 terminal -> evidence-backed paired index
  independent labels + exact paired index -> reviewed label receipt -> SE14 paired run -> SE14 terminal

SE15: #59 human A/B + #69 -> non-pixel binding -> SE15 terminal
SE16: #53/#52 -> fixed private cohort -> 8 real users -> SE16 terminal

SE10..SE16 terminals
        ->
Final Independent Product Review
        ->
Product Freeze = YES
        ->
L1->L2 transfer audit
        ->
L2 Architecture Evidence
        ->
Implementation Task DAG
```

## Node register

| Node | Phase class | Dependency | Minimum terminal | Downstream unlock |
|---|---|---|---|---|
| #53 / PR #52 | FRESH_REVIEW | current SE16 instrument | PASS on exact HEAD | merge #52, recruit |
| #61 / PR #60 | FRESH_REVIEW | current SE10 tooling; 17/17 regression PASS | Fresh terminal | merge #60, #58 |
| #66 / PR #62 | FRESH_REVIEW | current SE11 tooling; 18/18 regression PASS | Fresh terminal | merge #62, hidden prep |
| #68 / PR #67 | FRESH_REVIEW + LOCAL_REAL_HOST | R5 HEAD 1f9bcd1; PS5.1 real-host static PASS, match=1 | Fresh source terminal | merge #67, #69 |
| #71 / PR #70 | FRESH_REVIEW | current SE14 runner; 16/16 regression PASS | Fresh terminal | merge #70; labels may freeze early |
| SE14 paired-index freeze | PRODUCT_L1_EVIDENCE | SE10+SE11 evidence-backed Capability subject + independent ordinary-metadata audit | exact paired index + label receipt bound to its SHA | evaluated SE14 ranking |
| #58 | INDEPENDENT_HUMAN | #60 merge | sealed Gold commitment | SE10 evaluation |
| #69 | LOCAL_REAL_HOST | #67 merge | exact LO/runtime manifest + smoke | SE11/SE15 target |
| #55 | INDEPENDENT_HUMAN | #62 + #69 | sealed 80-claim truth | SE11 execution |
| #59 | 2×INDEPENDENT_HUMAN | source freeze | exact top-25 commitment | SE15 binding |
| #51 | REAL_EXTERNAL_USERS | #52 merge | fixed 8-person primary cohort evidence | SE16 terminal |
| SE12 | WEB/LOCAL protocol execution | SE10+SE11 terminal subject | protocol terminal | SE13 |
| SE13 | REAL benchmark | SE12 artifacts | paired benchmark terminal | final review |

## Finding classification

Only these remain on the Product/L1 critical path:

```text
A = EVIDENCE_VALIDITY_BLOCKER
B = EXECUTION_BLOCKER
```

The following do not reopen L1 unless an independent reviewer proves they affect the frozen study result:

```text
C = OPTIONAL_HARDENING
D = L2/L3_IMPLEMENTATION_CONCERN
```

## Stop rule

For an experiment tool:

```text
can execute frozen study
AND preserves blind/independent boundary
AND exact inputs/targets are bound
AND validity-relevant corruption fails closed
AND raw evidence/scoring inputs are preserved
=> L1_TOOLING_SUFFICIENT=YES
```

After this point, optional robustness is deferred.

### SE14 ordering clarification

Independent relevance adjudication may start once the 64-item universe and 48-query corpus are frozen and before any rankings are visible. However, the final label-freeze receipt must bind the exact real paired-index bytes. Because the Capability arm requires evidence-backed Capability/currentness/readiness fields, the real paired-index freeze is downstream of the SE10/SE11 evidence-backed subject. No synthetic or hand-invented `capability_extra` may substitute for that authority.

## Current aggregate

```text
L1_PROTOCOLS_MERGED=7/7
L1_STUDY_RESULT_GATES_PASS=0/7
PRODUCT_FREEZE=NO
L2_READY=NO
IMPLEMENTATION_TASK_DAG=NOT_AUTHORIZED
```
