# PRD v0.1-r4 — Executable Capability Evidence

Status: DRAFT_FOR_SUCCESSOR_ADVERSARIAL_REVIEW  
Project: app8  
Date: 2026-10-07  
Supersedes: PRD v0.1-r3  
Product Freeze: NO  
L2 Ready: NO

## 1. Product thesis

The project tests one proposition:

> Executable, falsifiable, replayable evidence about software behavior can provide material value beyond a typed wrapper plus static declarations/policy.

The MVP surface remains deliberately narrow:

- Provider-native contract
- Conformance runner
- CLOSED_SCOPE evidence
- Admission
- Replay / attestation
- Minimal local evidence store

The MVP does not require a universal capability registry, automatic analyzer, provider-ranking service, public marketplace, universal MCP generation, or maintained forks.

## 2. Canonical model

The canonical graph is:

~~~text
Software Artifact
  -> Provider
  -> Provider-native Contract
  -> Conformance Run
  -> Evidence Assertion
  -> Admission Decision
  -> Bound Execution Decision Record
~~~

Cross-software Capability alignment remains an experiment, not a prerequisite.

## 3. Provider identity

A Provider identity binds all behavior-relevant material:

- upstream source repository + source ref
- build recipe/configuration digest
- distribution channel/package identity
- artifact digest
- adapter digest
- contract digest
- invocation-template digest
- configuration digest

Changing any behavior-relevant component invalidates evidence matching for the old identity.

## 4. Evidence assertion model

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

These dimensions are orthogonal. A valid signature or a successful fixture run never upgrades an observed upstream property into an enforced guarantee.

## 5. Scope classes

Two scope classes exist:

### DISCOVERED_SCOPE

Known relevant state is recorded, but unknown observable state may remain.

DISCOVERED_SCOPE may be used for research/debugging. It cannot support security-required ALLOW.

### CLOSED_SCOPE

CLOSED_SCOPE is created by eliminating, fixing, or fingerprinting observable state rather than guessing which state matters.

A CLOSED_SCOPE reference environment must bind or prevent Provider access to:

- immutable rootfs/base-image digest
- explicit mount manifest
- HOME/XDG/config/profile/plugin state
- sanitized environment variables
- working directory
- network namespace and egress policy
- locale and timezone
- clock policy
- CPU feature/microarchitecture class
- kernel version/runtime identity
- visible /proc and /sys policy
- hostname policy
- CPU/memory/process/resource limits
- filesystem semantic class where relevant
- harness/runtime policy digest

Security-required evidence cannot rely on unbounded external network state. If network access is required, ALLOW must depend on a runtime-enforced egress contract such as a destination/protocol allowlist plus evidence that the enforcer works.

## 6. VERIFIED_IN_SCOPE

VERIFIED_IN_SCOPE means only:

> No contradiction was observed for the recorded assertion within the exact Provider identity, input domain, fixture corpus, invocation, CLOSED_SCOPE environment, repetition policy, and observation boundary.

It is never a universal statement about arbitrary future input.

Evidence records:

- fixture set digest
- input-domain descriptor/version
- runs_per_fixture
- invocation digest
- environment digest
- harness digest
- observation boundary and method
- assertion verdict
- guarantee source

For known stochastic/racy properties, the contract defines a minimum repetitions policy before VERIFIED_IN_SCOPE is permitted.

## 7. REFUTED dominance

REFUTED_IN_SCOPE is a first-class product result.

For a given Provider identity and policy-required suite lineage:

- any trusted REFUTED evidence dominates older VERIFIED evidence for the overlapping assertion/scope;
- callers cannot select an older bundle to hide a newer refutation;
- policy defines a minimum accepted suite/fixture lineage;
- Admission queries the local trusted evidence index, not only caller-supplied bundles.

The local store therefore contains a minimal content-addressed refutation/revocation index. This is not a public Registry service.

## 8. Execution context

Admission must bind to the actual invocation being authorized.

ExecutionContext contains at minimum:

- environment_digest
- input_descriptor
- invocation_digest
- provider_identity_digest
- requested contract version
- policy version

Input_descriptor is produced by a deterministic input-domain guard or runtime-enforced classifier.

If the requested input cannot be deterministically classified into an evidence-covered domain:

~~~text
UNKNOWN: INPUT_DOMAIN_UNDECIDABLE
~~~

## 9. Admission signature

Admission is:

~~~text
Admission(
  provider,
  contract,
  policy,
  trusted_evidence_set,
  execution_context
) -> ALLOW | DENY | UNKNOWN
~~~

Security-required ALLOW requires:

1. exact Provider identity match;
2. CLOSED_SCOPE environment match;
3. invocation match;
4. deterministic input-domain match;
5. required suite/fixture lineage satisfied;
6. no dominating trusted REFUTED assertion;
7. policy-required guarantees are ENFORCED;
8. evidence exists that the relevant enforcer works;
9. attestation trust policy passes;
10. no freshness/currentness mismatch.

UPSTREAM_OBSERVED alone is insufficient for security-required ALLOW on arbitrary runtime inputs.

Evidence proves that an adapter/runtime enforcer was tested; the enforcer supplies the runtime guarantee.

## 10. Decision/execute binding

ALLOW returns a DecisionRecord containing digests for:

- Provider identity
- artifact
- adapter
- invocation
- contract
- execution environment
- input descriptor
- evidence set
- policy
- decision

The runner must re-check these digests immediately before execution.

Any mismatch after Admission:

~~~text
EXECUTION_REJECTED: DECISION_BINDING_MISMATCH
~~~

This closes admit/exec TOCTOU within the reference verified path.

## 11. Fail-closed semantics

For security-required policy:

- ALLOW -> verified execution may proceed
- DENY -> execution blocked
- UNKNOWN -> execution blocked

UNKNOWN is never implicitly executable.

## 12. UNVERIFIED_ESCAPE

UNVERIFIED_ESCAPE is a separate path.

Authorization may be granted only by:

- explicit policy rule; or
- explicit human/operator authorization.

The Agent itself cannot self-authorize escape.

Policy may disable escape completely.

Any unsafe/refuted execution performed through escape still counts as an unsafe/refuted execution in E0 metrics and is reported separately.

The verified path never silently falls back to escape.

## 13. MVP trust model

The MVP trust model is FIRST_PARTY.

Security ALLOW accepts evidence only when it was generated or independently replayed under a runner controlled by the consuming organization.

Third-party publisher signatures are used only for:

- provenance;
- bundle integrity;
- identity binding.

A publisher signature does not prove the claimed run occurred honestly.

Third-party evidence cannot directly authorize security-required ALLOW unless it is replayed by the consumer or a separately trusted neutral runner. General third-party trust is Post-MVP.

## 14. E0-prevalence — first kill point

Before Agent A/B/C/D testing, measure whether false/stale declarations exist often enough for executable evidence to have plausible incremental value.

Sampling must be preregistered before inspection.

Initial study:

- snapshot one or more public third-party tool/MCP catalogs;
- randomly sample at least 30 eligible third-party tools/servers;
- select behavior claims that are actually declared by the publisher, such as read-only/destructive/open-world/documented side effects;
- run bounded conformance checks where technically feasible;
- report REFUTED rate and 95% confidence interval;
- separately record UNKNOWN/unverifiable claims instead of treating them as safe.

Sampling exclusions and claim-selection rules must be frozen before results are inspected.

### E0-prevalence kill rule

A prevalence threshold is preregistered before sampling.

Default initial threshold:

> If the upper bound of the 95% CI for materially false/stale security-relevant declarations is below 5%, executable Evidence has not demonstrated enough prevalence-based incremental value for the security-admission product thesis.

Disposition:

~~~text
PREVALENCE_TOO_LOW -> STOP_PLATFORM_EXPANSION
~~~

The threshold may only change in a new preregistered study version, never after observing results.

Major-version upgrade studies provide a second prevalence source for stale declarations and are reported separately.

## 15. Admission correctness test

The old E0a is renamed Admission Correctness.

It is a deterministic conformance/unit test of Admission, not product-value evidence.

It must include:

- trusted VERIFIED evidence;
- trusted REFUTED evidence;
- scope mismatch;
- environment mismatch;
- input-domain mismatch;
- stale suite lineage;
- untrusted signature;
- missing declaration/evidence;
- dominating refutation.

C and D use identical fail-closed handling for missing required information:

- static arm missing required declaration -> UNKNOWN
- evidence arm missing required evidence -> UNKNOWN

Admission Correctness must be 100% for the frozen cases before any E0 Agent experiment is meaningful.

## 16. E0 Agent experiment

Four arms:

A — Raw  
Agent + docs + shell.

B — Typed  
Agent + same narrow typed wrapper.

C — Static Admission  
Agent + same wrapper + same policy + Admission based on publisher/static declarations, no executable evidence.

D — Evidence Admission  
Agent + same wrapper + same policy + same Admission implementation + executable evidence.

Primary causal comparison:

~~~text
C vs D
~~~

The benchmark cannot choose its false-declaration prevalence arbitrarily.

Its case mix must either:

1. be sampled from the E0-prevalence population; or
2. be reweighted to the measured E0-prevalence distribution using a preregistered estimator.

Synthetic adversarial cases may test mechanism correctness but cannot determine real-world effect size.

## 17. E0 statistical plan

The exact sample size is not hard-coded before prevalence is measured.

After E0-prevalence, but before Agent episodes, a statistical analysis plan is frozen containing:

- expected prevalence from E0-prevalence;
- expected effect size;
- clustering assumptions;
- alpha = 0.05;
- target power >= 0.80;
- task/model stratification rule;
- task-level cluster-bootstrap or preregistered GLMM;
- required number of tasks and episodes.

Episodes from the same task are not treated as IID observations.

Primary safety comparison uses a confidence bound, not only a point estimate.

Evidence value PASS requires the 95% confidence interval for risk reduction to exclude the preregistered minimum meaningful effect threshold.

Benign-task success uses a preregistered non-inferiority test with margin 5 percentage points and sample size justified by the same power analysis.

Known-refuted execution rate is reported using the correct opportunity denominator.

### INCONCLUSIVE rule

At most one preregistered sample-size expansion is allowed.

The expansion rule and maximum N are fixed before the first Agent episode.

If the result remains INCONCLUSIVE after that expansion:

~~~text
E0 = NOT_DEMONSTRATED
PRODUCT_FREEZE = NO
~~~

No repeated optional stopping is permitted.

## 18. E0 blocking interpretation

E0 is a Blocking Gate composed of:

- Prevalence viability
- Admission Correctness
- Agent incremental-value test

Failure of prevalence or incremental value stops platform expansion.

Admission Correctness failure is an implementation/specification defect and must be repaired before the experiment; it cannot be counted as product-value failure.

## 19. E1 — CLOSED_SCOPE and falsifiability

E1 is Blocking.

It must demonstrate:

1. an incorrect safety claim becomes REFUTED_IN_SCOPE;
2. Admission blocks the refuted Provider;
3. host state outside CLOSED_SCOPE cannot silently alter behavior while old evidence still matches;
4. input-domain mismatch cannot obtain ALLOW;
5. decision/execute digest mismatch blocks execution.

At least half of hidden-state perturbations are selected by an independent reviewer after the scope design is frozen and are not limited to the implementation team's known-state checklist.

Any case where behavior changes because of state not represented or excluded by the environment identity while Admission still considers old evidence matching is E1 FAIL.

E1 failure invalidates the security-admission product thesis, not merely one assertion.

## 20. Heterogeneous replay

Single-host repetition demonstrates repeatability only.

Independent reproducibility requires a second clean runner that differs from the first in at least:

- CPU vendor or generation/feature set;
- kernel version; and
- controlled clock offset/policy.

The Provider and environment contract may intentionally constrain these dimensions. If they are constrained, the second runner must prove it reconstructed the declared constraints.

Verdict mismatch is recorded, investigated, and blocks reproducibility PASS until the scope/contract is corrected.

## 21. Contained execution

The reference Linux runner uses PID namespace and/or cgroup containment so all Provider descendants are enumerable and terminable.

Cancellation semantics are "contained execution cancellation", not generic process-tree cancellation.

Cancel/timeout:

- request graceful termination;
- wait configured grace period;
- terminate all remaining contained processes;
- verify contained process count = 0;
- record partial artifacts and temporary files.

## 22. E2 — cross-provider semantic alignment

E2 is a Branching Gate.

It does not block the Evidence product.

Provider-native contracts are canonical first.

Before alignment:

- freeze benchmark tasks;
- freeze required semantic dimensions;
- freeze dimension weights;
- freeze fidelity requirements for every dimension.

Fidelity includes where relevant:

- units;
- precision;
- nullability;
- enumeration normalization;
- error category fidelity;
- cardinality/ordering semantics.

Metrics:

- semantic retention >= 90% weighted;
- benchmark task coverage >= 80%;
- provider-extension-only tasks <= 20%;
- no required dimension may pass by reducing fidelity below its frozen requirement.

FAIL disposition:

~~~text
UNIVERSAL_CAPABILITY_ALIGNMENT = REJECTED
PROVIDER_NATIVE_EVIDENCE_PRODUCT = CONTINUES
~~~

Network access and side effects are evidence/policy assertions, not semantic output-retention dimensions.

## 23. E3 — suite sensitivity

E3 is Blocking for security admission.

The suite has:

- visible development mutation set;
- blind held-out validation set.

Blind-set independence requires:

- different reviewer/person or separate agent instance;
- no access to the frozen suite source while constructing held-out cases;
- mutation identities committed by hash before suite unblinding;
- commit-reveal after suite freeze.

At least half of the held-out set must be derived from historical real regressions, upstream behavior changes, security advisories/CVEs, or old/new release pairs rather than clean synthetic mutations.

The remaining cases may be synthetic conditional mutations.

Final sample size is determined by a preregistered precision target. Detection rate is reported with confidence intervals; "5/5" is not sufficient evidence.

All safety-critical held-out misses cause E3 FAIL.

## 24. Upgrade/Staleness validation

Upgrade/Staleness is a Branching Gate, not a Blocking Gate for the core Evidence product.

At least one major-version boundary is tested using the same initial contract/adapter/suite where possible.

Results may be:

- NO_DRIFT_OBSERVED
- DRIFT_DETECTED
- EVIDENCE_REFUTED
- ADAPTER_REVISION_REQUIRED
- CONTRACT_REVISION_REQUIRED

This experiment contributes to stale-declaration prevalence and the compatibility-corpus thesis.

If repeated major upgrades show substantial maintenance cost, the automatic/scalable adaptation thesis is rejected without invalidating the core Conformance Kit.

For future portfolio evidence, "maintenance explosion" means more than 50% of sampled Provider major upgrades require contract semantic redesign or changes to more than 25% of adapter behavioral paths.

One initial upgrade study is informational/branching and cannot alone trigger the portfolio-level threshold.

## 25. Attestation

Evidence bundles are content-addressed and may use DSSE/in-toto compatible attestations.

Attestation format is distinct from trust.

Technical MVP Attestation Trust PASS requires:

- signature verifies;
- Evidence bundle digest matches;
- signer/runner identity matches the configured first-party trust policy;
- run originated from the consumer-controlled or accepted neutral runner identity;
- trust-policy version is recorded;
- replay recipe is present;
- no revocation/currentness violation exists.

Publisher-only signatures cannot satisfy security ALLOW in MVP.

Attestation Trust is a Blocking Gate for the security-admission claim.

## 26. Output trust

Output schema fields may be labeled:

- CONTROL
- UNTRUSTED_EXTERNAL
- SECRET
- ARTIFACT

The product guarantees only:

1. the adapter preserves the declared trust class;
2. it does not upgrade UNTRUSTED_EXTERNAL to CONTROL;
3. conformance can test those properties.

The downstream Agent/Harness decides how untrusted content is placed into model context.

MVP does not claim that labeling alone prevents prompt injection.

## 27. Verified-path operational budget

Verified-path cost is a feasibility constraint.

The benchmark reports separately:

- Admission latency;
- environment setup/start latency;
- execution latency;
- replay-only overhead.

Initial feasibility budget for the Linux reference runner:

- Admission p95 <= 50 ms for local evidence;
- warm verified-environment preparation p95 <= 1 s;
- for tasks whose raw execution is >= 5 s, median verified-path overhead <= 15% excluding one-time evidence generation.

Cold-start results are reported but are not a Product Freeze blocker in r4.

If the warm-path budget fails, the product may continue as CI/governance infrastructure, but interactive-agent positioning is not allowed until resolved.

## 28. Fixture/benchmark governance

All gate-bearing corpora are:

- versioned;
- content-addressed;
- preregistered before measurement;
- immutable for a given result.

Each fixture records provenance, license, generator, privacy classification, expected behavior, and repetition policy.

Real user media/pcap/documents do not enter the default public corpus without explicit provenance and privacy disposition.

## 29. Gate taxonomy

### Blocking Gates

B0 — E0-prevalence viability  
B1 — E0 Admission Correctness  
B2 — E0 Agent Incremental Value  
B3 — E1 CLOSED_SCOPE/Falsifiability/Execution Binding  
B4 — E3 Blind Suite Sensitivity  
B5 — Independent/Heterogeneous Replay  
B6 — Attestation Trust

Any unresolved Blocking Gate prevents Technical MVP PASS.

### Branching Gates

R1 — E2 Cross-provider Alignment  
R2 — Upgrade/Staleness Validation  
R3 — Verified-path Performance Positioning

A Branching Gate changes product shape/claims but does not automatically kill the core Evidence product.

### Informational Probes

I1 — Hard-case adaptation probe  
I2 — deterministic Analyzer collectors  
I3 — future provider-distribution sampling

## 30. Technical MVP PASS

Technical MVP PASS requires:

- B0 PASS
- B1 PASS
- B2 PASS
- B3 PASS
- B4 PASS
- B5 PASS
- B6 PASS

Branching gates must have explicit dispositions but need not all PASS.

No implementation actor may self-certify overall closure.

An independent reviewer records the terminal.

## 31. Adoption evidence

Commercial evidence remains separate from Technical MVP.

The initial discovery cohort is fixed at exactly 5 participants before interviews begin and must cover at least two stakeholder classes:

- Agent/MCP platform;
- security/governance;
- tool/MCP publisher.

PASS requires at least 3 of 5 to provide both:

1. a concrete recurring current problem in tool admission, behavioral verification, or upgrade compatibility; and
2. a concrete pilot commitment.

Pilot commitment means at least one of:

- named pilot use case plus scheduled evaluation window;
- willingness to provide a representative tool/provider dataset;
- willingness to provide a test environment;
- committed engineering/security review time.

General interest is not a commitment.

If the cohort protocol changes, it becomes a new discovery version with a new preregistered threshold.

## 32. Product Freeze

Product Freeze requires:

- Technical MVP PASS;
- Adoption Evidence PASS;
- successor adversarial review terminal with P0 = 0;
- every P1 either closed or carrying an explicit accepted defer disposition;
- independent product reviewer acceptance recorded in GitHub durable state.

Technical feasibility alone cannot enter L2 product architecture.

## 33. Hard-case probe

A non-gating hard case, initially LibreOffice headless conversion or equivalent, estimates the distribution of:

- hidden profile/config state;
- lock/temp-file behavior;
- headless reliability;
- side-effect surface;
- adapter complexity.

It returns R0-R6 adaptation classification only.

R4-R6 are not added to MVP.

## 34. Analyzer / Registry / MCP

Analyzer remains deferred except for deterministic collectors needed by the runner.

The MVP local evidence store is content-addressed files plus indexes required for:

- lookup;
- refutation dominance;
- minimum-suite currentness;
- revocation.

It is not a public Registry service.

MCP is an optional projection/demo and has no independent business logic.

## 35. Kill criteria

K1 — Prevalence too low  
If B0 fails the preregistered prevalence threshold, stop platform expansion.

K2 — Evidence adds no incremental value  
If B2 fails after the one permitted preregistered expansion, stop platform expansion.

K3 — Closed scope or execution binding fails  
If B3 fails, stop the security-admission product thesis. A non-security observability/research pivot would require a new PRD.

K4 — False safety claim cannot be refuted  
If a preregistered false claim cannot produce REFUTED_IN_SCOPE and block execution, B3 fails.

K5 — Suite sensitivity inadequate  
Any safety-critical blind miss means evidence cannot support security admission until repaired and re-reviewed.

K6 — Capability over-abstraction  
E2 failure rejects the universal Capability layer only.

K7 — Adaptation maintenance explosion  
If later representative portfolio data crosses the >50% substantial-redesign threshold, reject scalable automatic adaptation as a core thesis.

## 36. Anti-metrics

Do not use these as success metrics:

- wrapper count
- MCP server count
- registry entry count
- adapter LOC
- fork count
- raw upgrade survival without suite sensitivity

## 37. Product boundary

app8 answers:

- What behavior has executable evidence?
- What exact scope does that evidence cover?
- Who/what enforces the guarantee?
- Is this exact invocation admissible under policy?

Agent/Harness answers:

- What goal should be pursued?
- Which admissible provider should be selected?

Execution runtime answers:

- Where/how is the process isolated and run?

app8 may integrate a reference runtime, but does not require RunX, domain-harness, or any specific Agent framework.

## 38. Current terminal

~~~text
PRD_REVISION = v0.1-r4
PREDECESSOR_REVIEW_r3 = FAIL
P0_r3 = 2
P1_r3 = 7
P2_r3 = 5

P0_r3 = ADDRESSED_IN_r4
P1_r3 = ADDRESSED_IN_r4
P2_r3 = ADDRESSED_OR_EXPLICITLY_DISPOSITIONED

PRODUCT_DIRECTION = CONDITIONAL_GO
PRODUCT_FREEZE = NO
L2_READY = NO

NEXT =
SUCCESSOR_ADVERSARIAL_REVIEW_r4
~~~

## 39. r4 successor-review attack targets

The next reviewer should attack at least:

1. Does E0-prevalence measure a real-world rate rather than a benchmark-manufactured effect?
2. Can third-party declaration selection/sampling still bias prevalence upward?
3. Does ExecutionContext + decision binding actually prevent domain/environment/TOCTOU bypass?
4. Is REFUTED dominance complete without accidentally turning every historical refutation into permanent denial?
5. Does first-party trust still leave a way to forge or replay misleading evidence?
6. Are task-clustered statistics and the preregistered power plan sufficient to prevent optional stopping?
7. Does CLOSED_SCOPE remain meaningful under CPU/kernel/time/resource differences?
8. Is the verified-path overhead compatible with the intended interactive-agent use case?
9. Are all Blocking/Branching/Informational gates now closure-complete?
