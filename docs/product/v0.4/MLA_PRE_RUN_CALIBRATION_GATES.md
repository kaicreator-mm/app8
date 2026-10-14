# V04-MLA-1 — pre-run calibration and adversarial gap register (R0)

**Status: DRAFT / NOT FROZEN / NOT AN INDEPENDENT REVIEW PASS.**
Parent [#147](https://github.com/kaicreator-mm/app8/issues/147); supports [#149](https://github.com/kaicreator-mm/app8/issues/149), [#150](https://github.com/kaicreator-mm/app8/issues/150), [#165](https://github.com/kaicreator-mm/app8/issues/165), [#166](https://github.com/kaicreator-mm/app8/issues/166).
Owner authority: [V04-PO-MLA-001](MULTI_LLM_OWNER_DECISION.md); proposed experiment: [V04-MLA-1](MULTI_LLM_SUCCESSOR_PROTOCOL.md).

This is a **pre-registration gap register** to prevent an easy synthetic structural PASS from being mistaken for empirical product qualification. It is not a retrospective reinterpretation of original frozen SE10/SE11 and does not authorize any release. A genuinely independent fresh reviewer must resolve the listed open decisions, confirm a frozen scorer/cohort/review rule, and pin exact Git blobs **before evaluated outputs**.

## Adversarial findings to close before a successor qualification PASS

| ID | Severity | Failure mode | Required resolution |
|---|---|---|---|
| F01 | P1 | R/X-generated claims or favorable predictions selected after scores create survivorship bias | Freeze 24 opaque case slots (6 per asset), inclusion/exclusion and deterministic selection rule before P outputs; keep every included case in denominators including BLOCKED |
| F02 | P1 | A signed EXECUTED/SUPPORTED runner assertion tests arbitrary plan assertions and is **not** an independent semantic oracle | Freeze oracle ownership, semantics, expected counterexamples, fixture/replay digests and negative controls independently of P/R/X/J before observed scores; #168 receipt bridge alone cannot count BEHAVIOR_SUPPORTED |
| F03 | P1 | Model-derived references can measure agreement, not independent precision/recall or false promotion | Report reference-origin strata; treat model agreement separately; only independently adjudicated executable behavior/verified counterexample can enter behavior-grounded numerator |
| F04 | P1 | Public source-pack SHA, prompt/config SHA or caller-provided pre-freeze boolean cannot prove actual provider invocation, temporal ordering or model blindness | Retain trusted pre-run timestamps/immutable receipt order, raw provider request/response digests and access logs in private store; #169 pure structural capture is **not** proof of isolation |
| F05 | P1 | LibreOffice candidate 26.8.1.1 DIVERGED or incomplete pandas dependency pins silently become a four-asset qualification PASS | Review full binary + dependency/environment identity and claim-specific source-to-target applicability before observation; ineligible cases remain blocked and counted |
| F06 | P1 | Audit of only easy accepted cases misses false rejections and systematic hallucinations | Precommit per-asset stratified sample from the entire cohort, separately tag decision classes, always review every high-impact unresolved exception; no after-the-fact resampling, max 12 human cards with fail-closed overflow |
| F07 | P1 | 24-case error-free pilot is falsely interpreted as calibrated low false-promotion risk | Qualify pilot only as PROVISIONAL; independent fresh reviewer must set eventual cohort size, risk/coverage thresholds, confidence rule and stopping conditions **before** formal scored evaluation |
| F08 | P2 | Multiple prompts from same model lineage counted as independent corroboration | Preserve exact family/provider/version lineage, mark correlated R/X as provisional and do not present model counts as statistically independent |

## Pilot accounting — fixed, bounded and truthful

- **Cohort**: 24 positions, exactly 6 for each FFmpeg / pandas / MinIO / LibreOffice. Case selection policy and randomness commitment must be precommitted; no outcome-driven substitution.
- **Primary denominator** `N=24`: every included case, even when unsupported, unresolved, source-only, inapplicable, deferred or BLOCKED. Report 6-by-4 asset denominators separately.
- **Mutually exclusive outcome count**: `BEHAVIOR_SUPPORTED + SOURCE_SUPPORTED_ONLY + REFUTED + NARROWED + UNVERIFIED + BLOCKED = 24`. Do not score executable behavior by counting `SOURCE_SUPPORTED_ONLY`.
- **Promotion attempts**: separately count all positive predictions and verified unsupported attempts, including those correctly stopped by policy. A zero-denominator rate is `NOT_ESTIMABLE`, never 0% or PASS.
- **Oracle-qualified evidence**: `BEHAVIOR_SUPPORTED` requires matching frozen case/source/target/plan/fixture identity, replayable authenticated execution, and a **separate calibrated decisive oracle**; `SUPPORTED` in a signed runner receipt alone never supplies that oracle.
- **Negative outcomes**: preserve contradicted original claim IDs and narrower replacement IDs, with independently reproducible refutation or boundary evidence. Missing decisive oracle goes to `UNVERIFIED/BLOCKED`, not `REFUTED`.
- **Audit**: choose at least one predetermined sample per asset plus all high-impact unresolved conflicts, cover negative/blocked disposition where present, and enforce 12-card overall cap. Require reviewer decision + private evidence pointer; `DEFER` is fail-closed.
- **Budget**: record model calls and tokens/provider costs, deterministic executions, reviewer card count and unresolved rate, with stop-on-overrun; no unlimited judge cycles.
- **Metric report**: source-only rate /24, behavior-verified rate /24, invalid target rate /24, blocked/unverified /24, candidate agreement by origin, false-promotion attempts with an explicit denominator and uncertainty, refutation/narrowing with replay coverage, human reversal rate with sampled denominator, resource cost.

## Hard gates for any evaluated-successor score

1. Protocol/metric contract **independently reviewed and frozen by exact SHA before the evaluated run**; no post-result threshold, denominator, case, seed or inclusion edits.
2. Complete source/target/relation/dependency approval **for each claim evaluated as behavior**; `DIVERGED` requires a separate applicability proof.
3. P/R/X/J isolation supported by retained trusted invocation and transcript evidence, not only caller-provided hashes; hidden oracle/decisive fixture access = 0 before prediction freeze.
4. All 24 pilot cases accounted for; **zero unverified Capability promotions**, zero acknowledged leakage, zero unaudited required human exceptions, and no trust-origin upgrade by model vote.
5. Every behavior-supported case has signed verified execution **and an independently reviewed calibrated oracle**. H may reject but cannot override deterministic counterevidence.
6. Missing required evidence, review-card budget overflow, unavailable oracle, or score denominators not computable => **BLOCKED/PROVISIONAL**, never inferred PASS.

A 24-case pilot is **not** adequately powered to certify a low population false-promotion rate by itself. Even with 0 failures in 24 independent trials, the one-sided 95% exact binomial upper bound is approximately **11.7%** (and independence/representative sampling are themselves unproven). A claimed ≤5% upper bound requires a separately determined sample/stopping plan; **do not silently reuse** the historical SE11 80-case threshold with model-sourced reference labels.

## Explicit unresolved independent-review decisions

- Decide candidate generation and pairing order (freeze cases before P predictions; R/X independent; no evaluation leakage); record exact schema and metric digests.
- Specify what constitutes an independently calibrated semantic/source-only criterion and how it is sampled; model proposals cannot certify themselves.
- Freeze eventual formal study cohort, population inference limits, false-promotion/coverage/abstention thresholds, multiple-asset aggregation and fail-closed confidence/stop rule.
- Confirm human sample selection includes failure/blocked strata as measurable, while preserving the user-approved default 4–8 cards and maximum 12; any amended algorithm is versioned and reviewed before use.
- Record actual independent reviewer identity, exact reviewed Git commit/tree and verdict. An author's own review or synthetic unit test must not be labeled independent.

```text
PRE_RUN_CALIBRATION=R0_DRAFT_NOT_FROZEN
ORIGINAL_SE10_SE11=NOT_RUN_OR_HISTORICALLY_BLOCKED
MLA_24_CASE_PILOT=NOT_RUN
SIGNED_OBSERVATION_IS_SEMANTIC_ORACLE=NO
PROVIDER_HASH_IS_INVOCATION_PROOF=NO
INDEPENDENT_FRESH_REVIEW=OPEN
CURRENT_EMPIRICAL_RELEASE_AUTHORITY=NO
```
