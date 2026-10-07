# L1 Evidence Index — app8 v0.1 Successor r2

Status: DRAFT_FOR_INDEPENDENT_REVIEW  
Authority: successor claim-to-evidence map for PRD.md

## 1. Purpose

This document defines what must be proven before successor Product Freeze.

It does not define production architecture.

Expanded comparator evidence is recorded in SE09_COMPARATOR_EVIDENCE.md.

## 2. Claim map

| Successor claim | Required evidence | Gate consequence |
|---|---|---|
| SPCL-001 Useful semantic capability extraction | SE10 | FAIL => SK1 |
| SPCL-002 Falsification/evidence validates or refutes hypotheses | SE11 + inherited E00 as method evidence only | FAIL => SK2 |
| SPCL-003 One Capability authority, many consumers | SE12 | FAIL => SK3 |
| SPCL-004 Agent utility | SE13 | FAIL => SK4 |
| SPCL-005 Capability search by intent | SE14 | FAIL => SK5 disposition |
| SPCL-006 Non-pixel exportability | SE15 | FAIL => SK6 / narrow supported classes |
| SPCL-007 Target-user capability-compilation pull | SE16 | FAIL => SK7 |
| Product/category differentiation and reuse boundary | SE09 | informs all claims; cannot substitute for execution evidence |

## 3. Inherited predecessor evidence

Predecessor E00 is retained:

~~~text
Issue #9 = PASS
E00 result blob = 9c4277b6fab4bdb89a94e688de3f438fc2f9ef85
~~~

It demonstrates a blinded commitment/reveal/scoring method and a bounded detector result on its frozen 160-case synthetic corpus.

It does not prove:

- successor Capability extraction quality;
- real-software behavioral validation;
- one-authority/multi-consumer consistency;
- Agent utility;
- Capability search quality;
- heterogeneous non-pixel exportability;
- successor adoption.

Therefore E00 is an inherited research asset, not a successor Gate PASS.

## 4. SE09 — Expanded market / comparator evidence

Authority:

~~~text
docs/product/v0.1-successor/SE09_COMPARATOR_EVIDENCE.md
~~~

Current research terminal:

~~~text
SE09_RESEARCH = COMPLETE
SE09_PROPOSED_VERDICT = PASS
FRESH_REVIEW_REQUIRED = YES

CATEGORY_VALIDATION = VERY_STRONG
DIRECT_COMPETITION = HIGH
FEATURE_DIFFERENTIATION = LOW
ARCHITECTURAL_DIFFERENTIATION = MEDIUM
UNIFIED_PRODUCT_GAP = MEDIUM
PRODUCT_DIRECTION = NARROW_AND_PROCEED
~~~

The expanded sweep includes strong current comparators across:

- GUI/App -> Agent CLI;
- Web/Electron -> CLI;
- docs/API/SDK -> Agent CLI;
- code/application -> MCP;
- library -> Fact/Skill;
- Skill utility evaluation;
- capability/backend routing.

SE09 rejects CLI/MCP/Skill generation or registry breadth as standalone app8 differentiation.

The proposed surviving Product distinction is:

~~~text
Evidence-backed Capability authority
+ adversarial falsification / behavioral evidence
+ one factual authority -> replaceable Agent consumers
~~~

SE09 remains subject to context-fresh Product review and therefore is not yet a Frozen PASS.

## 5. Required successor executable studies

### SE10 — Semantic Capability extraction quality

Purpose:

- test whether docs/tutorials/examples can be converted into user-meaningful Capability Hypotheses across heterogeneous software.

Protocol must freeze before evaluation:

- representative software/source classes;
- exact asset versions/snapshots;
- independent reference/gold Capability set;
- what counts as user-meaningful Capability;
- matching/adjudication procedure;
- precision/coverage metrics and PASS thresholds.

Minimum portfolio must cover at least four materially different source classes, including at least:

- a mature CLI/application;
- a library/SDK;
- an API/service or structured spec;
- an application whose useful capability is not exposed only as a trivial exported function list.

The study must penalize:

- hallucinated capabilities;
- low-level callable spam;
- loss of important user-meaningful capabilities;
- unsupported semantic merging.

### SE11 — Falsification / Evidence quality

Purpose:

- determine whether LLM-B adversarial Evidence/Test Plans plus real execution can confirm, narrow or refute Capability Hypotheses.

The protocol must include:

- positive claims;
- materially false/incomplete claims;
- near-miss/boundary claims;
- hidden or independently curated truth where feasible;
- real execution/observation;
- negative/refutation evidence;
- software/version/environment/binding identity;
- frozen scoring before reveal.

PASS thresholds must bound:

- false promotion of unsupported claims;
- false rejection of supported claims;
- failure to capture material constraints.

No LLM self-label may count as ground truth.

### SE12 — One authority, many consumers

Purpose:

- test whether one frozen Evidence-backed Capability can drive all required projections/consumers.

Required representative outputs:

- CLI;
- MCP;
- Skill;
- Agent/LLM docs;
- searchable metadata.

The study must verify:

- all consumers use the same frozen Capability/Evidence authority;
- no consumer re-analyzes source material to alter semantic truth;
- CLI and MCP execute the intended real-software behavior;
- Skill/docs preserve the same constraints/variants/errors;
- representation-specific metadata does not become semantic drift;
- unsupported projection is explicit rather than silently substituted.

Protocol must freeze an executable Capability/task set and consistency scoring before generation.

### SE13 — Agent utility

Purpose:

- compare Agents using raw software documentation/native interfaces with Agents using app8 Capability projections.

Use paired/blinded task design where practical.

Freeze:

- Agent/model/version;
- tool/runtime access;
- context and execution budget;
- representative tasks;
- success scorer;
- primary utility metric;
- secondary metrics such as tool-selection errors, glue-code creation, retries, time and tokens.

Existing OSS evaluation systems may be reused/harvested. Reuse does not waive exact experimental identity.

### SE14 — Capability search quality

Purpose:

- test semantic retrieval over Evidence-backed Capability Metadata.

Freeze:

- a Capability index;
- natural-language intent queries;
- relevance judgments;
- ranking metric(s);
- readiness/currentness display checks.

Search must never represent DISCOVERED/HYPOTHESIZED-only material as EXPORT_READY.

### SE15 — Non-pixel exportability

Purpose:

- measure how much useful software capability can be bound while obeying:

~~~text
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
~~~

Allowed routes include:

- native API/SDK/library;
- native CLI/headless;
- IPC/protocol/RPC;
- source/binary analysis;
- minimal forks/adapters;
- structured semantic UI automation/accessibility interfaces.

Protocol must freeze a representative asset portfolio and top-Capability set before measuring:

- directly bindable;
- bindable with thin adapter;
- bindable with minimal OSS fork;
- bindable using structured semantic UI;
- unsupported.

No screenshot/vision/OCR/pixel-template path may count as success.

### SE16 — Target-user pilot evidence

Purpose:

- verify recurring current demand for compiling existing software into reusable Agent capabilities.

Use real external participants from successor target segments.

A positive participant must demonstrate both:

1. a recurring concrete current problem around software-capability reuse/compilation/discovery; and
2. a concrete pilot commitment such as a real software asset, task set, environment, engineering time, or maintainer review.

General interest is not enough.

The old E03 cohort/instrument is not successor evidence because it was frozen around the superseded Admission/Governance problem.

## 6. Ecosystem harvesting boundary

LLM-0 ecosystem/module harvesting is a reuse-first architecture/evolution strategy, not a new independent L1 Product claim.

L1 Product invariants require:

~~~text
REUSE_HARVEST_FIRST = YES
LLM_REWRITE_LICENSE_ERASURE = NO
PROVENANCE_REQUIRED = YES
~~~

But exact implementation of:

- codebase mining;
- feature/module extraction;
- direct reuse vs contract-based reimplementation;
- language coverage;
- module packaging;
- dependency/vendor strategy;

is L2/implementation work unless it changes SPCL-001..007.

A future architecture may fail to automate harvesting and fall back to curated patterns or direct OSS reuse without falsifying the Product.

## 7. Product-level success discipline

Every executable study must preserve:

- falsifiable hypothesis;
- exact source/model/tool versions;
- preregistered dataset/task boundaries;
- negative evidence;
- raw/durable evidence references;
- exact scoring logic;
- explicit What Was NOT Proven;
- no threshold changes after outcome visibility.

Gate states:

~~~text
PASS / FAIL / BLOCKED / NOT_RUN / NOT_APPLICABLE
~~~

## 8. Capability-readiness rule

A successor study must not treat:

~~~text
LLM_GENERATED
DOCUMENTED
DISCOVERED
HYPOTHESIZED
COMPILED
~~~

as equivalent to:

~~~text
EVIDENCED
EXPORT_READY
~~~

The exact evidence sufficiency policy is Product/L1 where it changes SPCL-002 or readiness trust; implementation mechanics may be L2.

## 9. Product Freeze aggregate

Successor Product Freeze requires at minimum:

~~~text
SE09 = reviewed PASS or accepted reviewed disposition
SE10 = PASS
SE11 = PASS
SE12 = PASS
SE13 = PASS
SE14 = PASS
SE15 = PASS
SE16 = PASS
Final Independent Product Review = PASS
open valid P0 = 0
open valid P1 = 0
L1->L2 transfer audit = PASS
~~~

Current state:

~~~text
SE09 = COMPLETE_RESEARCH / PROPOSED_PASS / REVIEW_REQUIRED
SE10 = NOT_RUN
SE11 = NOT_RUN
SE12 = NOT_RUN
SE13 = NOT_RUN
SE14 = NOT_RUN
SE15 = NOT_RUN
SE16 = NOT_RUN

PRODUCT_FREEZE = NO
L2_READY = NO
~~~
