# V04-MLA-1 — bounded 24-case pilot preregistration R1

**Authority:** [V04-PO-MLA-001](MULTI_LLM_OWNER_DECISION.md) and [successor candidate](MULTI_LLM_SUCCESSOR_PROTOCOL.md).  
**State:** `AUTHOR_DRAFT_NOT_FROZEN`. Independent Fresh protocol/metric reviewer required **before** any pilot prediction or trial result.  
**Scope:** #147, #149/#150, support #165/#166. Not a rewrite of frozen original SE10/SE11 or authorization for Release PASS.

## A. Prospective cohort and no-cherry-picking rule

Exactly **24 case slots**; six per asset and no outcome-driven replacement:

| Asset | Case identifiers | Frozen source scope |
|---|---|---|
| FFmpeg | `V04-FFMPEG-001`…`006` | 14 reviewed source anchors |
| pandas | `V04-PANDAS-001`…`006` | 21 reviewed source anchors |
| MinIO | `V04-MINIO-001`…`006` | 18 reviewed source anchors |
| LibreOffice | `V04-LIBREOFFICE-001`…`006` | 23 reviewed source anchors |

Source-pack Git blob: `4b3c9b62b1899653524f19a286924f942605210a`; reviewed allowlist Git blob: `5be0ed7674fcdfd7361a57fd4f29a6f9655c1df1`. All reference outputs are `LLM_PROPOSED`, **not** independent human Gold.

Prior to any P/R/X response, independently fix a non-model-controlled `selection_seed_sha256` and use `SHA256(seed + ":" + asset + ":" + path + ":" + blob)` (ascending hex, path as tie-break) to pick six **distinct** source anchors per asset from the pinned allowlist. Then assign sorted ranks 001…006. Snapshot the exact six immutable source anchors, public user-job/task instruction per slot, inclusion/exclusion reasons and source context bytes in a retained private manifest; publish a safe digest. If a chosen anchor does not permit an assessable semantic task, keep its slot **UNVERIFIED/BLOCKED** and count it; never replace it after seeing outputs.

The existing public 24-case reducer accepts arbitrary allowlisted anchors and validates *identity*, not this stricter deterministic selection. Therefore **a new deterministic anchor-selection check or independent pre-run attestation is required before actual pilot execution**; do not claim this draft has already frozen or enforced selection.

P receives only the predeclared user job and source material, never R/X/J responses, hidden Oracle, decisive fixtures or any result labels. R and X independently receive the same case slots/source/job but not P's output or each other's output. R proposes semantic reference, X proposes falsification hypotheses; no model may change the cohort, oracle or denominator. Batch each model **once per asset**, giving **4 P + 4 R + 4 X = 12 base invocations**. An incomplete model batch blocks the affected slots; it is not quietly rerun with new samples. One J invocation may be added per genuinely unresolved high-impact conflict, capped at **12 total J calls** (24 overall model calls), never for an already deterministically settled fact.

### A.1. Prospective case intent and fixed denominator (R2 P1-D)

Each pre-output sealed job binds its exact text, claim contract, negative
boundary, boolean `requires_runtime_observation` and `evaluation_intent`
into the job SHA256 and per-role source contexts. The deterministic compiler
accepts `BEHAVIOR_CANDIDATE` iff runtime observation is required, otherwise
`SOURCE_SEMANTIC`. **The semantic requirement of the job alone determines
the distinction; never target readiness, model outputs or final scoring.**

Source-only claims describe pinned source/API declarations without asserting
successful behavior. Claims about real execution, outputs, compatibility,
side effects, performance, process status or reproducible runtime
counterexamples necessarily require behavior observation. An independent
pre-run reviewer must inspect the 24 private exact job texts against those
proposed labels and bind a sealed manifest digest; the operator-supplied
boolean alone is **not** independently validated.

All 24 slots, six per asset, remain in the denominator. An unapproved
behavior target (including LibreOffice DIVERGED) is `BLOCKED`, **never
reclassified** to source-only. Source-semantic dry-run reporting may describe
only model-proposal agreement, coverage/abstention, blocked counts, costs
and status; it cannot establish `SOURCE_SUPPORTED_ONLY`,
`BEHAVIOR_SUPPORTED`, independent Gold, false-promotion rates or promotion.
Pre-oracle outcomes remain `UNVERIFIED`/`BLOCKED`.

This A.1 revision remains `AUTHOR_DRAFT_NOT_FROZEN` until independent
incremental R3 approval. Chronology P1-A, H seed P1-B, independent conflict
P1-C, actual Oracle/H authority remain separate blockers. No provider calls
are authorized by this draft.

## B. Pre-run freeze ledger (privileged and append-only)

The operator must record these *before* the first output, with independently verifiable chronological storage, not just the caller's `frozen_before_first_response=true` flag:

1. Campaign ID/version, repository baseline HEAD/tree, this protocol Git blob, current public schema/reducer Git blobs, exact 76-source allowlist, 24 case slots, seed, source context digests and immutable inclusion denominator.
2. Separate P/R/X provider, family, exact model version, request endpoint identity, prompt bytes and sampling parameters, request caps, context ACL and model configuration digest. R/X same family => explicitly correlated/provisional.
3. Exact real-software execution target binaries, dependencies, environment and source→target relation **for each behavior case**, independently reviewed. pandas must pin numpy/python-dateutil/six. LibreOffice 26.8.1.1 is `DIVERGED` until claim-specific applicability is reviewed. An approved *candidate* is not the final target authority.
4. Decisive Oracle/fixture/replay rule and private commitment, authored/calibrated independently of evaluated P/R/X/J; no target credential or hidden truth shared with prediction providers.
5. Human sampling version/seed (current deterministic selector: one per asset + all high-impact unresolved cases), reviewer authority process, sealed card visibility, required sign-off and 12-card maximum. Seed/case freeze must precede predictions; no model-selected post-result sample.
6. Numeric **token/currency/time** caps, provider-call ceiling (24), trusted execution cap, hard-stop conditions and artifact retention/deletion policy. If any required budget is unspecified, trial authorization is **BLOCKED**, not assumed unlimited.

Hashes from #169/#172 prove structural correspondence of *submitted* bytes only, not real provider transport, chronology or isolation. The operator must retain actual trusted request/response telemetry and its sequence of timestamps in the sealed store. Never publish API keys, private Gold/oracle truth, raw prompts or decisive fixtures.

## C. Execution and case-outcome authority

After all freeze gates:

```text
24 slots fixed
  -> source- and model-configuration exact pin
  -> blind 12 P/R/X provider invocations + retained transport evidence
  -> source applicability / real target eligibility checks
  -> independently calibrated deterministic fixture + signed runner receipt
  -> optional J only on unresolved high-impact contradictions
  -> deterministic four-asset audit sample + mandatory exceptions (4–12 H cards)
  -> independent human H decisions bound to sealed evidence
  -> six exclusive case classes + fixed-denominator report
```

**No shortcuts:** authenticated signed `EXECUTED/SUPPORTED` is only execution provenance, not a semantic oracle. An independent calibrated oracle plus appropriate real behavior is needed for `BEHAVIOR_SUPPORTED`. Source-only can be `SOURCE_SUPPORTED_ONLY` as a hypothesis, **never verified runnable**. `REFUTED` or `NARROWED` require independently reproducible counterevidence. Missing oracle => `UNVERIFIED`; invalid target/required reviewer unavailable => `BLOCKED`. Model/J majority voting has no factual authority.

The public #173 J/H queue is **candidate metadata only**, not proof of genuine human involvement. Actual H reviewer authentication, immutable decision receipt and correct sealed-case access must be checked by a trusted service; `HUMAN_SELF_REPORT_UNVERIFIED` is always nonauthoritative. Defer/overflow/absent H response => BLOCKED.

## D. Pilot outcome table and stopping rules

**All 24 case IDs remain in the denominator**, including ineligible, refuted, narrowed, missing source, unverified and blocked cases. Report all six mutually exclusive totals, separately for each of four assets. Require total count exactly 24.

- Report executed/target eligible count; source-only count; verified supported count; replayably refuted/narrowed count; unverified/blocked count; human sampled/reversed/deferred count and denominator; actual P/R/X/J calls/tokens/cost; provider/target failures and all missing hard gates.
- Count positive **promotion attempts** separately from permitted promotions, including rejected attempts. False-promotion numerator requires independent Oracle truth; if denominator is 0 or Oracle qualification missing, report `NOT_ESTIMABLE`, **never** 0% accuracy or PASS.
- Pilot **safety stop**: any oracle leakage, unauthorized Capability promotion, invalid signed provenance, cohort substitution, missing required deterministic check or exceeded execution/provider/human budget stops further scoring; record evidence and `BLOCKED` or `FAIL_SAFETY`, without silently dropping cases.
- **Human cap**: four asset-stratified samples minimum (when eligible), plus every impactful unresolved exception, total **≤12**; more than 12 required => `BLOCKED_HUMAN_REVIEW_BUDGET`. Partial/untrusted H reports cannot satisfy this gate.
- A source/target mismatch, pandas dependency drift or unresolved LibreOffice release applicability affects the particular cases and the four-asset coverage claim. Do not falsely call 24/24 verified if any case is ineligible.
- Trial terminal: `V04_MLA_PROVISIONAL` when evidence is substantially collected and boundaries are honest; `BLOCKED` or `FAIL_SAFETY` if prerequisite/safety gates fail. **There is NO pilot-level formal product PASS terminal.**

## E. Statistical and release limits

Twenty-four observations (even 0/24 verified false promotions) are insufficient to establish a population 5% upper false-promotion rate. For independent exchangeable trials, one-sided exact 95% upper bound after 0 failures is `1 - 0.05^(1/24) ≈ 11.7%`; achieving an upper bound ≤5% requires **at least 59 independently justified at-risk opportunities** with zero failures and pre-registered sampling assumptions. An 80-case cohort does not automatically produce 59 *promotion attempts*. The formal successor study must independently pre-register sample sizes, exposure denominators, all thresholds, precision/coverage handling, confidence method and stopping rule before *its own* evaluated outputs. Model-generated reference agreement cannot be called independent-Gold precision/recall.

Original SE10 48 human-Gold benchmark and original SE11 80 hidden-truth benchmark remain `NOT_RUN/BLOCKED`; this pilot **does not substitute for either**. SE12–SE16 remain deferred/unproven and general Product Release remains NO.

## F. Independent Fresh review checklist — unresolved until recorded

A different qualified reviewer/model family must audit cohort-selection completeness, time-frozen model blindness, oracle ownership, real target applicability, H selection/authority, budget ceilings, pre-specified metrics and all counterexamples; record reviewed exact HEAD/tree and decision `PASS_FOR_PILOT_PROVISIONAL_ONLY` or `NEEDS_REVISION`. Do **not** stamp this author draft as independently reviewed or freeze it automatically.

```text
AUTHOR_PROTOCOL=R1_DRAFT_NOT_FROZEN
REAL_MODEL_EXECUTION=NOT_RUN
REAL_TARGET_INDEPENDENT_ORACLE=NOT_RUN
HUMAN_DECISIONS=NOT_RUN
PUBLIC_STRUCTURE_AND_RECEIPT_CODE=REUSED
PILOT_RELEASE_PASS=NOT_AVAILABLE
ORIGINAL_SE10_SE11=NOT_RUN
GENERAL_RELEASE=NO
```
