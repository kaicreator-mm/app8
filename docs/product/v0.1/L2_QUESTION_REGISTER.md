# L2 Question Register — app8 v0.1

Status: DRAFT_FOR_INDEPENDENT_REVIEW  
Purpose: preserve architecture/security UNKNOWNs without forcing them into the L1 PRD.

## 1. Transfer rule

Every entry must pass the PRD L1→L2 Transfer Test.

An entry cannot be used to move a product-feasibility blocker out of L1.

The Product Reviewer must explicitly review the classification.

## 2. Status vocabulary

Question status:

- `L2_REQUIRED`
- `L1_BLOCKING`
- `RESOLVED_BY_PRODUCT_DECISION`

These are question classifications, not Gate states.

## 3. Register

### Q-L2-001 — Enforcement / sandbox trust boundary

Classification: L2_REQUIRED

Question:

> Which Linux enforcement composition provides the v0.1 reference isolation contract, and what exact threat boundary does it support?

Known at L1:

- the product requires a deterministic enforcement baseline;
- Linux provides multiple plausible isolation/control mechanisms;
- the PRD does not require one specific mechanism.

L2 must decide:

- process/filesystem/network containment mechanism;
- sandbox-escape/kernel-exploit assumption;
- required privileges;
- observable violation telemetry.

Why not L1-blocking:

- multiple plausible mechanisms can satisfy the same black-box product contract;
- failure of one mechanism causes architecture pivot, not product-claim invalidation.

### Q-L2-002 — Host realization / kernel capability binding

Classification: L2_REQUIRED

Question:

> How should evidence bind the actual kernel/CPU/enforcer capabilities of a runtime instance?

L2 must decide:

- host-realization identity;
- exact vs class-based compatibility;
- capability probes for relevant enforcement features;
- portability/revalidation rules.

### Q-L2-003 — Evidence environment template vs instance binding

Classification: L2_REQUIRED

Question:

> Which environment dimensions are immutable template facts and which are per-execution instance bindings?

L2 must define:

- template schema;
- instance schema;
- admissible variation;
- boundary sampling/revalidation rules.

### Q-L2-004 — Immutable input and decision/execution binding

Classification: L2_REQUIRED

Question:

> How are Provider artifact, adapter, direct input and indirect dependency closure made immutable across admission and execution?

L2 must decide:

- content-addressed object lifecycle;
- copy-in/dependency rules;
- decision record freshness/single-use semantics;
- revocation/refutation recheck before execution;
- parser/guard interpretation enforcement.

### Q-L2-005 — Refutation lineage / overlap semantics

Classification: L2_REQUIRED

Question:

> How should a counterexample propagate across Provider identities without permitting evidence shopping or permanent false poisoning?

L2 must define:

- Provider/source lineage identity;
- environment/invocation compatibility predicates;
- counterexample family/domain semantics;
- retirement authority;
- external refutation replay/disposition.

L1 requirement retained:

- the product must support negative evidence as first-class and it must affect admission/currentness.

The exact algebra is L2.

### Q-L2-006 — Evidence attestation and trust

Classification: L2_REQUIRED

Question:

> What attestation format, identity model and consumer-replay policy are used by v0.1?

L1 product constraint:

- third-party publisher signature alone cannot authorize security admission.

L2 chooses:

- attestation format;
- first-party runner identity;
- replay/trust-root mechanics;
- revocation/currentness representation.

### Q-L2-007 — Output trust propagation

Classification: L2_REQUIRED

Question:

> How does the Provider contract distinguish trusted control data from untrusted external content and prevent privilege/trust upgrading?

Product-level requirement:

- output derived from untrusted external content must not silently become trusted control/policy input.

L2 defines field semantics and adapter/runtime enforcement.

### Q-L2-008 — Process containment / cancellation

Classification: L2_REQUIRED

Question:

> How does the reference runner guarantee contained cancellation and cleanup?

L2 defines:

- containment primitive;
- timeout/cancel semantics;
- descendant enumeration;
- partial-output cleanup;
- evidence capture.

### Q-L2-009 — Performance architecture

Classification: L2_REQUIRED

Question:

> Can the verified path meet an interactive latency budget, and what warm/cold execution architecture is required?

L2 defines:

- pooling/reuse;
- hashing/copy-in strategy;
- evidence-index lookup;
- cold/warm path;
- measurement method.

Failure to meet interactive targets may branch positioning to CI/governance while retaining the core product, subject to Product Review.

## 4. Explicit non-transfer items

The following are L1_BLOCKING and must not be transferred to L2:

- whether materially false-safe/stale declarations exist at useful prevalence;
- whether the evidence pipeline can detect them with useful sensitivity/specificity;
- whether evidence changes decisions beyond static declarations under a fixed enforcement baseline;
- whether target users have pilot-level demand;
- whether the PRD's security promise is coherent.

## 5. Transfer audit

For Product Freeze, the Independent Product Reviewer must verify for every L2_REQUIRED entry:

- at least one plausible implementation path exists;
- the product contract remains stable across multiple plausible implementations;
- a negative result for one implementation does not invalidate the product claim;
- no open P0/P1 has been relabeled as L2_REQUIRED.

Any failed transfer test reclassifies the question as L1_BLOCKING and Product Freeze fails.


### Q-L2-010 — Hard-case adaptation distribution

Classification: L2_REQUIRED

Question:

> How often do valuable non-trivial software Providers require deeper-than-thin adaptation, and what adaptation levels remain economically acceptable?

L2 / later evidence must sample hard cases such as stateful/headless desktop-core software and classify adaptation cost without using a single easy CLI-heavy sample as proof of scalability.

This does not change the v0.1 Provider-native product claim; it constrains future automatic/scalable adaptation positioning.
