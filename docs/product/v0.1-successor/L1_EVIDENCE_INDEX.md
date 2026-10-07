# L1 Evidence Index — app8 v0.1 Successor

Status: DRAFT_FOR_INDEPENDENT_REVIEW  
Authority: successor claim-to-evidence map for PRD.md

## 1. Purpose

This document defines what must be proven before successor Product Freeze.

It does not define production architecture.

## 2. Claim map

| Successor claim | Required evidence | Gate consequence |
|---|---|---|
| SPCL-001 Useful capability extraction | SE10 | FAIL => SK1 |
| SPCL-002 Evidence validates/refutes hypotheses | SE11 + inherited E00 as method evidence only | FAIL => SK2 |
| SPCL-003 One model, many exports | SE12 | FAIL => SK3 |
| SPCL-004 Agent utility | SE13 | FAIL => SK4 |
| SPCL-005 Capability search by intent | SE14 | FAIL => SK5 disposition |
| SPCL-006 Non-pixel exportability | SE15 | FAIL => SK6 / narrow supported classes |
| SPCL-007 Target-user pilot pull | SE16 | FAIL => SK7 |
| Product/category differentiation | SE09 | informs all claims; cannot substitute for execution evidence |

## 3. Inherited predecessor evidence

Predecessor E00 is retained:

~~~text
Issue #9 = PASS
E00 result blob = 9c4277b6fab4bdb89a94e688de3f438fc2f9ef85
~~~

It demonstrates a blinded commitment/reveal/scoring method and a bounded detector result on its frozen 160-case synthetic corpus.

It does not prove:

- successor capability extraction quality;
- real-software capability validation;
- multi-export quality;
- Agent utility;
- search quality;
- heterogeneous non-pixel exportability;
- successor adoption.

Therefore E00 is an inherited research asset, not a successor Gate PASS.

## 4. Required successor studies

### SE09 — Market / comparator evidence

Purpose:

- document current adjacent products that generate MCP, CLI or Skills;
- identify what they consume as source material;
- determine whether they expose a first-class Evidence-backed Capability layer;
- test whether app8 differentiation is more than feature bundling.

At minimum include direct code/product evidence for the strongest comparators and explicit reuse-vs-build conclusions.

A competitor existing is not failure. Failure occurs if the complete successor thesis is already available with no material differentiated product problem.

### SE10 — Capability extraction quality

Purpose:

- test whether docs/tutorials/examples can be converted into user-meaningful capability hypotheses across heterogeneous software.

Protocol must freeze before evaluation:

- representative software/source classes;
- exact asset versions/snapshots;
- independent reference/gold capability set;
- what counts as user-meaningful capability;
- matching/adjudication procedure;
- precision/coverage metrics and PASS thresholds.

Minimum portfolio must cover at least four materially different source classes, including at least:

- a mature CLI/application;
- a library/SDK;
- an API/service or structured spec;
- an application whose useful capability is not exposed only as a trivial exported function list.

The study must penalize both hallucinated capabilities and low-level callable spam represented as separate top-level capabilities.

### SE11 — Evidence / test validation quality

Purpose:

- determine whether LLM-generated evidence/test plans can confirm or refute capability hypotheses against real software.

The protocol must include:

- positive and materially false/incomplete claims;
- hidden or independently curated truth where feasible;
- real execution/observation;
- negative/refutation evidence;
- provider/version/environment binding;
- frozen scoring before reveal;
- near-miss cases, not only obvious synthetic contradictions.

PASS thresholds must bound false promotion of unsupported claims and false rejection of supported claims.

No LLM self-label may count as ground truth.

### SE12 — One evidence model, many exports

Purpose:

- test whether one frozen Evidence-backed Capability can drive all required projections.

Required outputs:

- CLI;
- MCP;
- Skill;
- Agent/LLM docs;
- searchable metadata.

The study must verify:

- exporters consume the same frozen capability/evidence authority;
- no exporter re-analyzes original source material to change capability semantics;
- CLI and MCP execute the intended real-software behavior;
- Skill/docs describe the same constraints/variants/errors;
- representation-specific differences do not become semantic drift.

Protocol must freeze an executable capability/task set and consistency scoring before export generation.

### SE13 — Agent utility

Purpose:

- compare Agents using raw software documentation/native interfaces with Agents using app8 exports.

Use a paired/blinded task design where practical.

Freeze:

- Agent/model/version;
- tool/runtime access;
- context and execution budget;
- representative tasks;
- success scorer;
- primary utility metric;
- secondary cost metrics such as tool-selection errors, glue-code creation, time/tokens/retries.

The test must not give the app8 arm hidden answer keys unavailable to the raw-doc arm.

### SE14 — Capability search quality

Purpose:

- test semantic retrieval over Evidence-backed Capability Metadata.

Freeze:

- a capability index;
- natural-language intent queries;
- relevance judgments;
- ranking metric(s);
- readiness-display checks.

Search must never represent DISCOVERED/MODELED-only hypotheses as EXPORT_READY.

### SE15 — Non-pixel exportability

Purpose:

- measure how much useful software capability can be exported while obeying:

~~~text
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
~~~

Allowed routes include native interfaces, IPC/protocols, source/binary analysis, minimal forks/adapters and structured semantic UI automation/accessibility interfaces.

Protocol must freeze a representative asset portfolio and top-capability set before measuring:

- directly exportable;
- exportable with thin adapter;
- exportable with minimal OSS fork;
- exportable using structured semantic UI;
- unsupported.

No screenshot/vision/OCR/pixel-template path may be counted as success.

### SE16 — Target-user pilot evidence

Purpose:

- verify recurring current demand for exporting existing software capabilities into reusable Agent interfaces/knowledge.

Use real external participants from successor target segments.

A positive participant must demonstrate both:

1. a recurring concrete current problem around software-capability reuse/export/discovery; and
2. a concrete pilot commitment such as a real software asset, task set, environment, engineering time, or maintainer review.

General interest is not enough.

The old E03 cohort/instrument is not successor evidence because it was frozen around the superseded admission/governance problem.

## 5. Product-level success discipline

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

## 6. Export-readiness rule

A successor study must not treat:

~~~text
LLM_GENERATED
DOCUMENTED
DISCOVERED
MODELED
~~~

as equivalent to:

~~~text
EVIDENCED
EXPORT_READY
~~~

The exact evidence sufficiency policy is a Product/L1 concern where it changes SPCL-002 or export trust; implementation mechanics may be L2.

## 7. Product Freeze aggregate

Successor Product Freeze requires at minimum:

~~~text
SE09 = PASS or accepted category/differentiation disposition
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

Any required NOT_RUN/BLOCKED keeps:

~~~text
PRODUCT_FREEZE = NO
L2_READY = NO
~~~
