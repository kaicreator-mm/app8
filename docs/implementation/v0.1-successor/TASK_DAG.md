# app8 v0.1 Implementation Task DAG

Status: FORMAL_DAG_ADOPTED_OWNER_R3 / IMPLEMENTATION_ACTIVE  
Parent: Issue #97  
Product scope freeze: Issue #92 / PR #93 merge `5f5c68bf9695c66453b4f82927e6b4155c9db76f`  
L2 Architecture Evidence: Issue #94 / PR #96 merge `77e850e0c873c624ec9d10896358f1ca680edc0d`  
Independent-human Gold/Fresh Review gate: WAIVED_FOR_L2_L3_BY_OWNER (not PASS)  
SE10/SE11 empirical results: UNPROVEN, required before strong release claims.

## Minimum release path

```text
T01 #98 Contracts ─┬→ T02 #99 Evidence storage ───┐
                  │                                ├→ T03 #100 Readiness ────────┐
                  └→ T04 #101 Discovery → T05 #102 ├→ T06 #103 Execution ────────┤
                                                   │                               ├→ T07 #104 Projections ──┐
                                                   └───────────────────────────────┘                          │
                                                   T03 #100 → T08 #105 Search ────────────────────────────────┤
                                                                                                               ↓
                                                                                                       T09 #106 E2E CLI
                                                                                                               ↓
                                                                                                       T10 #107 Validation
```

Critical path: T01 → T04 → T05 → T06 → T07 → T09 → T10.  
Parallel starts: after T01, T02 and T04; after T03, T08 independent of T06; T07 waits both readiness and execution.

## Exact task register

| ID | Issue | Dependencies | Architecture authority | Reuse | Write set | Gate |
|---|---|---|---|---|---|---|
| T01 | #98 | none | ADR01/02 | JSON Schema v1 contracts | pyproject.toml; app8/contracts; tests/contracts | strict input validation |
| T02 | #99 | T01 | ADR02/04 | SE11 Stage A/B evidence | app8/storage; tests/storage | immutable/replayable evidence |
| T03 | #100 | T01,T02 | ADR01/07 | SE10/SE11 negative outcomes | app8/readiness; tests/readiness | no unsupported promotion |
| T04 | #101 | T01 | ADR05/08 | 76-file source pack | app8/discovery; tests/discovery | exact source + no pixel |
| T05 | #102 | T04 | ADR03 | SE10 prediction/SE11 plan tooling | app8/orchestration; tests/orchestration | bounded frozen plans |
| T06 | #103 | T02,T05 | ADR03/05 | SE11 real execution and #69 script | app8/execution; tests/execution | sandbox + observation |
| T07 | #104 | T03,T06 | ADR01/06 | SE12 projection/SE15 binding | app8/projections; tests/projections | one factual authority |
| T08 | #105 | T03 | ADR06/07 | SE14 64/48 BM25 | app8/search; tests/search | readiness/currentness |
| T09 | #106 | T07,T08 | ADR01–08 | 16 model design seeds (illustrative only) | app8/cli; tests/integration | end-to-end negative tests |
| T10 | #107 | T09 | ADR02/03/07 | #69 runtime; SE10/11 reusable studies | tests/real_host; docs/release/v0.1 | real host, replay, release decision |

## Rules

- One concern, one PR; scoped CI/test then merge main, do not wait for entire version batch.
- Product core defaults to Python, SQLite and local content-addressed artifacts; optional Postgres/S3/other providers are later adapters.
- A model can design tests, hypotheses and examples but cannot self-create **real behavioral Evidence** or claim an independent benchmark PASS.
- Preserved experimental tools are source/test assets, not automatically production code. Cite exact reuse/reimplementation decisions.
- All PRs must include: Product Requirement, L1 evidence status, L2 decision, reused asset, negative test, write set, and failure handling.
- T06 and T10 may need genuine Build Host; ask user for one exact pinned prompt only when indispensable.
- MVP UI is not mandatory; use CLI first to avoid UI-driven delays.
- Strong release claims require scoped real-target execution; if unavailable, release qualification remains BLOCKED or technical preview with explicit unproven limitations.
- `REFUTED/BLOCKED/STALE` cannot become `EXPORT_READY`; model prose never substitutes for execution.

## Progress

```text
FORMAL_IMPLEMENTATION_TASKS=10
IMPLEMENTATION_TASKS_COMPLETED=0
READY=T01
BLOCKED_BY_DAG=T02,T03,T04,T05,T06,T07,T08,T09,T10
REAL_HOST_REQUIRED_LATER=T06,T10
PRODUCT_SCOPE_FREEZE=YES_OWNER_APPROVED
L2_ARCHITECTURE_DESIGN=ADOPTED
RELEASE_READY=NO
```
