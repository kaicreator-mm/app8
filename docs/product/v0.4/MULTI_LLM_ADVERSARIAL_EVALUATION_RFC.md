# app8 v0.4 — Multi-LLM Adversarial Evidence Evaluation (PROPOSAL)

**Status: DRAFT_FOR_PRODUCT_OWNER_DECISION / NOT NORMATIVE / NOT EXECUTION AUTHORIZATION**

Affects ongoing [#149 SE10](https://github.com/kaicreator-mm/app8/issues/149), [#150 SE11](https://github.com/kaicreator-mm/app8/issues/150), [#151 release terminal](https://github.com/kaicreator-mm/app8/issues/151), parent [#147](https://github.com/kaicreator-mm/app8/issues/147). User-requested design alternative to the labor-intensive requirement for independently human-authored 48 semantic Gold references and 80 hidden claims. This **does not edit or supersede** frozen SE10 blob `08f9244a04275c780f778d50f638e332aa5807a2` nor current SE11 blob `1204c717eb590071a7b7f7e1cd3018b825ef1617`. Historical [v0.4 BLOCKED terminal](../../release/v0.4/CORE_EMPIRICAL_TERMINAL.md) remains true.

## 1. Proposed goal and explicit tradeoff

Replace mandatory exhaustive human reference authorship with multiple *model-distinct, independent, blind* proposal and adversarial passes, ground accepted conclusions in pinned source **and when appropriate in real executable behavior**, and require humans to review a bounded exceptional sample rather than read all 76 source files. The evaluation measures **evidence-supported machine-verified quality**. Such a reference is **not independent-human semantic Gold**, and it **cannot claim old-protocol SE10 precision/recall PASS** unless an authorized successor protocol explicitly defines comparable acceptance criteria.

Unanimous model confidence or majority vote is **never** equivalent to semantic truth; common-mode model errors, positional bias and self-preference are plausible. The deterministic verifier/actual software behavior is independent of the LLMs. Models may propose tests but cannot self-certify their expected outcome as real observation.

## 2. Roles, isolation and lowest useful resource budget

| Role | Input / responsibility | Trust boundary |
|---|---|---|
| P — app8 predictor-under-test | Only frozen 76-source pack plus frozen production prompt/config; proposes semantic Capabilities | **Blind** to competing reference drafts, challenges, hidden fixtures and adjudication |
| R — independent reference builder | Different model family/config from P; independently proposes task-level Capabilities with exact source anchors, variant/failure/negative boundaries | Cannot see P or its outputs; output is **candidate reference**, not Gold |
| X — adversarial challenger | Different model family/config if practical; independently seeks unsupported merges, missed failure semantics, callable spam, source/version mismatches and minimal falsification fixtures | Does not see private target truth or model scoring; source references mandatory |
| V — deterministic evidence verifier | Git/sha256 source pin checking; static binding/schema/rule checks; safe sandbox execution of reproducible software fixtures; records observations and reproducible evidence hashes | **No LLM vote** can override deterministic contradiction or absent observation |
| J — adjudicator (on disagreement only) | Third independent model/config; receives anonymized and shuffled R/X claims with evidence links and counterexamples | Must cite evidence and return `ACCEPT/REJECT/NEEDS_HUMAN/UNVERIFIED`, cannot turn absent evidence into PASS |
| H — bounded human reviewer | Sees concise evidence + counterexample diff and chooses `CONFIRM/REJECT/DEFER` | **Not** a declaration that every case was independently human-authored or audited |

Default path: P is evaluated; R and X run **independently in parallel** before any transcript exchange; V validates evidence; J is **escalation only**, not a full mandatory extra call for every case; H sees samples/exception queue only. At least two genuinely different model families for proposal/challenge if available; record providers, versions, prompts, sampling, source pack and runtime SHA/config. If model diversity unavailable, label `SAME_FAMILY_CORRELATED_RISK` and escalate more evidence/human audit, not false independence.

**Cost control:** one initial R pass + one X pass per asset or batched anchor set; at most one J escalation per unresolved claim; no unlimited debate loops; cache source extraction by exact pin. Challenger priority is high-impact/promotion-capable cases.

## 3. SE10: evaluate user-task semantics, not a fake machine Gold

1. Freeze source-pack identities unchanged (FFmpeg 14, pandas 21, MinIO 18, LibreOffice 23). P predicts from frozen pack before seeing any R/X/judgments.
2. R independently drafts at least 12 **candidate references** per asset to retain original portfolio breadth; each item binds user job, sources, inputs/outputs, variants, failure semantics, binding equivalence and negative boundaries.
3. X independently proposes omissions, over-splitting, unsupported equivalence, incorrect source anchors and contradictory source excerpts. R may revise only **before** frozen comparison; preserve initial versions and all changes.
4. V validates referenced SHA/paths and static interfaces; when behavior is material, execute minimal bounded sandbox fixtures against exact target binaries. Source-only, non-executable semantic assertions remain `SOURCE_SUPPORTED`, **not** automatically `BEHAVIOR_VERIFIED`.
5. J arbitrates disagreements using shuffled, blinded identities and source/observation links. Conflicting, non-reproducible or ambiguous cases are `NEEDS_HUMAN` or `UNVERIFIED`, excluded from any *verified* numerator but **included in coverage/uncertainty reporting** (no favorable denominator shrink).
6. H reviews **all high-impact promotions and unresolved contradictory cases** plus a frozen stratified random audit of otherwise accepted cases. Suggested initial budget **up to 12 manual cards total** across four assets; if exceptional cases exceed budget or audited errors exceed predeclared threshold, return `BLOCKED` or request more review. The cap is **not** an exemption from safety/uncertainty.

Public metrics to distinguish: source-evidence validity, user-task/reference agreement, tested behavior support, challenged-claim refutation, uncovered uncertainty, reviewer disagreement, human overturn rate, per-asset counts/denominators and cost. Do **not** rename model consensus to human `Gold` or report original `SE10_PRECISION/RECALL_PASS` under this design without a newly frozen, independently reviewed measurement definition.

## 4. SE11: separate hidden truth from LLM-B and require executable oracle

1. Independently review/freeze the **real** four-target manifest, exact binaries/images/deps and source→target claim applicability before selecting tests. pandas: pin numpy/python-dateutil/six. LibreOffice: `DIVERGED` requires release-specific proof, not master-only source semantics. Same historical artifacts may be reused.
2. R (without seeing LLM-B plans) proposes testable claims; X produces negative/overbroad/near-miss counterexamples and fixtures. Use existing **4×20 = 80 planned cases** as a *candidate* cohort only; each per-asset 8 TRUE / 4 MATERIALLY_FALSE / 4 OVERBROAD / 4 NEAR_MISS grouping must be justified by **real observed behavior**, not adversarial model labeling.
3. V executes claims on pinned target with reproducible inputs/resets, recording stdout/stderr/status/side effects + evidence SHA and independent classification rules. Oracle must be determined before LLM-B exposure; use stable expected outputs, invariants and metamorphic properties where possible. If behavior does not unambiguously establish a truth class, keep `UNVERIFIED` and block claim-level scored promotion.
4. Freeze isolated private candidate truth and evidence commitments **before** exposing only anonymized claim text + allowed context to LLM-B (planner under test). Strict taint/visibility separation: the evaluated planner sees **no hidden truth, model proposer rationale or decisive fixtures**.
5. LLM-B plans falsification; executor runs plans on the same pinned target; scorer compares against independently recorded observations. J/H can inspect ambiguous cases *after* frozen plan/execution as governed by the successor protocol, never retroactively select favorable replacement cases.
6. Record all 80 original IDs, every unsupported promotion, environment BLOCKED, denominator and evidence drift; no after-the-fact claim swapping or threshold retuning.

**Important:** The existing `research/e11/stage-b/commit_hidden.py` validates private labels/structure but **does not prove origin**. An AI-generated hidden corpus cannot be published under an attestation claiming independent human authorship or an unchanged human-only protocol.

## 5. Human interface: single concise decision card

For each card show user job + claim, relevant pinned source excerpt, real execution observation when available, R/X disagreement, J tentative disposition, effect on downstream Capability promotion, and three choices: **Confirm / Reject / Defer**. The human need not read all 76 files: click-through source + reproducible test evidence is available for disputed cases.

Human confirmation is a **sampled owner acceptance** of the evidence workflow, not evidence of having independently reviewed every semantic reference. High-risk unknown cases remain non-promotable even when the 12-card review budget is exhausted.

## 6. Acceptance gate before implementing or scoring

- Product Owner explicitly approves this successor **evidence-based** study and study naming. Independent Product review verifies no model self-scoring, frozen source/target bytes, oracle separation, sample selection, denominator integrity, exposure and false-promotion safeguards. Existing original frozen protocols remain immutable and historically valid.
- Define/snapshot new schema IDs and acceptance thresholds **before** exposing P's predictions or LLM-B plans. Avoid converting 48 model references to declared `model_generated_gold=false` or setting independent human audit booleans dishonestly; introduce `reference_origin=LLM_PROPOSED`, `verification_basis`, `human_review_scope=SAMPLED`.
- Suggested initial model-diversity + 4-software dry run is **non-release evidence**, not SE10/SE11 normative PASS. Promote to official Product qualification only after independent review of successor protocol and measured calibration of verifier/J against a small authenticated human or deterministic truth anchor sample. Otherwise report `PROVISIONAL_EVIDENCE_ONLY`.
- No runtime/source/safety changes, no new large research workstreams, and no automatic Release tag from approval of this RFC alone.

## 7. Outputs and scope

```text
V04_MULTI_LLM_ADVERSARIAL_EVAL_RFC=DRAFT_NOT_APPROVED
FROZEN_OLD_SE10_PROTOCOL=UNCHANGED
FROZEN_OLD_SE11_PROTOCOL=UNCHANGED
HUMAN_ONLY_EXHAUSTIVE_GOLD=PROPOSED_REPLACEMENT_NOT_YET_ADOPTED
REVIEW_MANUAL_CARDS_TARGET=UP_TO_12_PLUS_MANDATORY_EXCEPTIONS
DETERMINISTIC_EVIDENCE_OR_ORACLE=REQUIRED_FOR_BEHAVIOR_VERIFICATION
MODEL_CONSENSUS_AS_TRUTH=FORBIDDEN
ORIGINAL_SE10_SE11_EVALUATION=NOT_RUN
FULL_PRODUCT_RELEASE_QUALIFIED=NO
```

Relevant evidence on judge bias and false consensus: [Shi et al., IJCNLP-AACL 2025](https://aclanthology.org/2025.ijcnlp-long.18/) (position bias) and [Cui et al., ACL Findings 2026, Free-MAD](https://aclanthology.org/2026.findings-acl.1600/) (conformity and limitations of majority-vote debate).
