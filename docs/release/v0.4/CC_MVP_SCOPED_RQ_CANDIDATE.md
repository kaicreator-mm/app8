# App8 v0.4 — CC-MVP scoped Release Qualification candidate (R0)

> **Status: RQ_CANDIDATE_ONLY / MAIN_MERGE_HOLD.** This is a source-visible reconciliation of existing real Host reports, not an independent replay of their private bytes, a Release PASS, or a rewrite of historical SE10/SE11. Scope baseline: `version/v0.4@e65e1a2c790606893475b0b345491f86105879e7`. Product contract: [CC-MVP scope](../../product/v0.4/CAPABILITY_COMPILER_MVP_SCOPE_R1.md) and [L2](../../architecture/v0.4/CAPABILITY_COMPILER_MVP_L2_DELTA_R1.md). Authority: [CC04 #208](https://github.com/kaicreator-mm/app8/issues/208); [controller #147](https://github.com/kaicreator-mm/app8/issues/147).

## What the approved Host actually reported

The operator-authorized Windows 11 / Docker Desktop Host first built and validated actual software from frozen Stage-A bytes ([PR #216 R2](https://github.com/kaicreator-mm/app8/pull/216#issuecomment-6441035683)); then validated Windows LF checkouts ([PR #217 R1](https://github.com/kaicreator-mm/app8/pull/217#issuecomment-6451231875)). At [PR #218 exact HEAD independent R1](https://github.com/kaicreator-mm/app8/pull/218#issuecomment-6453389544), two focused suites had **52 + 60 PASS, EXIT=0**; real FFmpeg/pandas local image-ID runs and *new* HMAC Evidence ledgers both obtained `SCOPED_EXPORT_READY`. Full local image IDs are `sha256:38096eccf5ca1d789fb4d62e8c8e33e969afc7963d3272862e121920e07d24e9` (original FFmpeg demo) and `sha256:92c1aa974ed0eeed9ca2b941d7329bc9c5c060eb9a358a8c2f7f4939acb556c4` (original pandas demo). Those **original demo tasks are operator-authored** and do *not* establish model-origin compilation.

[CC04 model-origin Host receipt](https://github.com/kaicreator-mm/app8/issues/208#issuecomment-6454284485) subsequently reports **two genuinely model-proposed user jobs** sourced *read-only* from the previously settled, sealed V04 P-role DeepSeek outputs. These are **distinct new Capabilities**, not relabeled demo Evidence:

| Scope | FFmpeg | pandas |
|---|---|---|
| Frozen P case | `V04-FFMPEG-004`, source `muxers.texi` | `V04-PANDAS-002`, source `merging.rst` |
| P response SHA prefix (Host-reported) | `1935555ae01f7c88…` | `09659400757b7f21…` |
| Actual model proposition | one data stream; explicit `-map` and `-f data`; no timestamps/metadata stored | duplicated join keys produce many-to-many Cartesian rows; validation checks uniqueness |
| Model limit | **P ABSTAIN on runtime support**; document-level hypothesis only | **P ABSTAIN on blind numeric/digest prediction**; doc-level task hypothesis remains |
| Executed new Capability | `cap:cc04-ffmpeg-mux-data` rev 1 | `cap:cc04-pandas-merge-m2m` rev 1 |
| New actual local image ID (Host-reported) | `sha256:1c9e656a250c3ad93cb8fa98071bbf065b9bd530c8a790f32ec3e37d21fda74e` | `sha256:7d134859d150c7b3…e4620` (**full ID only in private Host receipt**) |
| Selected CLI | `/opt/ccmvp/ffmpeg-data-job` | `/opt/ccmvp/pandas-merge-job` |
| Real positive and expected-error probes | `mux` exit 0, 12 × 1024-byte reconstructed payload; `badmap` exit 234, both SUPPORTED | `m2m` exit 0, oracle byte SHA `1510df55caaa9697ecf6d30d31209c777d94cd802527b4737a53edd61a55b42e`; `validate one_to_one` exit 2, both SUPPORTED |
| Actual signature/readiness | Fresh HMAC/Evidence, `SCOPED_EXPORT_READY` | Fresh HMAC/Evidence, `SCOPED_EXPORT_READY` |
| Real Agent first/second use | GLM + Kimi, EXIT=0 both, matching snapshot/output and observed events | GLM + Kimi, EXIT=0 both, matching snapshot/output and observed events |
| New provider calls | 0 | 0 |

**Interpretation matters:** ABSTAIN was not overwritten: source-bound model *task hypotheses* were tested against independently prepared Oracle expectations. The model did **not** predict the true numeric outputs. `SUPPORTED` applies only to exact selected tasks, pinned real binaries, fixture, command arguments, Host and signed execution scope. The original 24-case pilot is still exploratory and not a newly passed prediction benchmark.

## Source availability and reproducibility gap — material before version closure

The repository currently contains the **older demonstration** entrypoints `examples/cc-mvp/pandas/pandas-job` and `examples/cc-mvp/{ffmpeg,pandas}/Dockerfile`. They do not contain the *new* actual model-origin CLI sources `ffmpeg-data-job`, `pandas-merge-job` or the exact new Docker build recipes used in the final #208 private Host run. The Host report points to private `_tmp/i208-cc04/` and `_evidence-private/app8-i208-modelorigin/{ffmpeg,pandas}`; those directories are **not committed** and must not be assumed accessible to other builders.

This is a genuine **reproducible product delivery gap**. Keep private original paid prompts/completions, Oracle bytes, hidden fixtures, signing key, signed Evidence stores and identifiable Agent logs **outside GitHub**. The approved Host can submit one minimal source-only PR containing **only reviewed non-secret new CLI entrypoints, their Dockerfile variants and an inert public fixture generator/manifest where feasible**, with exact SHA256 and Git blob references to the real executed code. Never recreate different scripts and assert that prior Host signatures cover them. If the required fixture cannot be published, document its deterministic local generation and the original private SHA/authority; do not publish hidden truth.

A different independent reviewer then checks byte-identity between that source-only PR and the actual previously executed Host files. Reuse existing successful Host receipts; re-run a case **only if bytes or effective runtime inputs differ**, signing a new ledger for a changed image ID.

## R1 independent scoped RQ — only outstanding material checks

1. **P → CC01 typed candidate trace**: independently read the pre-existing sealed P input/output for both selected `V04-*` cases, exact request/response SHA and source/blob; establish whether `freeze_hypotheses` and **`assemble_typed_candidate`** actually participated in each successful Host job. If they did, publish the non-secret join digest. If the Host built a manual `app8-capability-v1` object directly from a P quotation, classify as `MODEL_ORIGIN_PROPOSAL_YES / CC01_COMPILER_PATH_UNPROVEN` and implement one minimal verified bridge using existing functions; do **not** synthesize a prior call or change the sealed model output.
2. **Exact executable source shipment**: verify the new actual FFmpeg/pandas CLI files and image build inputs are inspectable and reproducible at the reviewed version SHA, or **BLOCK version completion**. They must match the completed Host evidence byte-for-byte, including the selected fixture/digest.
3. **Evidence + independent tasks**: compare private HMAC-accepted per-asset `host-report.json`, `model-provenance.json`, signed source/target/fixture/plan, Evidence snapshots and the actual distinct GLM/Kimi task logs. Confirm exact join tuple: `capability_id/revision, semantic_sha256, source SHA, target SHA, environment_id, binding_id, evidence_snapshot_sha256`. A bare self-selected `session_id` proves nothing by itself. Confirm the second Agent did not reread source or call the proposal model.
4. **Scoped source/license/target decision**: independent reviewer checks upstream [FFmpeg pinned LICENSE.md](https://github.com/FFmpeg/FFmpeg/blob/f2bf7a2440d1e49023e4b3ed0e224a8806d388b8/LICENSE.md) + [LGPL text](https://github.com/FFmpeg/FFmpeg/blob/f2bf7a2440d1e49023e4b3ed0e224a8806d388b8/COPYING.LGPLv2.1) against actual binary/config, and [pandas pinned BSD-3-Clause LICENSE](https://github.com/pandas-dev/pandas/blob/82c18c170b9aea7cbb96ef54b8005bed07c94220/LICENSE) against the actual wheel/build; record permissible **local-only use** separately from external redistribution obligations. Neither old source pack omission nor operator-asserted `SAME` suffices alone.
5. **One version qualification**: run the focused version closure/compatibility tests **once** after the actual source is included and reviewed. Independent final RQ must give `READY / CONDITIONAL / BLOCKED / FAIL`, P0/P1/P2, and explicit `MAIN_INTEGRATION_AUTHORIZED=YES/NO`; a reviewer must separately decide whether an explicit model ABSTAIN still satisfies a *hypothesis-source*, not a *model runtime prediction*, MVP.

Do not create a registry, generic compiler abstraction, evaluation campaign, SDK/MCP installer, full 48 Gold or 80 hidden truth set, or rerun paid P/R/X calls. Historical original **19/22** formal DAG and SE10/SE11 `NOT_RUN` remain unchanged. CC-MVP development lanes **3/4 closed**; Host reports final **2/2 real task journeys**, but **CC04 stays OPEN pending the above reproducibility/qualification gate**. `main` remains untouched.

### 中文用户摘要

已取得两项真实模型提案对应的 FFmpeg / pandas 执行、签名证据与 GLM/Kimi 两次复用记录；不再缺 Docker/Agent 基础执行能力。剩余关键是把 **Host 实际执行过的 CLI 源码安全入库并核对字节一致性**、确认确实经过 CC01 编译路径、独立审查来源/许可与私有证据，然后一次性做 scoped RQ。文档本身**不是发布批准**。
