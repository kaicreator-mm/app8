# Product Direction Migration — Admission/Governance -> Evidence-backed Software Capability Compiler

Status: CANDIDATE_SUCCESSOR_MIGRATION  
Authority trigger: Issue #21  
Migration base main: 3c962ff5055e024c9676b041aa12531f0fc20692

## 1. Why a successor is required

The predecessor Product/L1 line defined app8 primarily as:

~~~text
Executable Conformance + Evidence + Admission
~~~

The successor is now:

~~~text
software knowledge / surfaces
  -> LLM-A UNDERSTAND
  -> Capability Hypothesis
  -> LLM-B FALSIFY
  -> real execution / observation
  -> Behavioral Evidence
  -> LLM-C COMPILE
  -> Evidence-backed Capability
  -> CLI / MCP / Skill / Docs / Search
~~~

with an additional low-frequency/offline evolution lane:

~~~text
open-source ecosystem
  -> LLM-0 ecosystem/code mining
  -> pattern/module candidates
  -> provenance/license gate
  -> app8-owned reusable modules/profiles
~~~

This changes the core problem, target value, black-box behavior, success criteria and kill criteria. It is not a minor remediation of the predecessor PRD.

## 2. Successor refinement history

### Successor r1

The first successor corrected the product endpoint from Admission/Governance to an Evidence-backed Capability Exporter.

### Successor r2

Expanded comparator research showed that CLI/MCP/Skill generation, Web/Electron adapters, library-to-Skill generation, evaluation and routing are already strongly served by current projects.

Therefore r2 narrows the Product identity further:

~~~text
NOT THE MOAT:
CLI generation
MCP generation
Skill generation
registry breadth
adapter breadth

APP8 CORE:
Evidence-backed Capability authority
Behavioral falsification/evidence
one authority -> replaceable consumers
~~~

r2 also adopts reuse/harvest-first as a Product invariant while keeping exact OSS module mining/reuse mechanics in L2/implementation.

## 3. Predecessor Product authorities

The following remain immutable historical evidence:

- docs/product/v0.1/PRD.md — predecessor Admission/Governance PRD;
- docs/product/v0.1/L1_EVIDENCE_INDEX.md;
- docs/product/v0.1/PRODUCT_FREEZE.md;
- predecessor reviews/issues/results.

The predecessor Product Freeze was never achieved and must never be promoted after this migration.

## 4. Research retained

The completed E00 campaign is retained as durable research:

~~~text
Issue #9 terminal = PASS
E00 result blob = 9c4277b6fab4bdb89a94e688de3f438fc2f9ef85
~~~

Retained principles:

- Declaration != Evidence;
- model output cannot self-certify;
- positive and negative/refuting evidence are first-class;
- evidence is scoped to software/version/environment/fixtures/observation;
- blinded/frozen scoring where appropriate;
- real execution and provenance/reproducibility;
- explicit What Was NOT Proven.

E00 remains bounded to its synthetic corpus and does not automatically satisfy successor evidence Gates.

## 5. Research not promoted

These predecessor concerns are not successor Product evidence:

- old E01 false-safe/stale declaration prevalence;
- old E02 Admission decision-value experiment;
- old E03 admission/governance adoption study;
- old security-enforcement threat promise;
- old Final Product Freeze review.

The E03-A cohort/instrument in Issue #13 remains historical research only.

## 6. Expanded comparator correction

The initial successor competitor sweep was incomplete because it over-indexed on MCP/Skill/exporter terminology.

Expanded SE09 now includes major adjacent categories such as:

- GUI/App -> Agent CLI;
- Web/Electron -> deterministic CLI;
- docs/API/SDK -> Agent CLI;
- code/application -> MCP;
- library -> Fact/Skill;
- Skill utility evaluation;
- capability/backend routing.

Durable evidence:

~~~text
docs/product/v0.1-successor/SE09_COMPARATOR_EVIDENCE.md
ADS method follow-up = kaicreator-mm/ai-development-standard#929
~~~

This correction reduces differentiation claims but strengthens category validation.

## 7. Issue disposition

Durable controller disposition under Issue #21:

- #6 — predecessor E00 umbrella: completed; research retained;
- #9 — E00-C: PASS; retained;
- #12 — old E03 umbrella: superseded;
- #13 — old E03-A cohort/instrument: historical artifact only;
- #14 — old E03 interviews: superseded / do not execute;
- #15 — old E03 scoring: superseded;
- #16 — old E01 prevalence: superseded;
- #17 — old E02 Admission decision value: superseded;
- #18 — old Final Product Freeze review: superseded.

The first successor Fresh Review #23 is also superseded once r2 changes PR #22 exact HEAD/tree; it must not review the stale r1 subject.

## 8. Product semantics preserved

- Evidence is central.
- Negative evidence/refutation matters.
- software/version/environment/binding scope matters.
- real execution matters.
- model-generated claims require external validation.
- Capability is semantic and distinct from raw callable surfaces.
- one factual authority must feed multiple projections.
- structured semantic UI is permitted.
- pixel-derived UI automation is forbidden.

## 9. Product semantics newly strengthened

### Reuse/harvest first

app8 should not reimplement mature non-core software-agentification machinery by default.

Allowed approaches:

~~~text
LEVEL_1_PATTERN
LEVEL_2_REIMPLEMENTED_MODULE
LEVEL_3_DIRECT_REUSE
~~~

### Provenance/license

~~~text
LLM_REWRITE != LICENSE_ERASURE
~~~

Any code-derived work must preserve durable provenance and an appropriate reuse/license disposition.

### Three runtime LLM roles

~~~text
UNDERSTAND -> FALSIFY -> REAL_EXECUTION -> COMPILE
~~~

These roles are semantically distinct. Real behavior is not decided by a model vote.

### Offline ecosystem learning

LLM-0 ecosystem mining is an evolution/build-time strategy and does not need to run for every target-software compilation.

## 10. Removed from core Product authority

- Admission as endpoint;
- governance decision engine as primary value;
- deterministic enforcement runtime as product identity;
- generic CLI/MCP/Skill generation as moat;
- runtime dependence on a fixed bundle of third-party projects.

## 11. Hard boundary

~~~text
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
SEMANTIC_STRUCTURED_UI = ALLOWED
~~~

Structured system/UI semantics such as Windows UI Automation/accessibility trees may be used.

Screenshot/Vision/OCR/pixel/template/coordinate-derived Computer Use is not a Capability discovery, binding or runtime mechanism.

## 12. Successor authority package

Candidate package now includes:

- docs/product/v0.1-successor/PRD.md
- docs/product/v0.1-successor/L1_EVIDENCE_INDEX.md
- docs/product/v0.1-successor/SE09_COMPARATOR_EVIDENCE.md
- docs/product/v0.1-successor/L2_QUESTION_REGISTER.md
- this migration document
- docs/product/v0.1-successor/PRODUCT_FREEZE.md

No successor Product Freeze or L2 entry is authorized until required L1 evidence and context-fresh independent Product review pass.
