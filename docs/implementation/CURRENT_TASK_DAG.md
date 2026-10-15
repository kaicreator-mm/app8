# app8 Current Task DAG — v0.1 → v0.4 (engineering + empirical qualification)

> Live task-status register, not a replacement for the frozen v0.1 normative design.
> Source of truth for current state: linked GitHub Issue/PR terminal and exact-SHA evidence.
> Update snapshot: 2026-10-15; main reference before this update:
> `de978a313f7130806679088a4f721a1badfe7d6b`.
> This is a living planning view. Actual Issue/PR and exact evidence at GitHub take precedence.
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


## Active v0.4 critical path and truthful status (2026-10-15)

**Formal Task DAG unchanged:** `#148 CLOSED → (#149 OPEN ∥ #150 OPEN) → #151 OPEN`, under controller `#147 OPEN`. These are **4** new tasks, of which **1** is closed. The other 18 engineering tasks remain CLOSED: **19/22 formally closed (86.4%)**. **Support #165 CLOSED → #166 OPEN** is a separate implementation/evidence branch under #147; it is **not** a fifth v0.4 task. Counting closed support PRs/Issues as formal task completion is prohibited.

The prior `CORE_EMPIRICAL_BLOCKED` terminal remains a dated historical result, not a permanently satisfied qualification. The original byte-frozen SE10 and SE11 studies remain `NOT_RUN`; their human-Gold and 80-hidden-truth outcomes cannot be inferred from successor multi-LLM candidates.

### Successor V04-MLA-1 admission and execution DAG

```text
Owner-approved successor methodology                      DONE (#147 decision)
    ↓
#165 typed contracts, deterministic fail-closed reducers  DONE / CLOSED
    ↓
Exact 76-source provenance + four target reentry          DONE AS CANDIDATE, NO TARGET APPROVAL
    ↓
24 prospective jobs + private seed + official compiler    DONE AS CANDIDATE
    ↓
Independent 24/24 job/intent semantic review               DONE AS CANDIDATE (#166)
    ↓
12 role instruction drafts (4 P / 4 R / 4 X)              DONE AS AUTHOR DRAFT, NOT FROZEN
    ↓
12 exact provider/request byte envelopes, R/X family
independence, cohort/job/protocol/scorer/budget pins       BLOCKED — HOST CONFIG / PRIVATE INPUTS
    ↓
Fresh independent PRE-OUTPUT provisional admission
verdict bound to exact campaign SHA256                     NOT_RUN
    ↓
Host ledger FREEZE → unique unedited GitHub public
commitment, witness verification before each dispatch     NOT_RUN
    ↓
12 trusted blind P/R/X invocations, 24 cases immutable    NOT_RUN; 0/24 evaluated
    ↓
Source-only disagreement/coverage, H sample + mandatory
exceptions; behavior requires independent target/oracle   NOT_RUN
    ↓
#149 / #150 honest empirical terminals → #151             NOT_RUN / BLOCKED
    ↓
v0.4 core qualification and Release decision              RELEASE NO
```

**Exact evidence ledger:** PR #182–#188 (including #188 [independently reviewed and merged](https://github.com/kaicreator-mm/app8/pull/188) into `de978a31`) provide bounded protocol/input/host protections, **not real provider runs**. [#166 24-case source review](https://github.com/kaicreator-mm/app8/issues/166#issuecomment-6176183752) reports **24/24 structurally correct and independently reviewed prospective jobs**, comprising 19 source-semantic and 5 behavior-candidate intents. [#166 latest private-host readiness](https://github.com/kaicreator-mm/app8/issues/166#issuecomment-6188060513) reports that its local environment could **not locate the separately delivered private 12-role author-draft JSON**; model provider/version/sampling/budget choices were not authorized, and final 12 exact outbound envelopes were therefore **BLOCKED**. The private JSON must remain outside Git; provide its existing download to the host, **not regenerate those 24 jobs or invent model profile defaults**.

**Minimal prerequisites for an honest source-semantic pilot:** same 24/24 frozen cases, all 12 final outbound request and profile digests, source excerpts bounded to the frozen anchors, different-family R/X, predeclared budget and scope, independent campaign-specific provisional reviewer verdict, live GitHub immutable public witness, then actual P/R/X execution and usage reconciliation. A source-only dry run cannot claim independent Gold, semantic precision/F1, behavior support, or promotion. The five behavior-intent cases remain in the fixed 24 denominator and **BLOCKED until exact target claim-specific applicability + independently calibrated deterministic Oracle**; LibreOffice remains `DIVERGED` and unapproved, pandas ABI import smoke is not the same as target/claim approval.

**Minimal H authority:** precommitted at least one audit card per asset plus all derived impactful unresolved cases; cap 12, excess BLOCKED. H may `CONFIRM/REJECT/DEFER` with evidence and must not silently upgrade model-derived truth. Formal original SE10 48-Gold / SE11 80-hidden results remain separate, `NOT_RUN`, and the successor 24-case calibration pilot cannot replace them or authorize production Release.

**Avoid repetition:** small code fixes → diff-only tests and independent incremental review; use one version-candidate full regression, not a fresh environmental campaign per PR. Do not repeat #150 wheel downloads/ABI smoke, 24-job semantic audit or prior Docker/LibreOffice installs absent identified evidence drift. No automatic live model call, no fake freeze comment, no opportunistic old PASS reuse.

### Blocker ownership at handoff

| Blocker | Status | Correct next owner or channel |
|---|---|---|
| Private author 12-role JSON delivery to host | FILE AVAILABLE TO USER; HOST DID NOT SEE FILE | User transfers existing private file, local Agent reads it; no Git upload |
| Frozen real provider profiles + exact P/R/X requests + token budget | BLOCKED / NOT CONFIGURED | Real host operator, with explicit model/price/permission inputs |
| Campaign-specific fresh independent provisional admission | NOT_RUN | Different-family reviewer on exact pre-output manifest |
| Pre-dispatch GitHub unedited witness proof | GRAPHQL FIELD READ-ONLY PROBE PASS; LIVE FREEZE NOT_RUN | Privileged host after admission only |
| Four approved behavior targets and independent calibrated Oracle | NOT READY; LibreOffice DIVERGED | Real host and independent claim-specific reviewer |
| Formal #149/#150 studies and #151 terminal | NOT_RUN / BLOCKED | Actual evidence first; status `BLOCKED` if infeasible, no invented PASS |

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
OPEN_PR_AT_V03_SCOPED_CLOSEOUT=NONE
SE10_SE11_GENERAL_PRODUCT_EFFICACY=UNPROVEN
FORMAL_PRODUCT_RELEASE_QUALIFIED=NO
```

If future Product/SE10/SE11 release requirements are adopted, create a **new scoped Task DAG with measurable empirical gates**; do not relabel those unproven objectives as completed under the current 18-task register.
