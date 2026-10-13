# app8 v0.4 T01 — SE10/SE11 evidence asset adoption and qualification eligibility

Status: **WEB_SOURCE_AUDIT_COMPLETE / EVALUATED_EXECUTION_NOT_AUTHORIZED_YET**  
Issue: [#148](https://github.com/kaicreator-mm/app8/issues/148), parent [#147](https://github.com/kaicreator-mm/app8/issues/147).  
Audit baseline: `main@aea267ec537a7aa6c76a7860f57b9f0787278113`.  
Read-only audit: repository source files, Git blobs, schema/test harnesses. This audit did **not** inspect any off-repository private Gold/hidden truth, inspect current real-host binaries or run any benchmark.

## Decision

**ADOPT existing SE10/SE11 artifacts; do not restart L1 research or rebuild unchanged Docker Runner.** The old study tooling and bounded source/material identity are reusable, but the frozen public/private experiment inputs and independent truth receipts required to *execute and score* are not in the GitHub tree. A tool being present is not an independent empirical result.

| Reusable asset | Exact immutable Git blob | Disposition and dependency |
|---|---|---|
| SE10 protocol | `08f9244a04275c780f778d50f638e332aa5807a2` | ADOPT reference thresholds and four-asset protocol; do not infer product PASS |
| SE10 76-file source-pack manifest | `4b3c9b62b1899653524f19a286924f942605210a` | ADOPT with exact four pinned revisions; future pack additions need pre-prediction amendment |
| SE10 source anchor allowlist | `5be0ed7674fcdfd7361a57fd4f29a6f9655c1df1` | ADOPT 76 references: FFmpeg 14, pandas 21, MinIO 18, LibreOffice 23; source paths/blobs must match |
| SE10 Stage B private Gold schema + independent attestation | `7f40ca17f32ed7a47225cf9b1f4d751f3ebc6ed3` / `987bdc9dfe3d5951bd9a73e6d3d5378da484446a` | REUSE validation/commit tooling; semantic Gold stays private outside Git; cannot be LLM-authored |
| SE10 Stage C scorer | `d443ef5e1d50c011935be682ae0513e695683990` | REUSE `research/e10/stage-c/stage_c.py` and existing synthetic scorer tests; actual four-asset predictions/adjudication absent in this tree |
| SE11 protocol | `1204c717eb590071a7b7f7e1cd3018b825ef1617` | ADOPT current bytes and four-asset, 80-claim, source→target mapping rule |
| SE11 Stage A prior host manifest | `28844d08c66766cb7442d803a8ed40893c433310` | REUSE as **historical provenance only**; exact artifact bytes must be rechecked if used |
| SE11 candidate target selection | `ee247c95eb56081e4014210f1013fb66f783345a` | CANDIDATE, not a final independent-approved `se11-execution-target-manifest-v1` |
| SE11 Stage B hidden-truth schema | `d610f5f053601abd95063123bdb3e755d5726983` | REUSE 80-claim private commitment validator; private truth/target-applicability labels not visible in Git |
| SE11 Stage C scorer | `50c9569746d5a6b9bdabfee6b9369cc1da3e3ae5` | REUSE bounded LLM-B plan scoring; actual committed hidden/plan/real execution result absent in tree |
| v0.3 real pinned JSON pilot | `docs/release/v0.3/REAL_CPYTHON_PILOT_TERMINAL.md` | SCOPED REAL EVIDENCE only, not general SE10 or SE11 empirical PASS |

Source availability check: GitHub repository tree contains Stage B **schemas/scripts**, Stage C **code/synthetic unit tests**, historical Stage A identity evidence. It contains **no identifiable frozen public SE10 Gold commitment, SE10 prediction/adjudication outcome, SE11 80-claim hidden public commitment, approved final target manifest or SE11 evaluated execution/scoring report**. Private files may exist outside GitHub; their absence from the repository does **not** prove physical nonexistence.

**Pin drift note:** SE11 Stage B README and historical Stage A metadata refer to `83abefb13e6a91e6b67a1c94937ca1bcce567aad`; current protocol Git blob is `1204c717eb590071a7b7f7e1cd3018b825ef1617`. Do not silently equate them. T03 must resolve lineage/current authority and freeze a reviewed protocol revision or explicit historical-reference overlay **before** private truth creation. Preserve previous protocol bytes; do not rewrite a historical manifest to look current.

## Frozen product study targets

| Asset | Knowledge Source revision | Candidate real target (SE11) | Currentness/eligibility |
|---|---|---|---|
| FFmpeg | `f2bf7a2440d1e49023e4b3ed0e224a8806d388b8` | Ubuntu 24.04 compatible FFmpeg binary SHA256 `fb2e2c6895f9e8a740587b0e540dfdce888387d4dc73a5e6c50d5ce8cba56023` | HISTORICAL_READY; binary/container must be re-verified, not built again automatically |
| pandas | `82c18c170b9aea7cbb96ef54b8005bed07c94220` | CPython 3.12 Linux wheel SHA256 `e57b0784bf6fe3abd3f292284c124ffc1c6367e35e5b97cc298f63d53431ce08` | HISTORICAL_READY; re-verify wheel, exact Python image and pin numpy/python-dateutil/six before execution |
| MinIO | `7aac2a2c5b7c882e68c1ce017d8256be2feea27f` | Windows minio.exe SHA256 `94d0b2677e6ed5a719fe1fc5fccbd60669beecb9901a3bb6a8bc71507bd55981` | HISTORICAL_READY; Windows-specific binary SHA must be rechecked, not run as Linux ELF |
| LibreOffice | `016fd5d049256dc849111f60870f15201fcd1526` | Official Windows LibreOffice 26.8.1.1 package; MSI SHA256 `c6298b10cfa1748bcbedad94c62ce771e240e5021bfd6d7a967cd571b04b5312` | PRIOR REAL INSTALL reported; official release→Knowledge Source **DIVERGED**. Applicability of each claim must be proven against release-specific evidence before freezing truth |

**No new Docker policy/sandbox or local software installation is authorized by this audit.** v0.2 #125/#133 host baselines and v0.3 signed CPython are retained as already demonstrated engineering scopes, not reused as real SE11 per-claim truth.

## Frozen metric and authority gates

**SE10, SPCL-001:**
- Four assets; each normally ≥12 assessable semantic references, if fewer than 8 then BLOCKED, model prediction blind to Gold; Stage B validates independently authored/reviewed private reference before Stage C.
- Pooled precision ≥0.80, coverage ≥0.70, F1 ≥0.75; no asset precision below 0.65/coverage below 0.55; hallucination ≤0.10, callable spam ≤0.15, over-split ≤0.10, unsupported merge ≤0.05, binding error ≤0.10, failure semantics preservation ≥0.85, ambiguity exclusions ≤0.15; zero materially incompatible confident merge.
- Real prediction provider/model, prompt/config/source pack, adjudication receipts frozen **before** scoring. No weak-asset swap and no threshold tuning after outcomes.

**SE11, SPCL-002:**
- Exactly 80 claims, 20 per asset: 8 TRUE, 4 MATERIALLY_FALSE, 4 OVERBROAD, 4 NEAR_MISS; freeze independent hidden truth/decisive fixtures/target applicability before LLM-B planning.
- False promotion ≤0.05, supported false rejection ≤0.15, refutation ≥0.90, narrowing ≥0.80, boundary detection ≥0.75, constraint discovery ≥0.80, reproducible decisive evidence ≥0.90, environmental BLOCKED ≤0.15; zero model-prose-only promotion.
- Actual executing target bytes, source→target mapping and private independent truth are separate from model-planned/expected outcomes. Model output cannot be hidden labels; a blocked execution never becomes SUPPORTED.

**Owner #92 scope:** waives independent human Product reviews *for L1→L2 scheduling*, **not** evidence independence in a study whose semantic Gold and hidden truth require it. If independent adjudication cannot be obtained, record the empirical status BLOCKED/NOT_RUN. A non-independent synthetic pilot is permitted as a development experiment but cannot receive the frozen SE10/SE11 PASS label.

## Minimal remaining Task DAG (v0.4)

```text
T01 #148 exact-byte reuse/eligibility audit — WEB (this document)
   ├─> T02 #149 SE10 independently anchored benchmark — WEB scorer/inputs, private Gold dependency
   └─> T03 #150 SE11 80-claim execution benchmark — WEB scoring, host + independent hidden truth
              T02 + T03
                └─> T04 #151 qualified core terminal and honest Release disposition
```

T02 and T03 may prepare in parallel; neither can score or claim PASS until private truth/source/target gates hold. T04 can report **BLOCKED** without inventing a release. T01 does **not** authorize either execution study, publish secrets, or request a new installer.

```text
V04_T01_SOURCE_REUSE_AUDIT=PASS_SOURCE_READ_ONLY
V04_SE10_SCORE=NOT_RUN
V04_SE11_SCORE=NOT_RUN
V04_INDEPENDENT_TRUTH_CONFIRMED=NO
V04_FINAL_RELEASE_PASS=NO
SE12_TO_SE16=UNPROVEN_DEFERRED
```

## Next safe action

T02: inspect and reuse the existing gold-commit/prediction/adjudication validators; seek only the **necessary independently authored sealed reference commitment** before a blind four-asset prediction. T03: resolve stale protocol citation, confirm a final reviewed Execution Target manifest and hidden truth isolation, then reuse the existing real-host artifacts where byte-identical. Both should **fail closed and report their exact missing prerequisites**, instead of spawning expensive repeated review/research or host loops.

