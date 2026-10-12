# SE11 Protocol — Falsification and Behavioral Evidence Quality

Status: AMENDMENT_CANDIDATE_FOR_FRESH_REVIEW
Execution: HOLD_FOR_IDENTITY_AMENDMENT_REVIEW
Parent: Issue #25
Owning task: Issue #27
Product authority: main@908cee661f3747439bb0366b158903cb9b38b413
Pinned ADS: kaicreator-mm/ai-development-standard@7929012f36a2202dcc2edc7a414b8163adc7afbd

## 1. Falsifiable question

Can LLM-B create adversarial Evidence/Test Plans which, when executed against real software, distinguish supported Capability claims from false, overbroad or boundary-sensitive claims well enough to prevent unsupported promotion?

## 2. Study corpus and identity separation

Use the same four frozen **Knowledge Source identities** as SE10 for hypothesis/provenance construction.

SE11 does **not** require the real execution target to be a binary built from the same exact Git commit. Before hidden-truth construction, freeze a separate **Execution Target identity** for each asset and an explicit Source -> Execution mapping.

Required identities:

- `KNOWLEDGE_SOURCE`: the frozen SE10 source/docs snapshot used to form claims and provenance;
- `EXECUTION_TARGET`: the real software artifact against which behavioral truth is measured;
- `SOURCE_EXECUTION_MAPPING`: the reviewed relationship between those two identities.

Preferred Execution Target order:

1. official publisher release binary/installer/package;
2. official publisher package-registry artifact or container image;
3. publisher-recommended build with durable provenance and cryptographic identity;
4. reproducible source build only when no suitable official artifact exists, or when the claim is explicitly source-only / unreleased.

Every Execution Target must record exact version/build/package identity, cryptographic checksum or immutable digest, acquisition provenance, OS/runtime requirements, and release/tag/source mapping where the publisher exposes one.

When both Knowledge Source and Execution Target source commits/tags are known, also freeze their repository relation as `SAME`, `KNOWLEDGE_SOURCE_ANCESTOR`, `KNOWLEDGE_SOURCE_DESCENDANT`, `DIVERGED`, or `UNRESOLVED`.

A source-built artifact is therefore **not** the default requirement.

### 2.1 Mapping discipline

The mapping must be frozen before hidden truth or LLM-B planning and classify each asset as one of:

- `EXACT_SOURCE_BUILD`: execution artifact built from the frozen source commit;
- `OFFICIAL_RELEASE_MAPPED`: official release with an authoritative release/tag/source relationship;
- `OFFICIAL_RELEASE_VERSIONED`: official release identity is exact, but no authoritative commit-level mapping is published;
- `PUBLISHER_RECOMMENDED_BUILD`: non-publisher artifact explicitly recommended/linked by the publisher;
- `SOURCE_ONLY_REQUIRED`: claim depends on unreleased/source-only behavior and therefore requires an exact/reviewed source build.

Claims must be scoped to the frozen Execution Target. A Knowledge Source statement that is not shown to apply to that target version may not be silently treated as expected runtime truth. Version mismatch is a first-class constraint/negative case, not grounds for post-outcome target substitution.

If the relation is `DIVERGED` or `UNRESOLVED`, hidden-truth construction must establish target applicability **before LLM-B exposure** using release-specific publisher metadata/source/tag/help or deterministic execution evidence unavailable to LLM-B. Applicability determination is a **pre-freeze eligibility gate**, before selecting or labeling the fixed 80-claim corpus. The independent curator must construct the required 8/4/4/4 truth-class balance per asset entirely against the frozen Execution Target, not from unverifiable master-only claims.

After the 80 claims and target manifest are frozen, **no claim may be replaced or excluded**, even if a later applicability check fails. Such a claim retains its original corpus ID, stays in the all-80 denominator, is reported as BLOCKED/INCONCLUSIVE with independent adjudication and contributes to the protocol's environmental BLOCKED threshold where applicable. No post-outcome reclassification, denominator shrinkage or silent favorable substitution is allowed. Version/currentness findings must be preserved as failure/constraint evidence rather than attributed to LLM-B reasoning without support.

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

Behavioral truth is determined by deterministic execution/observation on the frozen **Execution Target**, not by LLM judgment and not by source-text assertion.

Execution records must bind:

- Knowledge Source identity;
- Execution Target version/build/package identity;
- Source -> Execution mapping class and provenance;
- executable/package checksum or immutable digest;
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
- Knowledge Source identities;
- Execution Target identities;
- Source -> Execution mapping classes/provenance and repository relation;
- target-applicability evidence/eligibility disposition where relation is DIVERGED/UNRESOLVED;
- target environments;
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
SE11_PROTOCOL = IDENTITY_AMENDMENT_CANDIDATE_FOR_FRESH_REVIEW
SE11_EXECUTION = HOLD_FOR_IDENTITY_AMENDMENT_REVIEW
PRODUCT_FREEZE = NO
L2_READY = NO
~~~
