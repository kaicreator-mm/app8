# Product Direction Migration — Admission/Governance -> Evidence-backed Capability Exporter

Status: CANDIDATE_SUCCESSOR_MIGRATION  
Authority trigger: Issue #21  
Migration base main: 3c962ff5055e024c9676b041aa12531f0fc20692

## 1. Why a successor is required

The predecessor Product/L1 line defined app8 primarily as:

~~~text
Executable Conformance + Evidence + Admission
~~~

The clarified product is:

~~~text
LLM software understanding
  -> Capability Hypothesis
  -> Evidence
  -> Evidence-backed Capability
  -> CLI / MCP / Skill / Docs / Search
~~~

This changes the core problem, target value, black-box behavior, success criteria and kill criteria. It is therefore not a minor PRD remediation.

## 2. Predecessor product authorities

The following remain immutable historical evidence:

- docs/product/v0.1/PRD.md — predecessor Admission/Governance PRD;
- docs/product/v0.1/L1_EVIDENCE_INDEX.md;
- docs/product/v0.1/PRODUCT_FREEZE.md;
- predecessor reviews/issues/results.

The predecessor Product Freeze was never achieved and must never be promoted after this migration.

## 3. Research retained

The completed E00 campaign is retained as durable research:

~~~text
Issue #9 terminal = PASS
E00 result blob = 9c4277b6fab4bdb89a94e688de3f438fc2f9ef85
~~~

Retained principles:

- Declaration != Evidence;
- LLM/model output cannot self-certify;
- positive and negative/refuting evidence are first-class;
- evidence is scoped to provider/version/environment/fixtures/observation;
- blinded/frozen scoring where appropriate;
- real execution and reproducibility/provenance;
- explicit What Was NOT Proven.

E00 remains bounded to its synthetic corpus and does not automatically satisfy successor evidence Gates.

## 4. Research not promoted

These predecessor concerns are not successor Product evidence:

- old E01 false-safe/stale declaration prevalence;
- old E02 Admission decision-value experiment;
- old E03 admission/governance adoption study;
- old security-enforcement threat promise;
- old Final Product Freeze review.

The E03-A cohort/instrument frozen in Issue #13 remains historical research only. No interview outcome had been collected when product direction changed.

## 5. Issue disposition

Durable controller disposition under Issue #21:

- #6 — predecessor E00 umbrella: completed; research retained;
- #9 — E00-C: PASS; retained;
- #12 — old E03 umbrella: superseded;
- #13 — old E03-A cohort/instrument: completed historical artifact, not successor evidence;
- #14 — old E03 interviews: superseded / do not execute;
- #15 — old E03 scoring: superseded;
- #16 — old E01 prevalence: superseded;
- #17 — old E02 Admission decision value: superseded;
- #18 — old Final Product Freeze review: superseded.

## 6. Product semantics preserved vs removed

### Preserved

- Evidence is central.
- Negative evidence/refutation matters.
- Provider/version/environment scoping matters.
- Evidence must be replayable/auditable where feasible.
- LLM-generated claims require external validation.

### Removed from core product authority

- Admission as the product endpoint;
- governance decision engine as the main value proposition;
- deterministic enforcement runtime as the defining product boundary;
- the predecessor security threat promise as v0.1 app8 product scope.

These may be consumed by or integrated with app8 later but are not the successor core.

## 7. New hard boundary

~~~text
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
SEMANTIC_STRUCTURED_UI = ALLOWED
~~~

Structured semantic UI/system interfaces such as Windows UI Automation/accessibility trees may be used. Screenshot/vision/OCR/pixel/template/coordinate-derived Computer Use is not a capability discovery, binding or runtime mechanism.

## 8. New successor authority

Candidate package:

- docs/product/v0.1-successor/PRD.md
- docs/product/v0.1-successor/L1_EVIDENCE_INDEX.md
- docs/product/v0.1-successor/L2_QUESTION_REGISTER.md
- this migration document
- docs/product/v0.1-successor/PRODUCT_FREEZE.md

No successor Product Freeze or L2 entry is authorized until context-fresh independent Product review permits successor L1 execution and all required L1 evidence later passes.
