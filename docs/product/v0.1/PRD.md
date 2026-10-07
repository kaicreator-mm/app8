# app8 Product PRD v0.1 — L1 Authority Decomposition

Status: DRAFT_FOR_INDEPENDENT_REVIEW  
Product Freeze: NO  
L2 Ready: NO  
Pinned standard: kaicreator-mm/ai-development-standard@7929012f36a2202dcc2edc7a414b8163adc7afbd (4.9.0)

## 1. Problem

Agents can already discover software, read documentation, call shell/CLI tools, use MCP servers and execute inside sandboxes.

The unresolved product problem is not invocation. It is whether an Agent or governing platform can know, before use, that a concrete software Provider behaves as claimed for a bounded purpose, and can detect when those claims have become false or stale.

The product opportunity is therefore:

> turn behavior claims about executable software into bounded, replayable evidence that can be consumed by admission/governance decisions.

## 2. Target users

Primary:

- Agent / tool-platform engineers who admit local or remote software into an Agent runtime;
- security / governance teams that need behavior verification and upgrade currentness;
- tool / MCP publishers that need repeatable conformance evidence.

Secondary:

- local/server Agent builders that want to reuse mature software without repeatedly reasoning over its full CLI/API surface.

## 3. Product claims

These claims are normative product-level claims. Their required L1 evidence is defined in `L1_EVIDENCE_INDEX.md`.

### PCL-001 — The declaration problem is material

In the target population, materially false-safe or stale software behavior declarations occur often enough that relying only on publisher/static declarations is a meaningful operational problem.

### PCL-002 — Executable evidence can detect a material share of that problem

A bounded conformance process can detect materially false-safe/stale behavior with useful sensitivity and specificity, rather than merely reproducing declarations.

### PCL-003 — Evidence adds decision value beyond a typed interface and fixed enforcement baseline

Given the same typed invocation surface and the same enforcement runtime, executable provider-behavior evidence can improve pre-execution admission/currentness decisions without unacceptable false denial or operational cost.

This claim does **not** require finite tests to prove arbitrary-input safety.

### PCL-004 — The product can remain Provider-native

The MVP does not depend on proving that all software can be mapped into one universal cross-provider Capability ontology. Provider-native contracts are sufficient for v0.1.

### PCL-005 — There is adoption pull

At least one target-user segment has a recurring current problem and is willing to invest real pilot time/data/environment access.

## 4. Product thesis

The v0.1 product thesis is:

> **Executable Conformance + Evidence + Admission** is useful as a governance layer for software Providers.

Security boundary:

- runtime/adapter enforcement supplies the actual security restriction;
- executable evidence verifies bounded Provider behavior/currentness and, where applicable, that the configured enforcer works for the tested Provider/invocation class;
- upstream observation alone never becomes a universal safety guarantee.

## 5. MVP black-box behavior

The v0.1 product, after Product Freeze and L2 design, is expected to expose these black-box behaviors:

1. describe a Provider-native contract;
2. run conformance checks against a concrete Provider identity;
3. emit scoped evidence with provenance and replay information;
4. record positive and negative evidence, including explicit refutation;
5. answer whether a requested Provider invocation is admissible under a policy;
6. fail closed when required evidence/currentness is missing;
7. preserve an auditable history across Provider/software updates.

The PRD intentionally does not define the internal sandbox, kernel binding, content-addressed store layout, attestation protocol, refutation algebra implementation or process containment mechanism. Those are L2 questions.

## 6. MVP non-goals

v0.1 does not require:

- a public Registry or marketplace;
- a universal Capability ontology;
- provider ranking/optimization;
- automatic arbitrary-repository conversion;
- automatic adapter generation;
- maintained downstream forks;
- proprietary orchestration runtime;
- GUI/computer-vision automation;
- proof that finite fixtures establish universal safety;
- trust in third-party evidence without consumer-side verification.

## 7. Product invariants

### INV-001 — Declaration is not evidence

A static/publisher claim cannot be represented as executable verification.

### INV-002 — Negative evidence is first-class

A reproducible counterexample must be representable and capable of affecting admission/currentness.

### INV-003 — Evidence is scoped

Evidence always has an explicit Provider identity, contract, input/fixture scope, environment/runtime context and observation boundary.

### INV-004 — Missing security evidence fails closed

The verified path does not silently downgrade to raw execution.

### INV-005 — Product claims and architecture questions are separate authorities

A question may be transferred to L2 only if it passes the L1→L2 Transfer Test in `L2_QUESTION_REGISTER.md`.

### INV-006 — P0/P1 cannot be deferred through Product Freeze

Under the pinned standard, Product Freeze requires zero unresolved valid P0 and zero unresolved valid P1.

### INV-007 — Untrusted output never silently becomes control authority

Provider output derived from untrusted external content must not be silently promoted into trusted control, policy or instruction semantics. The exact representation/enforcement mechanism is L2_REQUIRED.

## 8. L1 success / kill model

Product Freeze is allowed only if all required L1 claims have supporting evidence and no open P0/P1 remain.

### Product kill / pivot conditions

- **K1 — Problem prevalence not demonstrated:** PCL-001 fails.
- **K2 — Evidence detection not demonstrated:** PCL-002 fails.
- **K3 — Incremental decision value not demonstrated:** PCL-003 fails.
- **K4 — Adoption pull not demonstrated:** PCL-005 fails.

K1–K3 stop expansion of the security-admission product thesis. A narrower research/audit tool would require a successor PRD.

K4 blocks commercial Product Freeze; an explicitly non-product OSS/research continuation may be proposed separately.

PCL-004 is intentionally non-blocking with respect to universal abstraction: failure of cross-provider alignment leaves the Provider-native product intact.

## 9. Required L1 evidence

The authoritative claim→evidence mapping is `L1_EVIDENCE_INDEX.md`.

Required pre-Freeze studies:

- E00 — detector calibration;
- E01 — declaration/prevalence study;
- E02 — evidence decision-value study;
- E03 — adoption study;
- independent Product Review of the exact Freeze package.

Experiment protocols are separate immutable preregistrations and are not part of this PRD body.

## 10. L1→L2 Transfer Test

A question may be classified `L2_REQUIRED` only when all are true:

1. its answer does not change the target user, core problem, PCL-001..005, MVP black-box behavior, product-level safety promise, success criteria or kill criteria;
2. at least one technically plausible implementation path is known at L1;
3. multiple reasonable L2 solutions could satisfy the same product contract;
4. a negative answer for one candidate architecture would cause architecture pivot, not invalidate the product claim itself.

If a negative answer would make the MVP product claim false, the question is L1_BLOCKING and cannot be transferred.

The Product Reviewer must review every L2 transfer classification.

## 11. Product Freeze authority

Product Freeze applies to an exact package, not to this PRD alone.

The package contains:

- exact PRD blob;
- exact L1 Evidence Index blob;
- exact required protocol/result blobs;
- exact L2 Question Register blob;
- current review-finding aggregation;
- pinned development-standard revision.

`PRODUCT_FREEZE.md` only aggregates those authorities. It cannot redefine their content.

Any contradiction among package members makes Freeze FAIL.

## 12. Post-Freeze lifecycle

After Product Freeze:

~~~text
Product Freeze
  -> L2 Architecture Evidence
  -> Task DAG
  -> Implementation
  -> Technical Validation / Release Qualification
~~~

Post-Freeze technical work may validate or reject architecture choices, but may not silently change PCL-001..005 or the product-level invariants.

If L2 evidence proves a product claim impossible, Product Freeze must be reopened through a successor PRD.

## 13. Deferred L2 domains

The current L2 Question Register includes, at minimum:

- enforcement/sandbox trust boundary;
- host/kernel capability binding;
- evidence scope and runtime instance identity;
- immutable input / decision-execution binding;
- refutation lineage / overlap semantics;
- evidence attestation/trust;
- output trust propagation;
- process containment/cancellation;
- performance architecture;
- hard-case adaptation distribution.

These are not considered solved by this PRD.

## 14. Anti-metrics

The following do not prove product success:

- wrapper count;
- MCP server count;
- registry entry count;
- adapter LOC;
- fork count;
- raw upgrade survival without suite sensitivity;
- number of "VERIFIED" labels without scoped negative testing.

## 15. Current terminal

~~~text
PRODUCT_DIRECTION = CONDITIONAL_GO
PRD_AUTHORITY = docs/product/v0.1/PRD.md
PRODUCT_FREEZE = NO
L2_READY = NO

NEXT =
independent review of the decomposed L1 authority package
then execute required L1 evidence protocols if review permits
~~~
