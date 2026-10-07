# app8 Product PRD v0.1 Successor r2 — Evidence-backed Software Capability Compiler

Status: DRAFT_FOR_INDEPENDENT_REVIEW  
Product Freeze: NO  
L2 Ready: NO  
Successor authority: Issue #21  
Expanded comparator evidence: SE09_COMPARATOR_EVIDENCE.md  
Pinned standard: kaicreator-mm/ai-development-standard@7929012f36a2202dcc2edc7a414b8163adc7afbd (4.9.0)

## 1. Product definition

app8 is an **LLM-driven software capability compiler**.

It converts existing software knowledge and real software behavior into reusable **Evidence-backed Capabilities**, then projects those capabilities into Agent/LLM-native interfaces and knowledge.

The stable product authority is not CLI, MCP, Skill, or any particular adapter.

The stable authority is:

~~~text
Capability semantics
+
Behavioral Evidence
+
Provenance/currentness
+
binding identity
~~~

CLI, MCP, Skill, Agent documentation and search metadata are replaceable projections/consumers of that authority.

Primary product outputs:

- Evidence-backed Capability packages;
- Agent-friendly CLI projections;
- MCP projections;
- portable Skill projections;
- Agent/LLM documentation;
- searchable Capability Metadata.

Inputs are not limited to graphical Apps. A Software Asset may be a CLI tool, library, SDK, API, service, source repository, binary, desktop/server application, website/Electron application, or a composition of these.

## 2. Product problem

Mature software already implements a large amount of useful functionality, but Agents repeatedly pay the cost of rediscovering and adapting it:

- reading long documentation at task time;
- reasoning over raw flags/functions/endpoints instead of user-meaningful capabilities;
- writing one-off glue code and wrappers;
- independently generating CLI/MCP/Skill representations that can drift semantically;
- trusting model-generated interfaces that were never validated against real software;
- losing knowledge about version-specific behavior, constraints, side effects and failure modes;
- rebuilding software-access machinery that mature open-source projects have already solved.

The product opportunity is:

> compile existing software into reusable, evidence-backed Agent capabilities, while learning from and reusing mature open-source engineering rather than rebuilding every interface mechanism.

## 3. Product core and non-core

### 3.1 app8-owned core

app8 owns:

- semantic Capability meaning;
- Capability lifecycle/readiness;
- Evidence semantics;
- positive and negative/refuting evidence;
- provenance;
- software/binding/version/environment currentness;
- falsification/evidence loop;
- Capability compilation from evidence;
- projection contracts;
- capability-level search semantics.

### 3.2 Non-core / reuse-first surfaces

These are necessary product capabilities but are not assumed to be proprietary app8 implementations:

- generic CLI generation;
- Web/Electron surface discovery;
- AST/framework/source analyzers;
- MCP generation;
- Skill generation;
- Agent utility evaluation infrastructure;
- backend health/routing;
- packaging/install machinery.

app8 should reuse, harvest, adapt, or directly depend on mature implementations when that is safer and cheaper than reimplementation.

The existence of these features in one product is not by itself app8 differentiation.

## 4. Core execution model

The main target-software compilation loop has three distinct LLM reasoning roles separated by real execution.

~~~text
Software knowledge / surfaces
          ↓
LLM-A — UNDERSTAND
          ↓
Capability Hypothesis
          ↓
LLM-B — FALSIFY
          ↓
Evidence/Test Plan
          ↓
Deterministic real execution / observation
          ↓
Behavioral Evidence
          ↓
LLM-C — COMPILE
          ↓
Evidence-backed Capability
          ↓
CLI / MCP / Skill / Docs / Search
~~~

The distinguishing property is not the number of model calls. It is the separation of epistemic roles:

- LLM-A is allowed to hypothesize;
- LLM-B actively searches for boundaries and counterexamples;
- reality, not a model, produces behavioral observations;
- LLM-C compiles only from the bounded hypothesis + evidence authority.

### 4.1 LLM-A — UNDERSTAND

From documentation/tutorials/examples and discovered surfaces, propose:

- user-meaningful capability purpose;
- when to use it;
- inputs/outputs;
- important constraints;
- side effects;
- variants/modes;
- likely native bindings;
- examples/recipes;
- expected error semantics.

LLM-A output is a hypothesis, not verified truth.

### 4.2 LLM-B — FALSIFY

For a Capability Hypothesis, propose bounded attempts to prove, narrow or refute it:

- executable fixtures;
- positive cases;
- negative/refutation cases;
- near-miss/boundary cases;
- expected observable outputs;
- side-effect checks;
- version/platform checks;
- replay requirements;
- tests designed to expose documentation ambiguity or hidden constraints.

The planner should ask "how could this claim be wrong?" rather than only "how can this pass?".

### 4.3 Deterministic real execution

When the environment permits, app8 executes or observes the actual software/binding and captures:

- commands/calls;
- inputs/fixtures;
- stdout/stderr or equivalent observations;
- output artifacts;
- state changes/side effects;
- version/environment identity;
- assertions and failures.

A model verdict is not a substitute for real execution where real behavior is the claim being tested.

### 4.4 LLM-C — COMPILE

LLM-C synthesizes an Agent-facing Capability only after evidence is available.

It decides, subject to evidence:

- which low-level surfaces belong to one semantic capability;
- which variants should remain distinct;
- which constraints become parameters/preconditions;
- which bindings are interchangeable;
- which failures/recovery guidance must be exposed;
- which claims must be narrowed or refuted.

LLM-C does not self-promote an unsupported capability to EXPORT_READY.

## 5. Offline ecosystem learning / module harvesting

app8 may use a low-frequency/offline LLM role to learn from mature open-source implementations.

~~~text
Open-source project
  -> LLM-0 ecosystem/code analysis
  -> reusable pattern/module candidate
  -> provenance + license disposition
  -> app8-owned contract
  -> independent validation
  -> KEEP / ADAPT / DIRECT_REUSE / DROP
~~~

LLM-0 answers:

> what has the software ecosystem already learned that app8 should not rediscover or reimplement?

This is an evolution/build-time lane, not a mandatory LLM call for every target-software compilation.

Three conceptual reuse levels are allowed:

~~~text
LEVEL_1_PATTERN
learn a reusable engineering pattern; no code intake required

LEVEL_2_REIMPLEMENTED_MODULE
derive a functional contract and implement an app8-owned generic module with durable provenance

LEVEL_3_DIRECT_REUSE
depend on/vendor/reuse upstream code when license, quality and module boundaries make that the best engineering decision
~~~

Normative rule:

~~~text
LLM_REWRITE != LICENSE_ERASURE
~~~

Model-assisted rewriting or refactoring does not automatically remove upstream copyright/license obligations. Code-derived work must preserve provenance and an appropriate license/reuse disposition.

The exact harvesting engine, code-analysis framework, language support and reuse machinery are L2/implementation questions unless later evidence shows they change the Product thesis.

## 6. Primary sources of capability understanding

For normal compilation, semantic sources are preferred roughly in this order:

1. official documentation;
2. official tutorials, cookbook material and examples;
3. built-in help, manpages and reference material;
4. API/SDK/library reference;
5. README/sample projects;
6. source code and type/schema information;
7. binary/static analysis or decompilation;
8. structured system/UI semantics such as UI Automation/accessibility trees.

Documentation/tutorials are important because they often express user intent better than raw callable surfaces.

Lower-level sources are used to:

- fill gaps;
- test claims;
- diagnose failed hypotheses;
- recover bindings;
- resolve undocumented behavior;
- establish implementation facts.

## 7. Evidence is the factual core

Evidence is not a separate governance product. It is the factual layer that prevents Capability and projection semantics from being based only on model inference.

A Capability may move through states such as:

~~~text
DISCOVERED
  -> HYPOTHESIZED
  -> TEST_PLANNED
  -> EVIDENCED | REFUTED | BLOCKED
  -> COMPILED
  -> EXPORT_READY
~~~

An Evidence Package may contain:

- documentation/source claims;
- invocation/binding identity;
- software/provider identity and version/build;
- fixtures/inputs;
- environment/platform;
- actual observations/results;
- output artifacts/state deltas;
- positive evidence;
- negative/refuting evidence;
- known constraints;
- known unsupported cases;
- replay information where feasible;
- currentness/provenance.

A passing fixture does not prove arbitrary-input or universal safety.

Evidence can narrow or refute the original hypothesis.

## 8. Capability model

The central semantic unit is an **Evidence-backed Capability**, not a raw function, endpoint, flag or UI action.

Example:

~~~text
Capability: media.trim

Evidence-backed behavior:
- bounded media trim
- fast stream-copy variant is keyframe constrained
- accurate variant requires decode/re-encode

Bindings:
- ffmpeg native CLI
- optional library binding

Projections:
- normalized CLI
- MCP tool
- Skill recipe
- Agent docs
~~~

A Capability may aggregate multiple low-level surfaces and multiple bindings.

Different functions/commands that implement the same user-meaningful behavior should not automatically become separate top-level Agent tools.

The exact internal schema is L2_REQUIRED, but L2 may not remove:

- evidence linkage;
- provenance;
- negative evidence;
- variants;
- constraints;
- binding identity;
- version/environment scope;
- readiness/currentness.

## 9. One authority, many projections

The product architecture is:

~~~text
Evidence Corpus
      ↓
Evidence-backed Capability
      ↓
 ┌────┼─────┬─────┬─────┐
 CLI  MCP  Skill  Docs  Search Metadata
~~~

Each projector consumes the same frozen Capability/Evidence authority.

A projector may add representation-specific material, but it must not independently reinterpret original software in a way that changes semantic truth.

A projection may be:

~~~text
SUPPORTED
UNSUPPORTED
BLOCKED
STALE
~~~

Unsupported output formats are valid results. app8 must not silently substitute a different capability.

## 10. Search / discovery

app8 exposes search over structured Evidence-backed Capability Metadata.

The intended query is semantic/user-intent oriented:

~~~text
convert DOCX to PDF
inspect a pcap
extract audio from video
~~~

Search results should expose at least:

- matching software asset;
- capability;
- evidence/readiness state;
- available bindings/projections;
- version/platform constraints;
- relevant negative/unsupported boundaries where material.

Search must not represent DISCOVERED/HYPOTHESIZED-only material as EXPORT_READY.

A public marketplace is not required for v0.1.

## 11. Surface discovery and binding policy

app8 may discover or bind software through:

- native API / SDK / library;
- native CLI / headless mode;
- protocol / IPC / RPC / local service;
- file/structured data interfaces;
- source/type/schema analysis;
- binary/static analysis/decompilation;
- structured UI semantics such as Windows UI Automation, accessibility trees and semantic DOM/accessibility roles;
- a minimal OSS fork/patch that exposes an internal capability as a stable programmatic/headless interface;
- generated thin adapters/shims.

Binding selection should prefer stable programmatic surfaces over fragile interaction paths.

### Pixel-derived automation is forbidden

The following are outside the app8 capability mechanism:

- screenshot/image understanding as UI control discovery;
- vision-model button/menu localization;
- OCR/layout inference used to drive UI;
- pixel/template matching;
- coordinate/pixel-derived Computer Use.

Normative rule:

~~~text
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
SEMANTIC_STRUCTURED_UI = ALLOWED
~~~

Structured accessibility/UI Automation is allowed because it exposes machine-readable semantic roles/state/actions.

If no permitted reliable binding exists, app8 reports UNSUPPORTED/BLOCKED instead of falling back to pixel-derived automation.

## 12. Fork and reverse-engineering policy

For open-source software, a minimal fork/patch is allowed when useful capability already exists internally but lacks a stable Agent-usable interface.

Preferred pattern:

~~~text
existing internal capability
  -> minimal headless/structured interface
  -> evidence
  -> Capability binding
~~~

For binaries/closed software, static analysis/decompilation/internal-interface discovery may be used only where authorized and lawful.

app8 does not define bypassing DRM, authorization or technical access controls as a product capability.

## 13. Product claims

Required evidence is mapped in L1_EVIDENCE_INDEX.md.

### SPCL-001 — Useful semantic capabilities can be extracted

Across representative heterogeneous software assets, documentation/tutorials/examples plus bounded lower-level analysis can produce useful user-meaningful Capability Hypotheses with acceptable precision and coverage.

### SPCL-002 — Falsification/evidence can validate or refute hypotheses

LLM-generated adversarial evidence plans plus real execution/observation can distinguish supported claims from materially incorrect/incomplete claims well enough that Capability readiness is not merely a model assertion.

### SPCL-003 — One Capability authority can drive multiple consumers

A single frozen Evidence-backed Capability can drive CLI, MCP, Skill, Agent docs and searchable metadata without each consumer independently re-understanding the source software or materially drifting semantics.

### SPCL-004 — app8 Capability projections improve Agent utility

For representative software tasks, Agents using app8-produced projections perform materially better than Agents given only raw software interfaces/documentation under comparable execution budgets.

### SPCL-005 — Capabilities can be searched by intent

Natural-language Capability search can retrieve relevant evidence-backed capabilities with useful ranking and correct readiness/currentness representation.

### SPCL-006 — Useful coverage is achievable without pixel-derived automation

Across a representative software portfolio, a material share of useful capabilities can be bound through native/programmatic/recovered/forked/structured-semantic surfaces while obeying the pixel prohibition.

### SPCL-007 — Target users have recurring capability-compilation pain

At least one target segment has a recurring current need to turn existing software into reusable Agent capabilities and is willing to contribute a real software asset, task set, environment, engineering time or maintainer review.

## 14. Expanded market finding

SE09 finds:

~~~text
CATEGORY_VALIDATION = VERY_STRONG
DIRECT_COMPETITION = HIGH
FEATURE_DIFFERENTIATION = LOW
ARCHITECTURAL_DIFFERENTIATION = MEDIUM
UNIFIED_PRODUCT_GAP = MEDIUM
~~~

CLI/MCP/Skill generation, Web/Electron adapters, library-to-Skill generation, Agent utility evaluation, registries and backend routing are already strongly represented in current projects.

Therefore app8 may proceed only under the narrower thesis:

> Evidence-backed Capability authority + falsification/evidence + one authority to replaceable consumers.

Exporter breadth alone is not a valid differentiation claim.

## 15. MVP black-box behavior

A v0.1 candidate should be able to:

1. accept a Software Asset and associated knowledge sources;
2. inventory semantic/programmatic surfaces;
3. produce Capability Hypotheses with provenance;
4. generate bounded adversarial evidence/test plans;
5. execute/collect real evidence when the environment permits;
6. retain positive and negative/refuting evidence;
7. explicitly mark capability state/readiness;
8. compile an Evidence-backed Capability from frozen evidence;
9. generate at least representative CLI, MCP, Skill and Agent-doc projections from the same Capability authority;
10. publish searchable Capability Metadata;
11. answer semantic Capability queries;
12. revalidate or mark stale when bound software/evidence currentness changes;
13. refuse pixel-derived automation rather than silently using screenshots/vision.

The MVP may reuse or harvest mature external open-source mechanisms instead of implementing every exporter/discovery engine from scratch.

## 16. MVP non-goals

v0.1 does not require:

- a general Agent runtime/orchestrator;
- a security admission/governance product;
- a universal ontology;
- a public marketplace;
- proprietary reimplementation of mature CLI/MCP/Skill infrastructure;
- automatic module harvesting for every open-source project;
- a permanently maintained fork of every upstream software target;
- proof that finite tests establish universal safety;
- pixel/screenshot-based Computer Use;
- automatic success on every software asset.

## 17. Product invariants

### SINV-001 — Declaration is not Evidence

Documentation and model interpretation create claims/hypotheses, not verified truth.

### SINV-002 — Model output cannot self-certify

No LLM stage can self-promote an inferred capability to EVIDENCED/EXPORT_READY without required external evidence.

### SINV-003 — Falsification is first-class

Evidence planning must include attempts to discover negative cases, limits and counterexamples where material.

### SINV-004 — Negative evidence is durable

Counterexamples, unsupported variants and observed constraints remain part of the factual authority.

### SINV-005 — Evidence is scoped

Evidence binds software/provider identity, version/build where available, environment, binding, fixture/input scope and observation boundary.

### SINV-006 — One factual authority, many consumers

CLI/MCP/Skill/Docs/Search must derive from the same Capability/Evidence authority rather than each consumer independently inventing semantic truth.

### SINV-007 — Semantic interfaces over pixels

Structured semantic UI/system interfaces are allowed. Pixel-derived automation is forbidden.

### SINV-008 — Reuse/harvest before reimplementation

When mature OSS already solves a non-core mechanism, app8 should first consider pattern harvesting, contract-based reimplementation or direct reuse rather than rebuilding it.

### SINV-009 — Provenance/license cannot be erased by LLM transformation

Model-assisted code analysis/refactoring does not eliminate upstream provenance or license obligations.

### SINV-010 — Reuse software, do not replace it

app8 exposes/adapts existing software capability. Thin adapters and minimal forks are allowed; duplicating mature upstream application logic is not the product goal.

### SINV-011 — Unsupported is valid

When no permitted reliable path exists, app8 records UNSUPPORTED/BLOCKED rather than fabricating one.

### SINV-012 — Historical evidence is preserved

New evidence or Capability compilation may supersede an interpretation, but prior evidence/refutations remain auditable.

## 18. Product success / kill model

Product Freeze requires required successor L1 evidence plus independent adversarial Product review with zero unresolved valid P0/P1.

Kill/pivot conditions:

- SK1 — capability extraction fails across the frozen representative portfolio;
- SK2 — falsification/evidence cannot reliably distinguish supported from materially unsupported claims;
- SK3 — one factual Capability authority cannot drive multiple consumers without material semantic drift;
- SK4 — app8-produced Capability projections do not materially improve Agent utility;
- SK5 — Capability search fails; search may be removed only by explicit Product disposition;
- SK6 — useful coverage is too low without pixel-derived automation; app8 must narrow supported classes rather than relax the prohibition;
- SK7 — no target segment demonstrates recurring current pull.

Failure to automate LLM-0 ecosystem harvesting by itself does not kill the Product thesis; it causes an architecture/implementation fallback to curated patterns, direct OSS reuse or independently implemented modules.

## 19. Required successor L1 evidence

The authoritative mapping is L1_EVIDENCE_INDEX.md.

Required evidence covers:

- expanded market/comparator landscape;
- semantic capability extraction;
- falsification/evidence quality;
- one-authority/multi-consumer consistency;
- Agent utility;
- Capability search;
- non-pixel exportability;
- target-user pilot pull;
- final independent Product review.

The completed predecessor E00 remains method/research evidence only.

## 20. L1 -> L2 Transfer Test

A question may be L2_REQUIRED only when all are true:

1. its answer does not change target user, core problem, SPCL-001..007, MVP black-box behavior, Evidence-before-readiness, one-authority-many-consumers, pixel prohibition or kill criteria;
2. at least one technically plausible path is known at L1;
3. multiple reasonable architectures could satisfy the Product contract;
4. failure of one implementation path causes architecture pivot rather than Product falsification.

If a negative answer would falsify a Product claim, it is L1_BLOCKING.

Examples normally left to L2:

- internal Capability IR schema;
- storage/content-addressing;
- exact model/provider routing;
- exact OSS harvesting implementation;
- whether a module is reused directly vs reimplemented under a clean functional contract;
- exporter implementation choices.

## 21. Product Freeze authority

Product Freeze applies to an exact successor package, not this PRD alone.

At minimum it binds:

- exact successor PRD blob;
- exact L1 Evidence Index blob;
- exact expanded SE09 evidence blob;
- exact L2 Question Register blob;
- exact migration/disposition blob;
- all required successor L1 protocols/results;
- final independent Product Review;
- pinned ADS revision.

The predecessor Product Freeze manifest can never be promoted into successor Product Freeze.

## 22. Current terminal

~~~text
PRODUCT_DIRECTION = NARROW_AND_PROCEED
SUCCESSOR_PRODUCT = EVIDENCE_BACKED_SOFTWARE_CAPABILITY_COMPILER
CORE_RUNTIME = UNDERSTAND -> FALSIFY -> REAL_EXECUTION -> COMPILE
OFFLINE_EVOLUTION = LLM_0_ECOSYSTEM_MINING
REUSE_HARVEST_FIRST = YES
LLM_REWRITE_LICENSE_ERASURE = NO
SUCCESSOR_PRODUCT_FREEZE = NO
L2_READY = NO
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
LEGACY_E00 = RETAINED_RESEARCH_ASSET

NEXT =
refresh successor L1 index/current exact package
then context-fresh independent Product review
~~~
