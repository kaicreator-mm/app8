# app8 Product PRD v0.1 Successor — Evidence-backed Capability Exporter

Status: DRAFT_FOR_INDEPENDENT_REVIEW  
Product Freeze: NO  
L2 Ready: NO  
Successor authority: Issue #21  
Pinned standard: kaicreator-mm/ai-development-standard@7929012f36a2202dcc2edc7a414b8163adc7afbd (4.9.0)

## 1. Product definition

app8 is an **LLM-driven software capability exporter**.

It analyzes existing software assets and their documentation/tutorials/examples to understand what the software can do, proposes structured capability hypotheses, generates and executes tests or other evidence acquisition to validate or refute those hypotheses, and then exports the evidence-backed capabilities into Agent/LLM-native forms.

Primary outputs:

- CLI;
- MCP;
- Skill;
- Agent/LLM documentation;
- searchable Capability Metadata.

The core product loop is:

~~~text
Software Asset
  -> Source/Surface Discovery
  -> LLM Capability Analysis
  -> Capability Hypothesis
  -> Evidence/Test Planning
  -> Real Execution / Evidence Acquisition
  -> Evidence Package
  -> Evidence-backed Capability
  -> CLI / MCP / Skill / Docs / Search Metadata
~~~

The product is not limited to graphical Apps. A Software Asset may be a CLI tool, library, SDK, API, service, source repository, binary, desktop/server application, or a composition of these.

## 2. Problem

Mature software already implements a large amount of useful functionality, but Agents repeatedly pay the cost of rediscovering and adapting it:

- reading long documentation at task time;
- reasoning over low-level CLI/API surfaces instead of user-meaningful capabilities;
- writing one-off glue code;
- hand-authoring MCP tools or Skills;
- trusting LLM-generated wrappers that were never verified against the real software;
- using brittle pixel-based computer-use approaches where better semantic/programmatic surfaces exist.

The product opportunity is:

> turn existing software knowledge and behavior into reusable, evidence-backed Agent capabilities that can be exported once and consumed repeatedly.

## 3. Target users

Primary:

- Agent/runtime/tool-platform engineers who need reusable software capabilities;
- developers building local/server Agents that should reuse mature software instead of reimplementing functionality;
- teams that need to convert existing internal or third-party software into Agent-usable interfaces.

Secondary:

- software/library/tool maintainers who want to publish Agent-ready CLI/MCP/Skill surfaces without hand-maintaining each representation;
- capability catalog/search systems that need structured, evidence-aware metadata.

## 4. Primary source of capability understanding

For normal app8 operation, the primary semantic sources are:

1. official documentation;
2. official tutorials, cookbook material and examples;
3. built-in help, manpages and reference material;
4. API/SDK/library reference;
5. README/sample projects;
6. source code and type/schema information;
7. binary/static analysis or decompilation;
8. structured system/UI semantics such as UI Automation/accessibility trees.

Source code is important, but it is not the definition of a user-meaningful capability. app8 should prefer product/user intent expressed in documentation/tutorials and use lower-level analysis to fill gaps, diagnose failures, discover bindings, or recover undocumented surfaces.

## 5. LLM role

LLM reasoning is a first-class product mechanism, but LLM output is never self-verifying.

The LLM is expected to perform at least three distinct roles.

### LLM-A — Capability understanding

From documentation/tutorials/examples and discovered surfaces, propose:

- capability purpose;
- when to use it;
- inputs/outputs;
- important constraints;
- side effects;
- variants/modes;
- likely native bindings;
- examples/recipes;
- error semantics.

### LLM-B — Evidence planning

For a capability hypothesis, propose:

- executable fixtures;
- positive tests;
- negative/refutation tests;
- expected observable outputs;
- side-effect checks;
- version/platform checks;
- replay requirements.

### LLM-C — Export synthesis

Only after sufficient evidence exists, synthesize the Agent-facing abstraction:

- capability naming/grouping;
- parameter model;
- high-level variants;
- error/recovery guidance;
- recipes/examples;
- Skill and documentation content.

Deterministic generators/runtimes should materialize the final export artifacts where practical.

## 6. Evidence is the factual core

Evidence is not a separate governance product. It is the factual layer that prevents app8 exports from being based only on LLM inference.

A capability may move through states such as:

~~~text
DISCOVERED
  -> MODELED
  -> TEST_PLANNED
  -> EVIDENCED | REFUTED | BLOCKED
  -> EXPORT_READY
~~~

An export-ready capability must bind evidence to the relevant:

- software/provider identity and version/build;
- source claims/provenance;
- invocation/binding;
- fixtures/inputs;
- environment/platform;
- observations/results;
- negative/refuting evidence;
- replay information where feasible.

A passing fixture does not prove arbitrary-input or universal safety.

## 7. Capability model

The central product abstraction is an **Evidence-backed Capability**, not a raw function/endpoint/tool.

A Capability may aggregate multiple software surfaces and bindings.

Example:

~~~text
Capability: media.trim

Evidence-backed behavior:
- trim bounded media ranges
- fast stream-copy variant is keyframe constrained
- accurate variant requires decode/re-encode

Bindings:
- ffmpeg native CLI
- optional library binding

Exports:
- normalized CLI
- MCP tool
- Skill recipe
- Agent docs
~~~

Different low-level functions/commands that implement the same user-meaningful behavior should not automatically become separate top-level Agent tools.

The exact internal schema is L2_REQUIRED, but L2 may not remove provenance, evidence bindings, negative evidence, variants, constraints, or binding identity required by this PRD.

## 8. Export model

The intended architecture is **one evidence-backed capability model, many projections**.

Required v0.1 export classes:

1. normalized Agent-friendly CLI;
2. MCP server/tool surface;
3. portable Skill package;
4. Agent/LLM documentation;
5. searchable Capability Metadata.

Each exporter consumes the same frozen capability/evidence authority. An exporter may add representation-specific metadata, but it must not independently reinterpret the original software in a way that changes capability semantics.

Where a specific export is technically impossible, it must be explicitly UNSUPPORTED/BLOCKED rather than silently substituting a different capability.

## 9. Search / discovery

app8 exposes search over structured capability metadata.

The intended query is semantic/user-intent oriented:

~~~text
convert DOCX to PDF
inspect a pcap
extract audio from video
~~~

Search results should expose at least:

- matching software asset;
- capability;
- evidence/export readiness;
- available bindings/exports;
- relevant platform/version constraints.

Search must not represent a DISCOVERED/MODELED-only hypothesis as evidence-backed/export-ready.

A public marketplace is not required for v0.1.

## 10. Surface discovery and binding policy

app8 may discover or bind software through:

- native API / SDK / library;
- native CLI / headless mode;
- protocol / IPC / RPC / local service;
- file/structured data interfaces;
- source/type/schema analysis;
- binary/static analysis/decompilation;
- structured UI semantics such as Windows UI Automation, accessibility trees, semantic DOM/accessibility roles;
- a minimal OSS fork/patch that exposes an internal capability as a stable programmatic/headless interface;
- generated thin adapters/shims.

### Pixel-derived automation is forbidden

The following are outside the app8 capability mechanism:

- screenshot/image understanding as UI control discovery;
- vision-model button/menu localization;
- OCR/layout inference used to drive the UI;
- pixel/template matching;
- coordinate/pixel-derived Computer Use.

Normative rule:

~~~text
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
SEMANTIC_STRUCTURED_UI = ALLOWED
~~~

A structured accessibility/UI Automation tree is allowed because it exposes machine-readable semantic roles/state/actions; interpreting pixels is not.

If no permitted reliable binding can be found, app8 reports the capability/binding unsupported rather than falling back to screenshot-based automation.

## 11. Fork and reverse-engineering policy

For open-source software, a minimal fork/patch is an allowed first-class strategy when the useful capability already exists internally but lacks a stable Agent-usable interface.

Preferred outcome:

~~~text
existing internal capability
  -> minimal headless/structured interface
  -> CLI/MCP/Skill export
  -> optional upstream contribution
~~~

For binaries/closed software, static analysis/decompilation and internal-interface discovery may be used only where authorized and lawful. app8 does not define bypassing DRM, authorization or technical access controls as a product capability.

## 12. Product claims

These are successor Product/L1 claims. Required evidence is mapped in L1_EVIDENCE_INDEX.md.

### SPCL-001 — Useful capabilities can be extracted from software knowledge

Across representative heterogeneous software assets, documentation/tutorials/examples plus bounded lower-level analysis can produce a useful set of user-meaningful capability hypotheses with sufficient precision and coverage.

### SPCL-002 — Evidence can validate/refute capability hypotheses

LLM-generated test/evidence plans plus real execution/observation can distinguish supported capability claims from materially incorrect or incomplete claims well enough that export readiness is not merely an LLM assertion.

### SPCL-003 — One evidence-backed model can drive multiple exports

A single frozen Evidence-backed Capability can drive CLI, MCP, Skill and Agent documentation without independently re-understanding the source software for each exporter, while preserving consistent semantics.

### SPCL-004 — app8 exports improve Agent utility

For representative software tasks, Agents using app8 exports perform materially better than Agents given only the raw software interface/documentation under a comparable execution budget.

### SPCL-005 — Evidence-backed capabilities can be searched by intent

Natural-language capability search can retrieve relevant export-ready capabilities with useful ranking while clearly preserving evidence/readiness state.

### SPCL-006 — Useful export coverage is achievable without pixel-derived automation

Across a representative software portfolio, a material share of useful capabilities can be exported through programmatic, recovered, forked, or structured-semantic surfaces while never relying on pixel-derived automation.

### SPCL-007 — Target users have recurring reuse/export pain

At least one target segment has a recurring current need to convert existing software into reusable Agent-facing capabilities and is willing to provide real pilot software/tasks/environment or engineering time.

## 13. MVP black-box behavior

A v0.1 candidate should be able to:

1. accept a Software Asset and associated knowledge sources;
2. inventory source material and available semantic/programmatic surfaces;
3. produce capability hypotheses with provenance;
4. generate a bounded evidence/test plan;
5. execute/collect evidence against the real software when the environment permits;
6. retain positive and negative/refuting evidence;
7. mark capability state explicitly;
8. synthesize an Evidence-backed Capability from the frozen evidence package;
9. export supported capabilities to CLI, MCP, Skill and Agent docs;
10. publish searchable capability metadata;
11. answer semantic search queries over the indexed capabilities;
12. refuse pixel-derived automation rather than silently using screenshots/vision.

## 14. MVP non-goals

v0.1 does not require:

- a general Agent runtime/orchestrator;
- a security admission/governance platform;
- a universal ontology covering all software domains;
- a public marketplace;
- provider ranking/optimization;
- reimplementation of upstream software functionality;
- maintained large downstream forks;
- proof that finite tests establish universal safety;
- pixel/screenshot-based Computer Use;
- automatic success on every software asset.

## 15. Product invariants

### SINV-001 — Declaration is not Evidence

Documentation and LLM interpretation create claims/hypotheses, not verified capability truth.

### SINV-002 — LLM output cannot self-promote to verified/export-ready

A model cannot mark its own inferred capability verified without required evidence acquisition.

### SINV-003 — Negative evidence is first-class

Counterexamples, unsupported variants and observed constraints remain durable and may narrow/refute a capability.

### SINV-004 — Evidence is scoped

Evidence binds provider/software identity, version/build where available, environment, binding, input/fixture scope and observation boundary.

### SINV-005 — One factual authority, multiple exports

CLI/MCP/Skill/Docs must derive from the same capability/evidence authority rather than each exporter independently inventing semantics.

### SINV-006 — Semantic interfaces over pixels

Structured semantic UI/system interfaces are allowed. Pixel-derived automation is forbidden.

### SINV-007 — Reuse, do not reimplement

app8 exports/adapts existing software capability. Thin adapters and minimal forks are allowed; duplicating the mature upstream implementation is not the product goal.

### SINV-008 — Unsupported is a valid result

When no permitted binding/evidence path exists, app8 records UNSUPPORTED/BLOCKED instead of silently fabricating one.

### SINV-009 — Historical evidence is preserved

New evidence or capability synthesis may supersede an interpretation, but prior evidence/refutations remain auditable.

## 16. Product success / kill model

Product Freeze requires required successor L1 evidence plus an independent adversarial review with zero unresolved valid P0/P1.

Product kill/pivot conditions:

- **SK1 — Extraction failure:** SPCL-001 fails across the frozen representative portfolio.
- **SK2 — Evidence failure:** SPCL-002 fails; LLM hypotheses cannot be validated/refuted reliably enough to gate exports.
- **SK3 — Multi-export failure:** SPCL-003 fails and each target requires independent source re-analysis or produces materially inconsistent semantics.
- **SK4 — Utility failure:** SPCL-004 fails; exports do not materially improve Agent use of existing software.
- **SK5 — Search failure:** SPCL-005 fails; search may be removed from v0.1 while the exporter thesis may survive only through an explicit Product disposition.
- **SK6 — Non-pixel coverage failure:** SPCL-006 fails; if useful coverage is too low without screenshots/vision, the product does not relax the pixel prohibition and must narrow supported software classes instead.
- **SK7 — Adoption failure:** SPCL-007 fails; commercial/product continuation requires explicit disposition.

## 17. Required successor L1 evidence

The authoritative mapping is L1_EVIDENCE_INDEX.md.

Required studies are expected to cover:

- market/comparator evidence;
- capability extraction quality;
- evidence/test validation quality;
- multi-export consistency/executability;
- Agent utility;
- semantic search quality;
- non-pixel exportability/coverage;
- target-user pilot pull;
- final independent Product Review.

The completed predecessor E00 result is retained as research/method evidence but does not by itself PASS any successor SPCL.

## 18. L1 -> L2 Transfer Test

A question may be classified L2_REQUIRED only when all are true:

1. its answer does not change the target user, core problem, SPCL-001..007, MVP black-box behavior, pixel prohibition, evidence-before-export rule, success/kill criteria;
2. at least one technically plausible path is known at L1;
3. multiple reasonable architectures could satisfy the same product contract;
4. failure of one candidate implementation causes architecture pivot rather than falsifying the product claim.

If a negative answer would make a successor product claim false, the question is L1_BLOCKING.

## 19. Product Freeze authority

Product Freeze applies to an exact successor package, not this PRD alone.

At minimum it must bind:

- exact successor PRD blob;
- exact successor L1 Evidence Index blob;
- exact successor L2 Question Register blob;
- exact migration/disposition blob;
- all required successor protocol/result blobs;
- final independent Product Review;
- pinned ADS revision.

The predecessor Product Freeze manifest can never be promoted into successor Product Freeze.

## 20. Current terminal

~~~text
PRODUCT_DIRECTION = CONDITIONAL_GO
SUCCESSOR_PRODUCT = EVIDENCE_BACKED_CAPABILITY_EXPORTER
SUCCESSOR_PRODUCT_FREEZE = NO
L2_READY = NO
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
LEGACY_E00 = RETAINED_RESEARCH_ASSET

NEXT =
independent adversarial review of this successor Product/L1 authority package
then preregister/execute successor L1 studies only if review permits
~~~
