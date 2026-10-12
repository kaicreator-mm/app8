# SE11 Protocol — Falsification and Behavioral Evidence Quality

Status: DRAFT_FOR_FRESH_REVIEW
Execution: NOT_AUTHORIZED
Parent: Issue #25
Owning task: Issue #27
Product authority: main@908cee661f3747439bb0366b158903cb9b38b413
Pinned ADS: kaicreator-mm/ai-development-standard@7929012f36a2202dcc2edc7a414b8163adc7afbd

## 1. Falsifiable question

Can LLM-B create adversarial Evidence/Test Plans which, when executed against real software, distinguish supported Capability claims from false, overbroad or boundary-sensitive claims well enough to prevent unsupported promotion?

## 2. Study corpus

Use the same four frozen software revisions as SE10.

For each asset, an independent truth curator constructs 20 claims, for 80 total:

- 8 supported claims;
- 4 materially false claims;
- 4 overbroad/incomplete claims with a discoverable narrowing condition;
- 4 near-miss/boundary claims.

Claims must cover at least:

- normal success;
- invalid/unsupported inputs;
- important variants;
- material failure semantics;
- version/environment/binding constraints;
- side effect or state behavior where applicable.

The frozen truth ledger is hidden from LLM-B until scoring.

## 3. Inputs to LLM-B

LLM-B receives:

- the Capability Hypothesis/claim;
- permitted source provenance;
- target binding identity;
- available execution interface;
- test-resource budget.

It does not receive the hidden verdict or hidden decisive fixture.

LLM-B must produce a bounded plan containing positive probes and explicit falsification attempts, expected observable evidence, stop conditions and replay metadata.

## 4. Real-execution rule

Behavioral truth is determined by deterministic execution/observation on the pinned target software, not by LLM judgment.

Execution records must bind:

- software/build revision;
- executable/package identity;
- OS/runtime/environment;
- binding/interface;
- inputs/fixtures;
- command/call;
- stdout/stderr or equivalent;
- output artifacts/state changes;
- assertion result;
- replay instructions.

When the environment cannot execute a planned probe, the claim is BLOCKED rather than guessed.

## 5. Scoring

For each claim, evidence outcome is classified:

- SUPPORTED;
- REFUTED;
- NARROWED;
- BLOCKED;
- INCONCLUSIVE.

Primary metrics:

- false-promotion rate: false/overbroad claims incorrectly treated as fully supported;
- supported false-rejection rate;
- refutation sensitivity on materially false claims;
- narrowing sensitivity on overbroad claims;
- boundary-detection sensitivity;
- material-constraint discovery rate;
- evidence reproducibility rate.

A plan that merely exercises a happy path but fails to challenge an overbroad claim scores as a falsification miss.

## 6. Frozen PASS thresholds

PASS requires:

- false-promotion rate <= 0.05;
- supported false-rejection rate <= 0.15;
- refutation sensitivity >= 0.90;
- narrowing sensitivity >= 0.80;
- boundary-detection sensitivity >= 0.75;
- material-constraint discovery >= 0.80;
- reproducible decisive evidence >= 0.90 of non-BLOCKED claims;
- zero unsupported claim promoted solely from model prose or documentation assertion.

If >15% of claims are BLOCKED for environmental reasons, aggregate verdict is BLOCKED unless the blocked cases are independently shown to be outside the frozen supported environment.

## 7. Epistemic separation checks

The execution report must explicitly verify:

~~~text
LLM-A hypothesis != truth
LLM-B plan != truth
LLM-C prose != Evidence
REAL OBSERVATION = factual input
~~~

No model may score its own plan as ground truth.

## 8. Anti-cheating

Before LLM-B run, freeze:

- 80-claim corpus;
- hidden truth ledger;
- decisive fixtures;
- target versions/environments;
- plan budget;
- scoring code/rules;
- thresholds.

After outcome visibility, no threshold, claim-category or decisive-fixture mutation is allowed except an auditable erratum that does not erase the original.

## 9. Evidence outputs

Produce:

- frozen claim manifest;
- hidden truth commitment;
- generated Evidence Plans;
- raw execution logs/artifacts;
- replay manifest;
- revealed truth ledger;
- per-category confusion matrix;
- metrics;
- counterexamples;
- terminal PASS/FAIL/BLOCKED;
- What Was NOT Proven.

## 10. What this study cannot prove

SE11 does not prove Capability extraction quality, cross-projection consistency, Agent utility, semantic search value, portfolio coverage, user pull or legal/implementation sufficiency. Finite tests do not prove arbitrary-input or universal safety.

## 11. Protocol terminal

~~~text
SE11_PROTOCOL = READY_FOR_FRESH_REVIEW
SE11_EXECUTION = NOT_AUTHORIZED
PRODUCT_FREEZE = NO
L2_READY = NO
~~~
