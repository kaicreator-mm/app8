# App8 v0.4 — Capability Compiler MVP product scope reset (R1)

> **Authority:** explicit Product Owner instruction on 2026-10-26: “按‘软件能力编译器’为最终目标”. **Disposition:** PRODUCT_DIRECTION_APPROVED; this document is the prospective v0.4 MVP scope draft, to be independently reviewed at an exact SHA before declaring Product/L2 FREEZE. **No actual MVP verification or Release PASS is claimed.**
>
> Existing frozen historical SE10/SE11 bytes and results remain unchanged. The owner-approved October 14 multi-LLM design is **retained as an optional evaluation/research lane**, not made retroactively invalid. This prospective scope does not inherit historical PASS or waive missing evidence. Pinned existing ADS specification in app8 remains v4.9.0@`7929012f36a2202dcc2edc7a414b8163adc7afbd`; ADS #1241 Web-first and #1337 value-first are execution guidance, not silent pin upgrades.

## A. Actual product thesis and scope

App8 turns real existing software into *reusable, evidence-backed, task-level Capabilities* consumable by Agents:

```text
versioned software knowledge + permitted bindings
  -> model-origin user-job hypothesis (never truth)
  -> typed Capability candidate + source/target pins
  -> bounded positive / negative real observation
  -> durable authenticated Evidence + deterministic readiness
  -> compiled single-meaning Capability
  -> one real permitted Agent-facing CLI/SDK adapter
  -> successful invocation + second-use without rediscovery
```

**v0.4 is not an LLM benchmark platform, signing framework, universal agent runtime, MCP server generator, or library extraction project.** Its unique deliverable is a small complete *software→useful Agent capability* journey. Replace no mature OS/transport/document tools solely to satisfy custom preflights.

## B. What exists, and the real gap

| Implemented and reusable | Actual boundary / missing product value |
|---|---|
| `discover_source` + pinned source, `freeze_hypotheses`, `freeze_falsification_plan`, in-memory search | `app8.cli.compile_preview` currently consumes **pre-existing model JSON**, then fills missing I/O/bindings with placeholders; no autonomous end-to-end generation or trust-qualified export |
| `capability-v1`, `evidence-v1`, `EvidenceStore`, `AttestationGate`, trusted Docker runner | Evidence can qualify a precise stored/signed scope; previously observed FFmpeg/pandas host run results are **not automatically valid app8 signed Capability Evidence** |
| `qualify_stored_capability`, `build_projections`, `verify_projection_suite`, `CapabilityIndex` | Projection CLI/MCP/Skill objects are metadata. `invocation_enabled` does **not** create an installed tool, working MCP server or authorized runtime call. One real Agent consumer is missing |
| v4 12/12 real paid P/R/X requests and R24 24-case exploratory crosswalk (PR #204 merged version-only) | Original v4 sealed P ingress 0/4; 12/12 normalized derived views are **post-hoc diagnostic**, 19 source semantics unverified, 7 H not adjudicated; useful *candidate* input, not frozen-semantics Gold or product acceptance |

## C. Bounded MVP portfolio

- **FFmpeg**: prefer one user-meaningful media transformation/inspection job with an existing scoped real target. Candidate fixture FFmpeg004 has 12×1024-byte observed PASS; FFmpeg005 preserves **original byte-identity REFUTED** and narrowed mirror relation. Do not force two unrelated fixtures into one semantic Capability.
- **pandas**: prefer one user-meaningful table merge/validation job. Existing pandas002 13/13 host observations are a candidate evidence input under exact package/environment pins.
- **No requirement to run MinIO object-lock mutation or LibreOffice MSI on current shared Windows Host for this MVP.** Keep their pre-existing V04 behavior cases `NOT_RUN`, their original four-asset study denominator unchanged, and any future product claim limited to the two implemented assets. Restoring these assets needs a separate high-ROI bounded product need and lawful Host authorization.

## D. Prospectively frozen-after-review acceptance (not self-asserted)

One **complete, demonstrable** user-job Capability for **each of two independent software types** (FFmpeg native CLI and pandas library) is the desired minimal scope:

1. **Discovery/compile**: actual model-origin/previously generated source candidate, exact source/blob, target and binding identity, user job, arguments/types, outputs, failure modes, side effects, negative boundaries. Never call a hand-authored static demo `autonomously model-generated`. If v4 P prompt cannot be attributed to an approved app8 product prompt, report external-proposal provenance honestly.
2. **Reality**: at least one real positive execution and one adversarial/negative input *per selected capability* within an allowed Host/runner. Signed Evidence only when verification owner, nonce, digest and admissible scope genuinely align; otherwise `BLOCKED/NOT_RUN` (never synthesize valid-looking signed receipts).
3. **Compile/readiness**: stored full ledger (including contradictions), deterministic readiness, no guessed `export_ready`; supports positive, negative, stale, wrong-version, unsupported and missing-Evidence terminal paths. A narrowed variant may be a **new distinct bounded claim** with independent acceptance, not retroactive repair of a refuted frozen test.
4. **Actually consume**: one minimal working Agent-facing CLI or SDK adapter using a scoped ready Capability and the already trusted execution path; verified output from the real target. Metadata projections do not count as working adapters. The second consumer/use reuses persisted Capability without full source reread or fresh model inference.
5. **Prove ROI**: record the source read/model calls, real target outcomes, both consumer invocations, reuse without re-generating a wrapper, and reasons for blocked unsupported requests. Report **actual journeys completed / 2 assets** and real scoped export status; no SE10 human-Gold/SE11 hidden-claim accuracy claims.

All five items are mandatory for **scoped CC-MVP READY**; failing any item means **PARTIAL/BLOCKED**, not a threshold relaxation. General product / GA release requires separately reviewed criteria and remains unproven.

## E. Work excluded from the MVP critical path

- No 48 human-authored Gold, no original 80 hidden-truth campaign, no mandatory R24/R27 seven H adjudications, no new v5 P/R/X paid provider campaign. All remain separate research/quality evidence, preserved with actual historic status.
- No new VC++ redistributable alternate identity system; PR #203 intentionally closed unmerged. No MinIO destructive S3 effects without explicit permit.
- No general-purpose MCP server / Skill installer / comprehensive UI automation, no proprietary SigV4 client or PDF engine, no new generic LLM eval harness.
- No unconditional human adjudication. Real human decision is an exception only where a *specific consequential unresolved Capability claim* changes a support or side-effect decision. A `DEFER` is an acceptable conservative terminal for that claim.
- No repeat full-suite CI per leaf task. Reuse exact valid Host evidence and focused tests, then one version closure.

## F. Version truth and decisions

Historical **18/18** v0.1–v0.3 engineering + **1/4** original v0.4 formal research tasks = **19/22** completed **of the historical DAG**. Do **not** reset, lower, or misreport this percentage as an MVP progress measure. New CC-MVP tasks are tracked **separately** as CC01–CC04 at 0/4 until real delivery. Prior controller [#147](https://github.com/kaicreator-mm/app8/issues/147) remains the version authority, old #149/#150/#151 studies are **not closed as PASS**. [#166](https://github.com/kaicreator-mm/app8/issues/166) v4 pilot remains actual exploration not future mandatory H.

Source-frozen SE10 48 Gold and SE11 80 hidden study `NOT_RUN`; SE12–SE16 unproven; no prior signed data, original denominator, blob, R24 report or past terminal rewritten. This scope reset may result in a separate **v0.4 CC-MVP scoped qualification**, not retroactive SE10/SE11 results. `main` stays unchanged until version branch closure and independent scoped Release Qualification.

**Owner intent approved**; independent Product/L2 review of this proposed acceptance and integration plan is still required before declaring `CC_MVP_SCOPE_FREEZE=YES`.
