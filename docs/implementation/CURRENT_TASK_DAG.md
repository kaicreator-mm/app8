# app8 Current Task DAG — v0.1 → v0.4 (engineering + empirical qualification)

> Live task-status register, not a replacement for the frozen v0.1 normative design.
> Source of truth for current state: linked GitHub Issue/PR terminal and exact-SHA evidence.
> Update snapshot: 2026-10-14; main reference before this document:
> `1c220fd343faa1e6fd481dc7515a9d527c72b3c2`.
> An Issue marked CLOSED does **not** imply full Product Release Qualification.

## Current portfolio snapshot (v0.4 active reentry after blocked terminal)

The v0.1–v0.3 **18/18 engineering tasks remain completed**. A separate empirical core-product qualification campaign has now been added; this is not retroactive incompleteness of the earlier engineering milestones.

| Scope | Defined tasks | Closed | Open | Release authority |
|---|---:|---:|---:|---|
| v0.1–v0.3 engineering | 18 | 18 | 0 | Scoped technical-preview / two-environment CPython pilot only |
| v0.4 SE10/SE11 core qualification | 4 | 1 | 3 | 1 asset-audit PASS; 2 BLOCKED studies REOPENED for true Gold/target work; aggregate pending |
| **Current defined task portfolio** | **22** | **19** | **3** | **19/22 formally complete, original BLOCKED history retained; full Release NO** |

v0.4 controller [#147](https://github.com/kaicreator-mm/app8/issues/147) is **OPEN** but not counted as a Task. Children: T01 [#148](https://github.com/kaicreator-mm/app8/issues/148) reuse audit **PASS/CLOSED**; T02 [#149](https://github.com/kaicreator-mm/app8/issues/149) **OPEN / empirical BLOCKED, reentry active**; T03 [#150](https://github.com/kaicreator-mm/app8/issues/150) **OPEN / empirical BLOCKED, reentry active**; T04 [#151](https://github.com/kaicreator-mm/app8/issues/151) **OPEN dependent terminal**. Child implementation-support Issues [#157](https://github.com/kaicreator-mm/app8/issues/157) (SE10 public source-anchor workpack, **CLOSED/PR #159 merged**) and [#158](https://github.com/kaicreator-mm/app8/issues/158) (SE11 unapproved target gap report, **CLOSED/PR #160 merged**) are **not counted twice** among four milestone Tasks. Dependency: #148 → (#149 ∥ #150) → #151. [Adopted assets and exact prerequisite blockers](../release/v0.4/SE10_SE11_REUSE_AUDIT.md).

Neither study's independent semantic Gold / hidden-truth commitment, four-asset evaluated run, nor aggregate empirical score exists in reviewed repository and reported checked private environment. [v0.4 terminal](../release/v0.4/CORE_EMPIRICAL_TERMINAL.md) records actual operator findings and fail-closed disposition. See owner #92 stage-gate waiver: it does not turn model-generated examples into independent empirical truth. **Full product Release NO; SE10/SE11 UNPROVEN; SE12–SE16 deferred.**

The 18-task register below is intentionally preserved as the completed **engineering baseline**, not rewritten into 22 unrelated implementation items.

**Active v0.4 owner-approved strategy (2026-10-14):** [V04-PO-MLA-001](../product/v0.4/MULTI_LLM_OWNER_DECISION.md) adopts **(1) independent multi-LLM adversarial review, (2) deterministic pinned-source + real-target verification, (3) minimal human final exception/sample adjudication**. [V04-MLA-1 successor contract](../product/v0.4/MULTI_LLM_SUCCESSOR_PROTOCOL.md) is **implementation candidate pending independent Fresh review / metric freeze**. For future #149/#150 runs, exhaustive independent-human semantic Gold/80-label *manual authorship* is **not the default requirement**; LLM output is only a candidate, real behavior is observed by tools, human confirms 4–8 audit/exception cards by default (hard maximum 12, overbudget BLOCKED). The historical original SE10/SE11 frozen protocols and [historical BLOCKED terminal](../release/v0.4/CORE_EMPIRICAL_TERMINAL.md) stay unchanged, not passed. No official successor scoring or Release PASS is authorized before frozen contract/valid real observations.


**Historical terminal immutability:** [v0.4 2026-10-14 BLOCKED report](../release/v0.4/CORE_EMPIRICAL_TERMINAL.md) remains a truthful outcome *at that date*. Reopening #149/#150/#151 upon owner instruction does not relabel its missing data as PASS; it resumes only the unmet evidence work. **PR #159 / #160 are MERGED**. [#159 exact-head Windows terminal](https://github.com/kaicreator-mm/app8/pull/159#issuecomment-6156122089): 5/5 targeted, 212 pass + 1 skip full. [#160 R2 exact-head Windows terminal](https://github.com/kaicreator-mm/app8/pull/160#issuecomment-6156421474): 6/6 targeted, 213 pass + 1 skip full. New [#149 sealed-store structural report](https://github.com/kaicreator-mm/app8/issues/149#issuecomment-6160398313) and [#150 structural report](https://github.com/kaicreator-mm/app8/issues/150#issuecomment-6160398688) additionally executed: public preflight 7/7, Stage-B validators 35 PASS; **both public metadata preflights correctly return BLOCKED**. These are tooling tests, not independent true Gold or evaluated SE10/SE11 metrics.


## Task totals

| Milestone | Implementation task count | Closed | Open | Current qualification |
|---|---:|---:|---:|---|
| v0.1 technical preview | 10 | 10 | 0 | Technical-preview R2 accepted; formal release NO |
| v0.2 trusted execution | 6 | 6 | 0 | Scoped Docker isolation / real runner PASS; SE10/SE11 not measured |
| v0.3 real CPython JSON Capability pilot | 2 | 2 | 0 | Windows Docker Desktop R3 + Ubuntu WSL2 native Docker R4 real signed Evidence scoped PASS |
| **All defined implementation tasks** | **18** | **18** | **0** | **18/18 (100%) by defined task count, not by release readiness** |

The two v0.3 Issues are #139 (code/contract complete) and #140 (scoped real-host product slice accepted). Controller #138 is a dependent terminal and is **not** counted as an independent implementation task. Equivalent controller #123 and v0.1 project-level Issues are not double counted. No source-backed estimate exists for overall product commercial readiness.

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
| v0.3 | T02 CPython JSON real capability | #140 | CLOSED | PR #143 merged; Windows R3 and Ubuntu WSL2 R4 signed P01/N01/F01/B01 real pilot PASS |

Dependency overview:

```text
v0.1 T01–T10 (all closed)
    ↓
v0.2 S00/S01 → S02 → S03/S04 → S04R1 (all closed)
    ↓
v0.3 T01 #139 (closed)
    ↓
v0.3 T02 #140 (closed; Windows R3 and Ubuntu WSL2 R4 scoped signed Evidence qualification PASS)
    ↓
v0.3 Controller #138 terminal (closed, not a task)
```

## Final v0.3 T02 #140 verification

- PR [#143](https://github.com/kaicreator-mm/app8/pull/143) is **MERGED** at `f4c1692c73aac76ec127e45f5fc8d48d68bbd2e6` after Windows exact-HEAD source and real Docker pilot PASS. [Real-host terminal](../release/v0.3/REAL_CPYTHON_PILOT_TERMINAL.md).
- R1 test failure (old HEAD `0dacd591307192451b229efbb3e3341c36ea4c41`): 2 API assumption failures.
- R2 test failure (old HEAD `210fdac577009d0f0379238e4a1408bcbd55d9d6`): two additional stale caller-boolean assertions.
- R3 tested HEAD: `7bb6435c2112a9980b48d909f7f3af1f0d314961`, tree `d8ed1a6890bb4d2cd75c346c86f50355826dd2fc`. Actual Docker policy-argv assertions passed.
- **Windows R3: 20/20 qualification PASS, 200 PASS + 1 SKIP full pytest; real P01/N01 SUPPORTED scoped, F01 signed REFUTED, B01 BLOCKED_PRE_SPAWN.** Three signed immutable Evidence rows accepted in a private SQLite store. Ubuntu R4 **20/20 qualification PASS**, source SHA matched Windows, P01/N01 scoped SUPPORTED, F01 signed REFUTED, B01 blocked before spawn.
- Windows exact-HEAD source gate completed (20/20 and 200 PASS, 1 SKIP). Ubuntu R4 exact-main incremental pilot completed (20/20 qualification PASS); full pytest was deliberately not repeated. Prior R1/R2 failures are not release baselines.
- Ubuntu WSL2 used its **own** Docker client/daemon/environment and private key/nonce ledger, independently measured exact source hash `d5d41e2c29049515d295d81a6d40b4890fbec8d8482cfb401630f8ef2f77e4d5` and image SHA, then executed P01/N01/F01/B01. Evidence and projection hashes are in [R4 source terminal](https://github.com/kaicreator-mm/app8/issues/140#issuecomment-6154181907). WSL2 is **not** an independent physical host.
- If full-product empirical SE10/SE11 results have not been produced, Product Release Qualification remains **NO** even after a scoped JSON pilot succeeds.

## No duplicate local work

Do not redo LibreOffice official installation (#69), v0.1 host R2 (#95), v0.2 Docker 22 escape probes (#125) or v0.2 smoke 42 checks (#133) unless the material security/environment baseline has changed. No remaining local-host task is required for the defined v0.1–v0.3 engineering scope. Independent physical-host or broader product efficacy testing is future, separately scoped work.

## Issue closure versus release

```text
IMPLEMENTATION_TASKS_TOTAL=18
IMPLEMENTATION_TASKS_CLOSED=18
IMPLEMENTATION_TASKS_OPEN=0
V03_T02_REAL_PILOT=#140_CLOSED_SCOPED_REAL_PILOT
V03_CONTROLLER=#138_CLOSED_NOT_COUNTED_AS_IMPLEMENTATION_TASK
OPEN_PR=NONE
SE10_SE11_GENERAL_PRODUCT_EFFICACY=UNPROVEN
FORMAL_PRODUCT_RELEASE_QUALIFIED=NO
```

If future Product/SE10/SE11 release requirements are adopted, create a **new scoped Task DAG with measurable empirical gates**; do not relabel those unproven objectives as completed under the current 18-task register.
