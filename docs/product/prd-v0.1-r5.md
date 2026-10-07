# PRD v0.1-r5 — Executable Capability Evidence

Status: DRAFT_FOR_SUCCESSOR_ADVERSARIAL_REVIEW  
Project: app8  
Date: 2026-10-07  
Supersedes: PRD v0.1-r4  
Pinned standard: kaicreator-mm/ai-development-standard@7929012f36a2202dcc2edc7a414b8163adc7afbd (4.9.0)  
Product Freeze: NO  
L2 Ready: NO

## 1. Product thesis

app8 tests a narrow product thesis:

> Executable evidence about software behavior can add material value after a typed interface and a deterministic enforcement runtime already exist.

For the MVP security model, app8 adopts the strict interpretation:

> A security-required property may be admitted only when the property is ENFORCED by an adapter/runtime mechanism and app8 has executable evidence that the enforcer works for the bound Provider/invocation class.

Finite upstream observations never turn an infinite future input domain into a universal safety guarantee.

Executable Evidence therefore has three explicit value channels:

1. **Pre-execution exclusion and accountability** — a Provider/invocation already REFUTED by trusted evidence is denied before the enforcing runtime is asked to execute it.
2. **Enforcer-fit evidence** — app8 verifies that a Provider remains functional under the required sandbox/adapter policy and helps prevent over-broad allowlists or repeated runtime failures.
3. **Functional reliability evidence** — output schema, error semantics, cancellation, progress and other non-security behavior can be checked against a bounded contract.

The MVP does not claim that upstream observation alone proves arbitrary-input safety.

## 2. Security property classes

A policy property is classified before validation.

### 2.1 ENFORCEABLE_SECURITY

Examples:

- outbound network denied or restricted to an allowlist;
- filesystem writes restricted to declared mounts;
- process containment;
- protocol/demuxer/input-domain restrictions implemented by an adapter;
- credential/device availability restrictions.

Security-required ALLOW requires:

~~~text
ENFORCED guarantee
+
trusted enforcer-validity Evidence
~~~

### 2.2 OBSERVATIONAL_RELIABILITY

Examples:

- output schema;
- exit/error mapping;
- progress behavior;
- cancellation cleanup;
- metadata normalization.

These can be VERIFIED_IN_SCOPE but are never promoted into universal security guarantees.

### 2.3 NON_ENFORCEABLE_RESIDUAL_RISK

If a required behavior cannot be enforced in the MVP reference path, it cannot receive normal security ALLOW.

It may only use:

~~~text
ACCEPTED_RESIDUAL_RISK
~~~

which requires the same authorization class as UNVERIFIED_ESCAPE:

- explicit policy rule; or
- explicit human/operator approval.

It is never labeled verified-safe and is reported separately in experiments.

## 3. MVP product surface

The post-Freeze v0.1 MVP surface is:

- Provider-native Contract;
- Conformance Runner;
- CLOSED_SCOPE Evidence;
- local content-addressed Evidence/Refutation store;
- Admission;
- DecisionRecord-bound execution;
- replay/attestation;
- deterministic CLI.

Deferred:

- public Registry service;
- universal Capability ontology;
- provider ranking;
- automatic repo Analyzer;
- automatic adaptation/fork maintenance;
- marketplace;
- proprietary orchestration runtime.

MCP may be a projection/demo only.

## 4. Canonical model

~~~text
Software Artifact
  -> Provider Lineage
  -> Provider Identity
  -> Provider-native Contract
  -> Conformance Run
  -> Evidence Assertion
  -> Admission Decision
  -> DecisionRecord
  -> Bound Reference Execution
~~~

Cross-software Capability alignment is a Branching experiment, not a prerequisite.

## 5. Provider lineage and identity

### 5.1 ProviderLineage

ProviderLineage identifies the semantic family across rebuilds/revisions for purposes such as refutation ratcheting.

It includes:

- upstream project/source family;
- adapter semantic lineage;
- provider-native contract family.

Changing a digest alone does not automatically create a new lineage.

Starting a new lineage requires an explicit reviewed disposition explaining the semantic break.

### 5.2 ProviderIdentity

A ProviderIdentity binds:

- source repository/ref;
- build recipe/configuration digest;
- distribution channel/package identity;
- artifact digest;
- adapter digest;
- contract digest;
- invocation-template digest;
- configuration digest.

Any behavior-relevant component change creates a new identity and invalidates exact-identity Evidence matching, while lineage-level counterexamples may still ratchet forward.

## 6. Evidence assertion model

Claim provenance:

- UNKNOWN
- DECLARED
- DETECTED
- INFERRED

Observation verdict:

- UNTESTED
- VERIFIED_IN_SCOPE
- REFUTED_IN_SCOPE

Guarantee source:

- NONE
- UPSTREAM_OBSERVED
- ADAPTER_ENFORCED
- RUNTIME_ENFORCED
- COMPOSITE_ENFORCED

The dimensions are orthogonal.

A valid signature, static declaration or successful fixture run never upgrades UPSTREAM_OBSERVED into ENFORCED.

## 7. Scope classes

### DISCOVERED_SCOPE

Known relevant state is recorded but unknown observable state may remain.

Use:

- research;
- debugging;
- readiness reports.

It cannot support security-required ALLOW.

### CLOSED_SCOPE

CLOSED_SCOPE is established by eliminating, fixing, or schema-constraining observable state.

It does not require the system to guess every hidden variable.

## 8. Environment template and instance

r5 separates immutable execution policy from per-call bindings.

### 8.1 EnvironmentTemplate

The template digest binds:

- immutable base/rootfs image;
- sandbox/runtime policy;
- HOME/XDG/profile/plugin policy;
- sanitized environment schema;
- mount layout and permission schema;
- network/egress policy;
- process containment policy;
- locale/timezone policy;
- clock policy class;
- CPU feature/microarchitecture class;
- kernel/runtime class;
- visible /proc and /sys policy;
- hostname policy;
- resource-limit schema;
- filesystem semantic class where relevant.

### 8.2 InstanceBindings

Each execution records values allowed to vary by the template, for example:

- one read-only content-addressed input at /in;
- one fresh writable output directory at /out;
- declared secrets/credentials handles;
- real-time clock value under a `realtime` clock-policy class;
- resource-limit values within declared bounds.

Admission matches the template and validates that instance bindings satisfy the template schema.

A time-dependent upstream observation does not become a security guarantee merely because the clock value was recorded.

## 9. Input binding and parser differential

Verified execution uses immutable content-addressed objects.

Before Admission/execution:

1. direct input content is copied into the content-addressed store;
2. `input_content_digest` is recorded;
3. indirect references are either forbidden or recursively copy-in to a dependency-closure manifest with its own digest;
4. Provider artifact and adapter are executed from content-addressed immutable objects;
5. input-domain guard output is encoded into the invocation so the Provider is forced to use the same interpretation where the tool permits it.

Example mechanisms include a fixed demuxer, protocol allowlist or explicit parser mode.

The input-domain guard is an ADAPTER_ENFORCED component and is subject to the same suite-sensitivity testing as other enforcers, including polyglot/differential cases.

The claim is deliberately bounded:

> The reference path closes check/use substitution for the content-addressed objects bound into the DecisionRecord. It does not claim to solve arbitrary external TOCTOU outside that path.

## 10. VERIFIED_IN_SCOPE / REFUTED_IN_SCOPE

VERIFIED_IN_SCOPE means only:

> No contradiction was observed for the exact Provider identity, Contract, fixture/input scope, invocation, EnvironmentTemplate + valid InstanceBindings, repetition policy and observation boundary.

Evidence records:

- fixture set digest;
- input-domain descriptor/version;
- runs_per_fixture;
- input/dependency digests;
- invocation digest;
- environment template digest;
- instance-binding schema/version;
- harness digest;
- observation method/boundary;
- verdict;
- guarantee source.

For known stochastic/racy properties, the Contract defines a minimum repetition policy.

Any valid counterexample yields REFUTED_IN_SCOPE.

## 11. REFUTED dominance and ratchet

Time ordering is not the dominance rule.

A trusted REFUTED assertion dominates every VERIFIED assertion whose proposed scope overlaps the counterexample.

Deterministic overlap rule:

~~~text
overlap(refutation r, candidate scope s) :=
    guard_s.accepts(r.counterexample_fixture)
    AND environment_compatible(r, s)
    AND invocation_compatible(r, s)
~~~

If the new deterministic guard legitimately excludes the counterexample from its input domain, the new scope does not overlap and may recover.

### Counterexample ratchet

Every trusted REFUTED counterexample fixture is automatically added to the minimum required suite lineage for descendants of the same ProviderLineage.

A new ProviderIdentity must re-test all still-active lineage counterexamples it accepts.

### Refutation retirement

`REFUTATION_RETIRED` is allowed only through a trusted first-party review with one of these reasons:

- harness defect;
- fixture invalid;
- fixture outside the declared domain.

Retirement records the old refutation, justification, reviewer identity and successor evidence. It never deletes history.

### Untrusted external refutation

A non-trusted but replayable external refutation creates:

~~~text
UNKNOWN: REFUTATION_PENDING_REPLAY
~~~

for overlapping security Admission until the consumer replays or explicitly rejects the report through an audited disposition.

## 12. Admission

~~~text
Admission(
  provider,
  contract,
  policy,
  trusted_evidence_store,
  execution_context
) -> PASS | FAIL | BLOCKED
~~~

This function returns a decision record, not a standard development Gate. To avoid terminology collision, its business decision field is:

~~~text
decision = ALLOW | DENY | UNKNOWN
~~~

Mapping:

- ALLOW -> admission evaluation PASS;
- DENY -> admission evaluation FAIL;
- UNKNOWN -> admission evaluation BLOCKED.

For security-required policy:

- UNKNOWN never executes on the verified path;
- UPSTREAM_OBSERVED alone is never enough;
- required properties need ENFORCED guarantees and trusted enforcer-validity Evidence.

## 13. ExecutionContext and DecisionRecord

ExecutionContext includes:

- ProviderIdentity digest;
- Contract version/digest;
- EnvironmentTemplate digest;
- validated InstanceBindings digest;
- invocation digest;
- input descriptor;
- input content digest;
- dependency-closure digest when applicable;
- policy version.

ALLOW produces a DecisionRecord that additionally binds:

- trusted Evidence-set digest;
- suite-lineage minimum;
- refutation index version;
- attestation/trust-policy version;
- admission decision digest.

Reference execution consumes the immutable objects identified by that DecisionRecord.

Any mismatch yields:

~~~text
decision = DENY
reason = DECISION_BINDING_MISMATCH
~~~

## 14. UNVERIFIED_ESCAPE and residual risk

An Agent cannot self-authorize UNVERIFIED_ESCAPE or ACCEPTED_RESIDUAL_RISK.

Authorization source must be:

- policy; or
- explicit human/operator approval.

Policy may disable both.

All unsafe/refuted executions that happen through these paths still count as unsafe/refuted executions in experiments and are separately reported.

The verified path never silently falls back.

## 15. Threat model

| Adversary / failure source | MVP stance | Primary mechanism |
|---|---|---|
| Careless publisher / stale declaration | IN SCOPE | conformance, REFUTED ratchet, Admission |
| Malicious or compromised Provider | PARTIALLY IN SCOPE | enforcement sandbox, private/seeded held-out fixtures; no claim that public finite fixtures prove arbitrary semantics |
| Test-aware Provider | PARTIALLY IN SCOPE | private held-out fixtures or per-run generated fixtures with recorded seed; ENFORCED properties remain primary security boundary |
| Malicious input author | IN SCOPE for enforceable boundaries | content-addressed copy-in, deterministic guard, enforced invocation, sandbox |
| Prompt-injected Agent | IN SCOPE for bypass attempts | no self-authorized escape, Admission-controlled verified tool surface |
| Malicious publisher-signed Evidence | IN SCOPE | publisher signatures cannot authorize security ALLOW; consumer replay required |
| Compromised first-party runner/trust root | OUT OF SCOPE for MVP | explicitly assumed trusted; later hardening may use neutral/remote attestation |
| Malicious first-party insider with trust-policy authority | OUT OF SCOPE for MVP | organizational governance problem, not claimed solved |

Security conformance fixtures used against malicious/test-aware Providers must include a private held-out or per-run generated subset not disclosed to the Provider in advance.

## 16. L1 lifecycle before Product Freeze

Product Freeze must not depend on implementing the Technical MVP.

Before Freeze, only bounded Product Evidence activities are allowed.

L1 pre-Freeze gates:

- L1-CAL — prevalence measurement calibration;
- L1-PREV — false-safe/stale declaration prevalence viability;
- L1-ADOPT — adoption/customer evidence;
- L1-REVIEW — successor adversarial PRD review.

Any executable L1 research must be authorized by a separate Research/Evidence Issue with:

- exact hypothesis;
- allowed prototype code/scripts;
- prohibited productionization;
- exact dataset/sampling protocol;
- What Was NOT Proven;
- cleanup/retention disposition.

No L1 research artifact becomes production architecture by implication.

## 17. L1-CAL — measurement calibration

Before prevalence can kill or support the thesis, the bounded detector is calibrated on planted-positive cases.

Protocol is preregistered in GitHub before execution.

Minimum calibration set:

- 40 known false-safe claims/cases;
- independently authored or sourced subset >= 50%;
- categories include filesystem, network, process/side-effect and at least one structured-output/reliability mismatch.

PASS requires:

- all materially false-safe planted positives detected; and
- Wilson 95% lower bound for sensitivity >= 90%.

If calibration fails:

~~~text
L1-CAL = FAIL
~~~

Prevalence cannot issue a low-prevalence kill using an uncalibrated detector.

## 18. L1-PREV — problem prevalence

Purpose:

> Measure whether false-safe/stale declarations are common enough in the target tool population to justify continued product investment.

It is Product Evidence, not the effect size used by the later C-vs-D experiment.

### Sampling

Before inspection, a GitHub preregistration freezes:

- target population;
- catalog snapshot(s);
- eligibility/exclusion rules;
- claim types;
- materiality taxonomy;
- sampling weights;
- primary estimator;
- threshold T = 5%;
- maximum sample budget.

Primary statistic counts only **material false-safe** declarations.

False-unsafe/overly conservative declarations are reported separately.

Results are reported:

- per-claim;
- per-tool;
- uniform/unweighted;
- usage-weighted or target-population weighted when valid weights exist.

UNKNOWN/unverifiable claims are not silently removed; best-case and worst-case bounds are both reported.

### Sample size and three-way outcome

Initial eligible sample:

~~~text
n >= 80 tools
~~~

This permits a zero-event Wilson upper bound below 5%.

The gate uses only standard statuses:

- **PASS**: primary estimator's 95% lower bound >= 5%;
- **FAIL**: primary estimator's 95% upper bound < 5%;
- **BLOCKED**: interval straddles 5%.

One preregistered expansion is allowed, to a maximum of:

~~~text
n = 160 tools
~~~

If the expanded study still straddles 5%:

~~~text
L1-PREV = FAIL
reason = PROBLEM_EVIDENCE_NOT_DEMONSTRATED
~~~

A new study version cannot erase the earlier negative result. All versions remain reported, and rerunning after a negative result requires independent review approval with a stated reason.

## 19. L1-ADOPT

The discovery cohort is fixed before interviews:

- exactly 5 participants;
- at least two stakeholder classes.

PASS requires at least 3/5 participants to provide both:

1. a concrete recurring current problem involving tool admission, behavioral verification or upgrade compatibility; and
2. a concrete pilot commitment.

A pilot commitment means at least one of:

- named pilot + scheduled evaluation window;
- representative Provider/tool dataset;
- test environment;
- committed engineering/security review time.

General interest is insufficient.

Protocol changes create a new study version and never overwrite prior evidence.

## 20. L1-REVIEW

The Product Freeze review must use a context-fresh Independent Reviewer:

- reviewer did not author r5;
- reviewer operator_id/session_ref differs from author context;
- for this gate, reviewer must not have participated in prior app8 PRD authoring/review sessions;
- GitHub durable state is the only fact source.

Gate uses standard statuses only.

PASS requires:

~~~text
P0 = 0
AND
(P1 = 0 OR every P1 has an explicit independently accepted defer disposition)
~~~

## 21. Product Freeze

Product Freeze requires:

- L1-CAL = PASS;
- L1-PREV = PASS;
- L1-ADOPT = PASS;
- L1-REVIEW = PASS;
- pinned standard remains valid/current for the project's chosen baseline or is explicitly migrated through reviewed durable state.

After Freeze:

~~~text
Product Freeze -> L2 Architecture -> Task DAG -> Implementation / Technical MVP
~~~

Technical MVP gates do not block Product Freeze because they require architecture and implementation.

## 22. Post-Freeze v0.1 technical gates

After L2 and implementation, the v0.1 candidate must satisfy:

- T1 Admission Correctness;
- T2 Evidence Incremental Value Agent Experiment;
- T3 CLOSED_SCOPE / Falsifiability / Bound Execution;
- T4 Blind Suite Sensitivity;
- T5 Independent/Heterogeneous Replay;
- T6 Attestation Trust.

All are required release gates for the security-admission claim.

Gate states are only:

~~~text
PASS / FAIL / BLOCKED / NOT_RUN / NOT_APPLICABLE
~~~

If T3/T4/T6 FAIL, the security-admission v0.1 claim fails. A non-security observability/research pivot requires a successor PRD; it is not an automatic partial PASS.

## 23. T1 — Admission Correctness

T1 is a deterministic contract/gate test, not product-value evidence.

Cases include:

- trusted VERIFIED evidence;
- trusted REFUTED evidence;
- scope mismatch;
- environment mismatch;
- input-domain mismatch;
- content-digest mismatch;
- stale suite lineage;
- untrusted attestation;
- missing declaration/evidence;
- dominating refutation;
- pending external refutation;
- unauthorized escape;
- DecisionRecord mismatch.

At least half of frozen gate cases are authored by an Independent Reviewer after the Admission contract is frozen.

T1 PASS requires 100% expected decisions.

## 24. T2 — Evidence incremental value

Four arms share the same Provider, wrapper, policy and **same enforcing runtime**.

A — Raw: docs + shell.  
B — Typed: narrow wrapper.  
C — Static Admission: same wrapper + same enforcer + static/publisher declarations.  
D — Evidence Admission: same wrapper + same enforcer + executable Evidence.

In C and D:

- the Agent has no raw shell/direct Provider bypass on the measured verified path;
- any unauthorized bypass attempt is counted as a violation;
- same enforcement policy is active in both arms.

The C-vs-D difference is Evidence-informed pre-execution knowledge, not the presence of sandbox enforcement.

### Primary strata

The experiment does not manufacture a single blended effect by choosing an arbitrary false-declaration ratio.

It reports separately:

1. **REFUTED/stale stratum** — cases with externally established refutation/currentness failure;
2. **benign-valid stratum** — Provider/invocation known to satisfy the enforced path;
3. **functional-reliability stratum** — output/error/cancel regressions.

Primary Evidence metrics:

- pre-execution detection rate of trusted REFUTED/stale attempts;
- contained-violation attempts that reached the enforcer;
- benign availability / false denial;
- functional task success/reliability.

The observed L1-PREV rate is used only to estimate expected population impact after conditional effects are measured; it does not determine the conditional gate result.

### Statistical plan

Before episodes, GitHub preregistration freezes:

- models;
- tasks/strata;
- power analysis;
- alpha 0.05;
- power >= 0.80;
- task-level clustering method;
- model stratification;
- minimum meaningful effect;
- non-inferiority margin;
- maximum budget;
- at most one sample expansion rule.

Episodes within one task are not treated as IID.

Primary effect thresholds use confidence bounds, not point estimates.

After the one allowed expansion, insufficient evidence maps to:

~~~text
T2 = FAIL
reason = INCREMENTAL_VALUE_NOT_DEMONSTRATED
~~~

No optional stopping through study re-versioning can overwrite that result.

## 25. T3 — CLOSED_SCOPE / falsifiability / execution binding

T3 must demonstrate:

- incorrect safety claim -> REFUTED_IN_SCOPE;
- overlapping REFUTED -> pre-execution DENY;
- unknown host state cannot affect a matching CLOSED_SCOPE execution;
- input-domain mismatch cannot ALLOW;
- immutable input/artifact/adapter objects prevent substitution after Admission;
- guard/provider interpretation is forced or mismatch blocks;
- DecisionRecord mismatch blocks execution;
- contained execution cleanup leaves no descendant process.

At least 10 hidden-state perturbations are used; at least 5 are selected by an Independent Reviewer after the scope design freezes and are not limited to the implementation checklist.

Any silent behavior change while prior evidence still matches causes T3 FAIL.

## 26. T4 — suite sensitivity

T4 uses:

- visible development mutation set;
- blind held-out set.

Independence requires:

- different reviewer/person or separate agent instance;
- no access to frozen suite source while constructing held-out cases;
- held-out identities hash-committed before unblinding.

At least half of held-out cases come from historical real regressions, behavior changes, CVEs/advisories or real old/new release pairs.

The remainder may be synthetic conditional mutations.

Sample size is selected by a preregistered precision target, not a fixed 5-case minimum.

Any safety-critical held-out miss causes T4 FAIL.

Detection rate and confidence interval are reported.

## 27. T5 — independent / heterogeneous replay

Single-host repetition proves repeatability only.

T5 uses a second clean runner.

Within the same declared EnvironmentTemplate class, the second runner must differ in actual member values for at least:

- CPU vendor/generation/feature realization;
- kernel version;
- controlled clock realization/offset.

A template cannot satisfy heterogeneity merely by pinning the entire machine identity to one exact host.

If an exact member is truly required, that limitation is part of the Provider's compatibility claim and heterogeneous reproducibility for that dimension is NOT_APPLICABLE only through explicit reviewed disposition.

## 28. T6 — attestation trust

MVP trust is FIRST_PARTY / consumer-replayed.

PASS requires:

- Evidence bundle digest matches;
- signature verifies;
- signer/runner identity matches first-party trust policy;
- run originated from consumer-controlled or separately trusted neutral runner;
- trust-policy version recorded;
- replay recipe present;
- no revocation/currentness failure.

Publisher signature alone never authorizes security ALLOW.

## 29. Threat-aware fixture policy

Security fixtures are:

- versioned;
- content-addressed;
- provenance/licensing/privacy recorded;
- partly private held-out or per-run generated for test-aware Provider resistance.

Generated fixture seed is recorded after execution for replay but need not be disclosed before the run.

Real user media/pcap/documents do not enter default corpora without explicit provenance/privacy disposition.

## 30. Performance / positioning branch

Performance is a Branching gate for interactive-Agent positioning, not for the existence of CI/governance value.

Measured overhead includes:

- input hashing/copy-in;
- guard classification;
- Admission;
- revocation/refutation-index lookup;
- environment preparation;
- execution-wrapper overhead.

Initial interactive targets:

- local Admission p95 <= 50 ms using a pinned local revocation snapshot;
- for raw tasks <= 1 s, added warm-path p95 overhead <= 250 ms;
- for raw tasks > 1 s and <= 5 s, median added overhead <= 20%;
- for raw tasks > 5 s, median added overhead <= 15%.

If these fail, app8 may continue as CI/governance infrastructure but cannot claim an interactive Agent path until a successor positioning review passes.

## 31. Cross-provider alignment branch

Provider-native contracts remain canonical.

Cross-provider semantic alignment is optional and tested only after v0.1 core evidence mechanics exist.

Before alignment, freeze:

- benchmark tasks;
- required semantic dimensions;
- dimension weights;
- fidelity requirements such as unit, precision, nullability, enum normalization and error-category fidelity.

A Universal Capability layer is rejected if required semantic fidelity cannot be preserved without lowest-common-denominator degradation.

## 32. Upgrade / stale-declaration branch

At least one major-version boundary is studied post-Freeze.

Outcomes are recorded as evidence, not forced into PASS semantics:

- NO_DRIFT_OBSERVED;
- DRIFT_DETECTED;
- EVIDENCE_REFUTED;
- ADAPTER_REVISION_REQUIRED;
- CONTRACT_REVISION_REQUIRED.

For development Gate mapping:

- successful execution of the planned study -> PASS;
- study cannot execute -> BLOCKED;
- study protocol invalid -> FAIL.

The observations contribute to compatibility-corpus and stale-declaration evidence.

For later representative portfolio data, automatic/scalable adaptation is rejected if >50% of sampled Provider major upgrades require contract semantic redesign or changes to >25% of adapter behavioral paths.

## 33. Local Evidence / Refutation store

MVP storage is content-addressed local files/indexes only.

Required indexes:

- identity -> evidence;
- lineage -> active counterexamples;
- suite-lineage minimum;
- pending external refutations;
- retired refutations;
- revocation/currentness metadata.

This is not a public Registry service.

## 34. Pre-registration and study governance

Every gate-bearing experiment is preregistered as a GitHub commit and/or Issue before data collection.

The preregistration records:

- protocol version;
- dataset/catalog snapshot;
- sampling/fixtures;
- metrics;
- thresholds;
- statistical plan;
- maximum budget;
- allowed expansion;
- independent reviewer identity requirement.

Negative results remain durable.

A successor study version:

- cannot delete or supersede a negative result;
- must report all prior versions;
- requires independent reviewer approval for rerun;
- must state the new information that justifies another study.

## 35. Independent Reviewer definition

For gate-bearing independent work:

- operator/context differs from the Builder/author;
- operator_id and session_ref are recorded;
- reviewer does not modify the reviewed artifact;
- exact reviewed SHA/blob is recorded.

For L1-REVIEW specifically, the context must also be fresh to app8 PRD history: no prior participation in r1-r5 authoring or review.

## 36. Gate state mapping

Only standard Gate states are used.

| Situation | Gate state |
|---|---|
| Required evidence meets frozen criterion | PASS |
| Evidence demonstrates criterion is not met / max study budget exhausted without demonstration | FAIL |
| Required evidence cannot yet be obtained but an authorized bounded next attempt remains | BLOCKED |
| Work not started | NOT_RUN |
| Gate explicitly does not apply under an accepted product branch | NOT_APPLICABLE |

Business-domain outcomes such as ALLOW/DENY/UNKNOWN or DRIFT_DETECTED are fields inside evidence/results, not Gate states.

## 37. Adoption and commercial boundary

Technical feasibility does not imply commercial product viability.

If L1-ADOPT FAILS, Product Freeze does not occur.

A research/OSS prototype may continue only under a new explicitly non-product disposition; it cannot silently advance to product L2.

## 38. Product boundary

app8 answers:

- What bounded executable evidence exists?
- What scope does it cover?
- What mechanism enforces the security property?
- Has that enforcer been tested against this Provider/invocation class?
- Is this exact immutable invocation admissible under policy?

Agent/Harness answers:

- What goal should be pursued?
- Which admissible Provider should be selected?

Execution runtime answers:

- How is the enforced environment instantiated?

app8 may integrate a reference runtime but does not depend on RunX, domain-harness or a specific Agent framework.

## 39. What r5 explicitly does not prove

This PRD revision does not prove:

- false-safe prevalence is >= 5%;
- customers will adopt app8;
- the reference enforcer is implementable with acceptable overhead;
- executable Evidence materially improves Agent outcomes;
- universal Capability abstraction is viable;
- third-party Evidence can be trusted without consumer replay;
- arbitrary software can be adapted automatically.

Those are controlled future evidence/gate questions.

## 40. Current terminal

~~~text
PRD_REVISION = v0.1-r5

PREDECESSOR_REVIEW_r4 = FAIL
P0_r4 = 1
P1_r4 = 8
P2_r4 = 7
P3_r4 = 1

PRODUCT_DIRECTION = CONDITIONAL_GO
PRODUCT_FREEZE = NO
L2_READY = NO

NEXT =
SUCCESSOR_ADVERSARIAL_REVIEW_r5
~~~

## 41. r5 successor-review attack targets

The context-fresh reviewer should attack at least:

1. Is the Evidence value proposition coherent when C and D use the same enforcing runtime?
2. Does L1-PREV now have a mathematically reachable PASS/FAIL/BLOCKED rule without optional stopping?
3. Can REFUTED ratcheting be bypassed through identity changes, scope narrowing or retirement?
4. Are content-addressed input/dependency closure + forced guard interpretation sufficient for the reference path's bounded TOCTOU claim?
5. Does EnvironmentTemplate + InstanceBindings remove the template/instance ambiguity?
6. Is the threat model explicit enough about malicious/test-aware Providers and trusted-runner assumptions?
7. Is the L1 Freeze lifecycle now compatible with the pinned development standard?
8. Are all experiment/Gate states mapped to the standard enum?
9. Is the interactive performance branch measured on the short-call case rather than hidden by long tasks?
