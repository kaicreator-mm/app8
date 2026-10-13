# app8 Current Task DAG — v0.1 → v0.3

> Live task-status register, not a replacement for the frozen v0.1 normative design.
> Source of truth for current state: linked GitHub Issue/PR terminal and exact-SHA evidence.
> Update snapshot: 2026-10-14; main reference before this document:
> `1c220fd343faa1e6fd481dc7515a9d527c72b3c2`.
> An Issue marked CLOSED does **not** imply full Product Release Qualification.

## Task totals

| Milestone | Implementation task count | Closed | Open | Current qualification |
|---|---:|---:|---:|---|
| v0.1 technical preview | 10 | 10 | 0 | Technical-preview R2 accepted; formal release NO |
| v0.2 trusted execution | 6 | 6 | 0 | Scoped Docker isolation / real runner PASS; SE10/SE11 not measured |
| v0.3 real CPython JSON Capability pilot | 2 | 1 | 1 | Driver PR #143 awaiting exact-HEAD tests and real software Evidence |
| **All defined implementation tasks** | **18** | **17** | **1** | **17/18 (94.4%) by task count only** |

The two v0.3 Issues are #139 (code/contract complete) and #140 (real-host product slice open). Controller #138 is a dependent terminal and is **not** counted as an independent implementation task. Equivalent controller #123 and v0.1 project-level Issues are not double counted. No source-backed estimate exists for overall product commercial readiness.

## 18-task dependency register

| Milestone | Task | Issue | Status | Completion evidence |
|---|---|---|---|---|
| v0.1 | T01 schema contracts | #98 | CLOSED | Strict Capability/Evidence v1 schemas |
| v0.1 | T02 append-only Evidence | #99 | CLOSED | SQLite/content digests |
| v0.1 | T03 Readiness | #100 | CLOSED | Fail-closed reducer |
| v0.1 | T04 source discovery | #101 | CLOSED | Exact source snapshot |
| v0.1 | T05 hypothesis + test plan | #102 | CLOSED | Frozen bounded design |
| v0.1 | T06 observation adapter | #103 | CLOSED | Historical adapter; unsafe direct subprocess later disabled by v0.2 #129 |
| v0.1 | T07 projections | #104 | CLOSED | Frozen Capability → CLI/MCP/Skill/Docs/Search metadata |
| v0.1 | T08 search | #105 | CLOSED | Local BM25 retrieval |
| v0.1 | T09 preview E2E | #106 | CLOSED | CLI illustrative previews only |
| v0.1 | T10 host/preflight | #107 | CLOSED | v0.1 Windows/Ubuntu R2 verified; [terminal](../release/v0.1/TECHNICAL_PREVIEW_TERMINAL.md) |
| v0.2 | S00 retire unsafe process bypass | #129 | CLOSED | PR #130 |
| v0.2 | S01 pinned Docker policy | #124 | CLOSED | PR #127, 16/16 policy tests |
| v0.2 | S02 real host isolation | #125 | CLOSED | 11/11 Windows + 11/11 Ubuntu scoped probes |
| v0.2 | S03 authenticated Evidence | #126 | CLOSED | PRs #128/#131/#132; signed v2, replay, Readiness |
| v0.2 | S04 real Docker runner | #133 | CLOSED | PR #134, 21/21 checks per host on frozen baseline |
| v0.2 | S04R1 runner plan/adjudication integrity | #135 | CLOSED | PR #136; Windows 72/72, Ubuntu targeted 8/8 |
| v0.3 | T01 stored Capability qualification | #139 | CLOSED | PR #141; 11/11 targeted and 191 passed, 1 skipped full pytest |
| v0.3 | T02 CPython JSON real capability | #140 | **OPEN** | Protocol PR #142 merged; driver PR #143 under exact-HEAD validation |

Dependency overview:

```text
v0.1 T01–T10 (all closed)
    ↓
v0.2 S00/S01 → S02 → S03/S04 → S04R1 (all closed)
    ↓
v0.3 T01 #139 (closed)
    ↓
v0.3 T02 #140 (open; PR #143 test → pinned CPython real host → signed Evidence → qualification)
    ↓
v0.3 Controller #138 terminal (open, not a task)
```

## Current blocker: T02 #140

- PR [#143](https://github.com/kaicreator-mm/app8/pull/143) contains a fixed, operator-only CPython JSON pilot. The current PR **must be resolved from live GitHub**, not this document's snapshot.
- R1 test failure (old HEAD `0dacd591307192451b229efbb3e3341c36ea4c41`): 2 API assumption failures.
- R2 test failure (old HEAD `210fdac577009d0f0379238e4a1408bcbd55d9d6`): two additional stale caller-boolean assertions.
- R3 candidate HEAD at this snapshot: `7bb6435c2112a9980b48d909f7f3af1f0d314961`. Corrected tests now assert **actual prepared Docker policy argv**, not nonexistent request attributes.
- **R3 actual unit test results = PENDING**. Windows/Ubuntu CPython Docker pilot results = **NOT_RUN**. No signed real v0.3 Evidence or v0.3 scoped Capability Ready may be claimed yet.
- Required source gate: `python -m pytest tests/qualification -q` and `python -m pytest tests -q`, exact PR HEAD; do not treat prior failing HEAD evidence as PASS.
- Once tests PASS: run the fixed image/source inspection, approve measured source SHA/license, and perform P01 positive, N01 separately-scoped invalid-input behavior, F01 signed refutation and B01 blocked target-drift cases. See [pilot runbook](../validation/v0.3/CPYTHON_JSON_PILOT.md). Preserve exact target/config/source/attestation identities and keep keys/logs/DB off GitHub.
- If full-product empirical SE10/SE11 results have not been produced, Product Release Qualification remains **NO** even after a scoped JSON pilot succeeds.

## No duplicate local work

Do not redo LibreOffice official installation (#69), v0.1 host R2 (#95), v0.2 Docker 22 escape probes (#125) or v0.2 smoke 42 checks (#133) unless the material security/environment baseline has changed. The only current genuine local-host dependency is #140 T02's exact-HEAD tests + real software pilot.

## Issue closure versus release

```text
IMPLEMENTATION_TASKS_TOTAL=18
IMPLEMENTATION_TASKS_CLOSED=17
IMPLEMENTATION_TASKS_OPEN=1
V03_T02_REAL_PILOT=#140_OPEN
V03_CONTROLLER=#138_OPEN_NOT_COUNTED_AS_IMPLEMENTATION_TASK
OPEN_PR=#143
SE10_SE11_GENERAL_PRODUCT_EFFICACY=UNPROVEN
FORMAL_PRODUCT_RELEASE_QUALIFIED=NO
```

If future Product/SE10/SE11 release requirements are adopted, create a **new scoped Task DAG with measurable empirical gates**; do not relabel those unproven objectives as completed under the current 18-task register.
