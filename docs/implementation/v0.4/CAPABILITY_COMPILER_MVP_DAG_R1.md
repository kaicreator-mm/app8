# App8 v0.4 — Capability Compiler MVP execution DAG (R1)

> **Prospective new scope; no historical status rewrite.** Owner-directed pivot 2026-10-26; design/acceptance exact-SHA review pending. Source baseline `version/v0.4@487c5b1d142c241d10c8a96026f4e98b8c1c9cd6`. This plan is derived from [product](../../product/v0.4/CAPABILITY_COMPILER_MVP_SCOPE_R1.md) and [L2](../../architecture/v0.4/CAPABILITY_COMPILER_MVP_L2_DELTA_R1.md). Do not count new tasks inside the old 19/22 numerator/denominator.

## Native Issues and work lane dependency

```text
CC0: Product scope + small existing-contract L2 review (this PR)
 ├── CC01 #205: candidate → typed semantic Capability           [lane: agent/product]
 ├── CC02 #206: Evidence verifier and mapping; fixture tests      [lane: verification/Host]
 └── CC03 #207: CLI consumer contract and fixture tests         [lane: agent/SDK]
                 independent branches, interfaces pinned from CC0
         └─────────────┬──────────────────┘
                       ▼
 CC04 #208: selected Capability + signed real Evidence + Agent journeys,
            repeated Agent use, version regression and honest scoped terminal
                       ▼
           Product/Release qualification → version branch closure
                       ▼
          main merge/tag ONLY if independently eligible
```

CC01/CC02/CC03 build and test interfaces **in parallel** against existing schemas; they may close lane-level implementation with fixture checks but **not** claim end-to-end real Evidence or Agent invocation. CC04 first pins CC01's final Capability, then validates actual CC02 signed source/target-scoped Evidence and license/target identities, then performs CC03 real Agent CLI call and second task/session reuse. Join tuple: capability_id/revision, semantic_sha256, source SHA, target SHA, environment ID, binding ID, evidence snapshot SHA. Both demo assets require real CLI binding; the current projection verifier blocks pandas LIBRARY_API-only. This is a parallel implementation DAG with an explicit serial **real acceptance join**, not a chain of four implementation Tasks.

| Lane | GitHub | Owner capability / best execution kind | Primary output | Completion |
|---|---|---|---|---|
| CC0 contract | This Product/L2 PR | Web Product/L2 + independent family exact-SHA review | approved prospective MVP scope and actual existing schema interface | proposed, not yet frozen |
| CC01 Product compile | [#205](https://github.com/kaicreator-mm/app8/issues/205) | source/semantic agent; Python code/tests | typed candidate assembler/CLI binding and unit fixtures; actual selection at CC04 | OPEN, 0/1 |
| CC02 Real Evidence | [#206](https://github.com/kaicreator-mm/app8/issues/206) | deterministic verification agent; Host only when indispensable | Evidence mapping/verifier and unit fixtures; live signed Evidence only at CC04 | OPEN, 0/1 |
| CC03 Agent consumption | [#207](https://github.com/kaicreator-mm/app8/issues/207) | SDK/CLI agent, no new runtime | CLI consumer and persisted-use contract tests; live Agent use at CC04 | OPEN, 0/1 |
| CC04 E2E/release | [#208](https://github.com/kaicreator-mm/app8/issues/208) | integration agent + independent critic/release | 2/2 selected assets with genuine signed Evidence + two Agent session receipts each | OPEN, 0/1 |

## Reuse and block policy

- **R1 review boundaries:** CC02 independently determines `REVIEWED_COMPATIBLE` and target `SAME` from reliable project/target evidence (not a model); otherwise BLOCK. CC04 requires real Agent caller/task context and separate reuse context with zero source reread or proposal generation. No new tracing infrastructure.
- Reuse prior #166 v4 12 settled calls and #166 R24 diagnostic data as *candidate provenance*, not old pilot PASS; #150 FFmpeg004, FFmpeg005 and pandas002 real target receipts as bounded prior observations, but do not retrofit untrusted signatures to claim app8 Evidence.
- No requirement to adjudicate seven earlier H cards or pay for prospective v5 to start CC01/CC02/CC03. Human only for actual material unresolved capability support/side effects. If needed, minimum targeted owner choice, not a 7-item forced exercise.
- No new MinIO disposable S3 write or LibreOffice MSI validation in the two-asset MVP. Those remain open (historic four-asset qualification) with distinct denominator and truthful `NOT_RUN`; code PR #203 remains closed.
- Each lane does local unit/integration tests for its concern and exact-SHA independent diff review. CC04 performs critical journey regression and final packaging once. Do not over-repeat CI. Use `UNKNOWN/NOT_RUN` where Host or CI is unavailable and request one exact Host trigger *only* for the indispensable missing environment.
- Controlled release baseline: maintain version branch until scoped MVP Release Qualification. `main` current `3dcd2b36ed544204bf5854a3eadfcc517a81d4a7` unchanged by this planning PR.

## Distinct progress registers

Historical formal DAG remains **19/22 (86.4%)**, originally v0.4 T01 **1/4**; old #149/#150/#151 **OPEN** and original frozen Gold48 / hidden80 `NOT_RUN`, no PASS. New **CC-MVP 0/4** (CC01–CC04), CC0 proposed as a preliminary contract, not counted as a completed implementation. Count a task only when real deliverables, tests and independent review pass. Record completed end-to-end assets separately (currently **0/2**), actual Agent invocations (0), repeat uses (0) and scoped release status (BLOCKED/NOT_RUN).
