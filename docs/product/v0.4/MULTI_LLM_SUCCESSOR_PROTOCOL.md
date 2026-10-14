# V04-MLA-1 — successor empirical evaluation protocol (implementation contract candidate)

**Authority:** [owner-approved V04-PO-MLA-001](MULTI_LLM_OWNER_DECISION.md)  
**Status:** CONTRACT_CANDIDATE / INDEPENDENT_FRESH_REVIEW_AND_METRIC_FREEZE_PENDING  
**Replaces for *future* v0.4 study:** mandatory exhaustive human Gold curation as the default evaluation method; **not** the original SE10/SE11 result identities or past BLOCKED terminal.  
**Not authorization for:** release PASS, human-Gold attestation or scoring unscreened LLM consensus.

## Scope and invariants

The central falsifiable claim is that app8's automatically proposed task-level Capability is supported by pinned source constraints and, where claiming observed behavior, reproducible execution evidence. Model disagreement is useful *search guidance*, never factual truth.

- **Knowledge source:** existing immutable SE10 76-anchor pack (FFmpeg 14, pandas 21, MinIO 18, LibreOffice 23).
- **Execution target:** reuse SE11 real target candidates only after separately reviewed exact binary/environment/dependency pins. FFmpeg, pandas and MinIO historically map `SAME`; LibreOffice maps `DIVERGED` and requires claim-specific release applicability. Candidate identity does **not** equal approved target.
- **Independent model roles:** P (evaluated app8 predictor), R (reference proposer), X (adversarial challenger), optional J (third judge for unresolved source-backed conflicts). Run P, R, X *blind* with separate contexts; preference for different model families across R/X, record correlated-family fallback and never count it as statistical independence. No J invocation for facts already settled deterministically.
- **Evidence role:** V pins source/target SHA256/Git blob, validates typed interfaces, runs bounded fixtures in the existing trusted runner and writes signed/replayable observations; deterministic policy, not another LLM vote.
- **Human authority:** H independently sees concise decision cards for impactful irreconcilable conflicts plus an audit sample. H may `CONFIRM/REJECT/DEFER`, and may reject a promotion; H is **not** claimed to have authored all candidate references or reviewed all inputs.
- **Cost:** 1 R and 1 X pass (batched) per asset; at most 1 J escalation per unresolved claim; no recursive debate or external source expansion after freeze. Initial dry-run portfolio **24 candidates (6/asset)**; fuller qualification cohort/denominators are frozen separately **before** scores. Original SE11 80 claims cannot be silently relabeled as validated by a 24-case pilot.

## State machine / decision authority

```text
FROZEN_INPUTS
  -> BLIND_P_R_X_CAPTURED (immutable transcript/prompt/model hash)
  -> SOURCE_CHECKED
  -> TARGET_ELIGIBILITY_CHECKED (if behavioral)
  -> DETERMINISTIC_EVIDENCE_OBSERVED_OR_BLOCKED
  -> OPTIONAL_J_ON_CONFLICT
  -> FIXED_HUMAN_SAMPLE_AND_EXCEPTION_QUEUE
  -> REDUCED_TERMINAL_WITH_ORIGIN_AND_DENOMINATORS
```

The reducer must reject missing stage commitments, malformed or swapped target identities, output-before-freeze, hidden oracle leakage, unresolved source→target mappings and model-origin evidence masquerading as real observations. Every case belongs to exactly one terminal class:

| Case outcome | Required evidence | Can promote? |
|---|---|---|
| `BEHAVIOR_SUPPORTED` | Exact target identity + replayable real decisive observation + independent oracle + no unresolved contradiction | Yes within that bounded behavior |
| `SOURCE_SUPPORTED_ONLY` | Frozen source anchor verified and source-linked semantic task; no real observation asserted | Only source-level hypothesis; **not** verified runnable Capability |
| `REFUTED` | Deterministic counterexample against asserted scope | No |
| `NARROWED` | Replayable boundary/constraint proof with original claim retained | Only newly scoped bounded variant, subject to new evidence |
| `UNVERIFIED` | Missing/ambiguous oracle or unresolved LLM disagreement | No |
| `BLOCKED` | Target/env/identity/taint/mandatory-review prerequisite unavailable | No |

A high-confidence model answer is insufficient; a human `CONFIRM` cannot override contradictory signed execution. Deferral is fail-closed. Source-only propositions cannot be counted in behavior-verified numerator.

## Required immutable artifacts (schema IDs to implement)

- `v04-mla-freeze-v1`: campaign ID; pre-result source/target artifact hashes; P/R/X/J model family+provider+config prompt & sampling hashes; reference origin `LLM_PROPOSED`; immutable cohort, sampling PRNG seed and protocol/scorer digest; allowed test budget; safety runtime; visibility ACL.
- `v04-mla-case-v1`: opaque fixed case ID; asset; candidate origin/model transcript SHA; semantic user job, claim+constraints, expected boundary, exact source path/blob anchors; fixed prior-to-outcome inclusion; no hidden-truth labels in P/LLM-B input.
- `v04-mla-challenge-v1`: challenger transcript SHA; target case ID; concrete falsification hypothesis; relevant source anchors; candidate fixture digest; no independently authoritative verdict field.
- `v04-mla-observation-v1`: case ID; exact Source/Target relation+digest; execution interface; fixture hash; signed/replayable receipt; raw output/side-effect/replay hash; independent deterministic oracle ID; observed verdict; runtime status, optional `BLOCKED` reason.
- `v04-mla-human-card-v1`: deterministic selection reason `STRATIFIED_SAMPLE` / `HIGH_IMPACT_UNRESOLVED`; evidence pointers; proposer/challenger/J conflicting excerpts; non-secret suggested decision; `CONFIRM/REJECT/DEFER`; review scope `SAMPLED`; reviewer decision timestamp. Human verdict cannot relabel model-generated reference as human-authored Gold.
- `v04-mla-terminal-v1`: all included case IDs and denominators, every outcome, evidence status tier, error families/false promotions, empirical budget, all human selection cards, missing gates and `PASS/FAIL/BLOCKED/PROVISIONAL` decision. Preserve both original and corrected claim identities.

**Private/public separation:** raw model prompts, oracle labels, decisive hidden fixtures, sensitive execution logs and any secret remain in sealed store. Git may hold only safe public manifests, model/config identifiers, redacted metrics, SHA256 commitments and closed-world metadata. An LLM-C/J cannot consume oracle-hidden fields or outcome labels before a candidate transcript freeze.

## Deterministic human selection contract

- Before P or LLM-B output: freeze campaign seed, asset strata and human-selection algorithm/version. After outputs, **four sample cards minimum: one per asset** across eligible accepted cases. Target **4–8 review cards**, **12 total maximum** including impactful unresolved exceptions. If no eligible case in an asset, do not fabricate a sample: mark coverage gap.
- Select required high-impact unresolved cases first (may exceed 12); then fill remaining slots using deterministic, seeded, non-replacement stratified sampling among otherwise eligible cases. Do **not** let a model choose the audit sample after seeing favorable outcomes. Sampled errors escalate to wider review within the 12-card cap; persistent errors block qualification.
- If required exceptions + sampled cards cannot fit, human unavailable, or `DEFER` remains unresolved, return `BLOCKED` for promotion/aggregate terminal, rather than silently auto-approving. H review may be zero on purely documentary dry-run but then its output is `PROVISIONAL`, not qualified.
- All human decisions must include exact evidence ref; reviewer authority is limited to acceptance of a cited, bounded conclusion, not claiming independent authorship of a whole reference corpus.

## Pilot, metrics and formal PASS boundary

**Pilot** (24 candidates, 6/asset) exists to calibrate cases, tools and budget; no official product SE10/SE11 pass/fail comparable to previous protocols. Report exact number of candidate references, source-verified vs behavior-verified cases, challenged supported/refuted/narrowed cases, leaked/missing evidence gates, human-reversed decisions, undecided cases and cost. Public `V04_MLA_PROVISIONAL` until model outputs and target execution validate the contract.

**Release-qualification study** needs an independently Fresh-reviewed, pre-run *frozen* cohort and threshold table. Proposed invariant hard gates (subject to such review): **0 unsupported Capability promotions**, **0 truth leakage**, **100% Git/target digest validity for scored cases**, **100% reviewed exception coverage**. Precision/recall/F1 against model-generated candidate references must be explicitly named **agreement metrics**, not independent-human-Gold precision/recall. Behavioral false promotion/refutation/narrowing claims must be supported by independent real-software oracle and frozen denominators; abstentions are counted, not dropped.

Any missing final real-target mapping, severe sampling bias, unbounded cost, correlated model-rater uncertainty without calibration, elevated audit error, inaccessible oracle or unverified outcome yields `BLOCKED` or `PROVISIONAL` rather than PASS. Independent fresh review must define quantitative soft thresholds and score handling **before running the evaluated cohort**. The original fixed SE10 and SE11 threshold matrices remain untouched and cannot be reused with changed ground-truth provenance without comparability evidence.

## Minimal implementation reuse and DAG

- T02 #149: reuse 76-source workpack from #157 and source pin code; build blind P/R/X capture + semantic source claim/challenge validator and candidate reducer; optional J + sampled human card interface.
- T03 #150: reuse target gaps from #158 and real trusted runner; freeze final mapping/deps/release applicability before real oracle; use typed observation/fixture receipts and prevent leakage; adapt 80-case benchmark only when true execution-based eligibility is available.
- T04 #151: issue a **new MLA-specific terminal**, distinguish original SE10/SE11 `NOT_RUN` from successor empirical outcomes, and retain SE12–SE16 `UNPROVEN` and formal Release `NO` absent separately satisfied criteria.
- One concern/PR: product authority/protocol → typed schema and reducer tests → role orchestration → bounded local execution + human exception cards → scored terminal. Keep local-agent delegation restricted to actual host binaries/sandbox/sealed evidence.

```text
OWNER_DESIGN_AUTHORIZED=YES
V04_MLA_PROTOCOL=CONTRACT_CANDIDATE_NOT_FROZEN
INDEPENDENT_FRESH_REVIEW=REQUIRED_BEFORE_EVALUATED_PASS
PILOT_24_CASES=NOT_RUN
FORMAL_EVALUATION=NOT_RUN
MODEL_CONSENSUS_AS_TRUTH=FORBIDDEN
HUMAN_DEFAULT_BUDGET=4_TO_8_CARDS_MAX_12
OLD_SE10_SE11_PROTOCOLS=IMMUTABLE_NOT_RUN
GENERAL_PRODUCT_RELEASE=NO
```
