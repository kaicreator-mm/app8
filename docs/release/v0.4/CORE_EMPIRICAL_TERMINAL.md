# app8 v0.4 — Empirical Core Qualification Terminal

**Terminal disposition: CORE_EMPIRICAL_BLOCKED / FORMAL_PRODUCT_RELEASE_NO**  
Scope: [controller #147](https://github.com/kaicreator-mm/app8/issues/147), [SE10 #149](https://github.com/kaicreator-mm/app8/issues/149), [SE11 #150](https://github.com/kaicreator-mm/app8/issues/150), [aggregate #151](https://github.com/kaicreator-mm/app8/issues/151).  
Engineering baseline: v0.1–v0.3 **18/18 scoped engineering PASS**. This document does not revise or retract their narrow terminals.

## Facts and evidence

| Gate | Source evidence | Verdict and meaning |
|---|---|---|
| T01 exact reusable research/qualification assets | [PR #152](https://github.com/kaicreator-mm/app8/pull/152), #148 and [asset reuse audit](SE10_SE11_REUSE_AUDIT.md) | **PASS — Web asset audit only** |
| SE11 protocol succession | [PR #153](https://github.com/kaicreator-mm/app8/pull/153), [PR #64/#65 authority record](SE11_PROTOCOL_AUTHORITY_OVERLAY.md) | **PASS — normative currentness determination only** |
| Public-metadata preflight | [PR #154](https://github.com/kaicreator-mm/app8/pull/154), [Windows exact-HEAD R1 terminal](https://github.com/kaicreator-mm/app8/pull/154#issuecomment-6155441709) | **7/7 targeted PASS**, **207 passed, 1 skipped** full pytest; actual missing inputs yield SE10/SE11 **BLOCKED_PRE_EVALUATION** with expected exit 2; Release remains false |
| Windows exact-source checkout hardening | [PR #155](https://github.com/kaicreator-mm/app8/pull/155) | Frozen six file checkouts forced LF; avoids `core.autocrlf=true` CRLF false drift without changing any expected pin |
| SE10 reference/Gold availability | [#149 operator audit](https://github.com/kaicreator-mm/app8/issues/149#issuecomment-6155062052) | **BLOCKED**: 76/76 source pack present and hash-checked; no independently authored sealed Gold, Gold reviewer attestation or public commitment |
| SE11 actual software target readiness | [#150 operator audit](https://github.com/kaicreator-mm/app8/issues/150#issuecomment-6155062506) | **PARTIAL READY**: FFmpeg+ffprobe, pandas wheel, Windows MinIO, official LibreOffice MSI/runtime assets currently present with exact SHA256; pandas runtime deps require freezing; LibreOffice source→release DIVERGED requires applicability |
| SE11 hidden truth/final target selection | Same #150 audit | **BLOCKED**: no approved final `se11-execution-target-manifest-v1`, no sealed independently adjudicated 80 claims/decisive fixtures, no public commitment |

### Source and experiment identities

- SE10 source pack exact Git blob `4b3c9b62b1899653524f19a286924f942605210a` (FFmpeg 14, pandas 21, MinIO 18, LibreOffice 23), allowlist blob `5be0ed7674fcdfd7361a57fd4f29a6f9655c1df1`, protocol blob `08f9244a04275c780f778d50f638e332aa5807a2`.
- SE11 current protocol blob `1204c717eb590071a7b7f7e1cd3018b825ef1617`, historical blob `83abefb13e6a91e6b67a1c94937ca1bcce567aad` superseded for evaluation only; old Stage A artifacts are retained without rewrite.
- Exact Windows preflight PR #154 tested HEAD `b84941fb4b66eb3de662972fc1803c07a5d97f2a`, tree `71145f2b509b9f4ef261efdc6602f553f4dc3acc`. Host had global autocrlf conversion; the tester normalized its clean checkout to byte-identical pinned blobs and reran **PASS**. Subsequent #155 `.gitattributes` is a scoped checkout fix, not a new evaluated benchmark and has no independent post-merge regression claim.
- SE10/SE11 Stage B/Stage C synthetic scoring regression checks were authored historically; they establish scorer logic only. No four-asset blinded model predictions or evaluated 80-claim executions were run for v0.4.

## Terminal decisions

**T02 #149 / SPCL-001 / SE10** = `BLOCKED_BEFORE_EVALUATION`.

The frozen SE10 protocol requires an independently authored semantic Gold reference, a separate independent reviewer/attestation and only then a public SHA256 commitment. No such Gold or attestation exists in the checked sealed store. LLM- or Agent-authored dummy Gold may be used only as clearly labeled design examples; it cannot honestly meet the frozen empirical protocol. No semantic precision/coverage/F1/hallucination outcome is available, so all original thresholds are **UNTESTED**, not FAIL and not PASS.

**T03 #150 / SPCL-002 / SE11** = `BLOCKED_BEFORE_EVALUATION`.

Exact host artifact SHA256 availability has been checked for all four targets, but this is neither a final, reviewed, four-asset target manifest nor valid hidden behavioral truth. Final target applicability (especially LibreOffice DIVERGED relation), 80 private truth-class labels/decisive fixtures, isolated LLM-B plan, and actual 80 real observations do not exist as evaluated results. False-promotion/refutation/narrowing/boundary/reproducibility metrics are **UNTESTED**, not FAIL and not PASS.

**T04 #151 / CORE empirical release decision** = `BLOCKED_BECAUSE_SE10_AND_SE11_NOT_RUN`.

| Product claim | Current qualification |
|---|---|
| SPCL-001 semantic extraction across heterogeneous software | **UNPROVEN** |
| SPCL-002 falsification effectiveness and false-promotion rate | **UNPROVEN** |
| SPCL-003 multiple consumers; SPCL-004 Agent utility | **UNPROVEN** |
| SPCL-005 semantic search quality; SPCL-006 non-pixel coverage; SPCL-007 user demand | **UNPROVEN** |
| v0.1–v0.3 engineering, scoped Docker real signed Evidence | **PASS within documented scope** |
| Formal Product Release Qualification | **NO** |
| Release tag / publication authorized | **NO** |

### Why close the Task DAG with blocked results?

The v0.4 parent #147 explicitly allows a terminal `PASS/FAIL/BLOCKED` and permits closure on truthful **BLOCKED** completion of investigative tasks. Its task success rate is **not** 4/4 PASS: it consists of **1 audit PASS, 2 empirical BLOCKED and 1 aggregate BLOCKED**. Closing administrative Issues avoids fake repeated Web review/research and does not certify missing truth, unobserved software behavior, independent human review, or product maturity. These requirements remain backlog prerequisites for any future **evidence-qualified** release.

## Minimal reentry gates (not automatically scheduled)

1. Obtain **genuinely independent** human-authored/reviewed SE10 Gold with frozen 76-file anchors in an external sealed store and run the existing Stage B commitment; expose public hash only. If the owner does not authorize this dependency, SE10 official PASS is not assessable under its current frozen protocol.
2. Independently approve the actual SE11 four-target manifest, source-to-release applicability and pandas dependency pins **before** hidden corpus creation. Preserve original SHA256 targets, no automatic rebuild or substitution.
3. Curate/attest 80 independently observed hidden claims and decisive fixtures outside the prediction context; emit only public commitment, then conduct bounded LLM-B planning and real execution.
4. Only score with the frozen SE10 and SE11 Stage C and original thresholds; scorecard must retain every refutation and blocked case. If this is not feasible, adopt a **different explicitly labeled, non-equivalent evaluation** rather than laundering synthetic data into an empirical PASS.
5. Before any general product release, separately qualify SE12–SE16 according to Product acceptance criteria. v0.4 closeout alone authorizes none.

### What was NOT proven

No true software capability extraction accuracy, cross-asset recall, hallucination/error-family rate, multi-software falsification sensitivity, false-promotion rate, LLM-B evidence quality, independent Gold semantics, general Product Release eligibility, end-user Agent benefit or independent physical Ubuntu host was proven by v0.4.

```text
V04_T01_#148=PASS_AUDIT_CLOSED
V04_T02_#149=BLOCKED_BEFORE_EVALUATION
V04_T03_#150=BLOCKED_BEFORE_EVALUATION
V04_T04_#151=CORE_PRODUCT_QUALIFICATION_BLOCKED
V04_CONTROLLER_#147=DEFINED_STUDY_TERMINALIZED_WITH_BLOCKERS
PREVIOUS_ENGINEERING=18_OF_18_SCOPED_PASS
DEFINED_ISSUES_WITH_TERMINAL_DISPOSITION=22_OF_22
V04_EMPIRICAL_EVALUATIONS_PASS=0_OF_2
SE10=NOT_RUN
SE11=NOT_RUN
SE12_TO_SE16=UNPROVEN_DEFERRED
REAL_HOST_REINSTALL_OR_REBUILD=NOT_NEEDED_TO_REACH_THIS_TERMINAL
RELEASE_QUALIFIED=NO
TAG=NO
```
