# app8

**app8** is an LLM-driven **Evidence-backed Software Capability Compiler**.

It turns software knowledge plus real software behavior into reusable **Evidence-backed Capabilities**, then projects the same factual authority into Agent-facing CLI, MCP, Skill, documentation and searchable Capability Metadata.

The stable authority is not an exporter or adapter:

```text
Capability semantics
+ Behavioral Evidence
+ Provenance / Currentness
+ Binding identity
```

## Current stage

```text
PRODUCT_DIRECTION = NARROW_AND_PROCEED
SUCCESSOR_PRODUCT = EVIDENCE_BACKED_SOFTWARE_CAPABILITY_COMPILER

CORE_RUNTIME =
UNDERSTAND
-> FALSIFY
-> REAL_EXECUTION
-> COMPILE
-> Evidence-backed Capability

PRODUCT_FREEZE = NO
L2_READY = NO
FORMAL_IMPLEMENTATION_TASK_DAG = NOT_AUTHORIZED
```

The project is still in **Product/L1 evidence qualification**. Protocol/research work is not production implementation.

## Product documents

- [English PRD — v0.1 Successor r2](docs/product/v0.1-successor/PRD.md) — normative Product/L1 reference.
- [中文 PRD — v0.1 Successor r2](docs/product/v0.1-successor/PRD.zh-CN.md) — Chinese reference translation; English authority remains normative.
- [L1 Evidence Index](docs/product/v0.1-successor/L1_EVIDENCE_INDEX.md) — SPCL claim-to-evidence mapping and Product Freeze gate.
- [SE09 Comparator Evidence](docs/product/v0.1-successor/SE09_COMPARATOR_EVIDENCE.md) — market/comparator and reuse-first evidence.
- [L2 Question Register](docs/product/v0.1-successor/L2_QUESTION_REGISTER.md) — candidate architecture questions only; does not authorize L2.
- [Product Freeze Manifest](docs/product/v0.1-successor/PRODUCT_FREEZE.md) — exact-package aggregation only.

The previous `docs/product/v0.1/**` Admission/Governance product line is historical/superseded for the current successor product.

## Core product loop

```text
Software knowledge / surfaces
          ↓
LLM-A — UNDERSTAND
          ↓
Capability Hypothesis
          ↓
LLM-B — FALSIFY
          ↓
Evidence / Test Plan
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
```

Important rules:

```text
DECLARATION != EVIDENCE
LLM_OUTPUT_SELF_CERTIFICATION = FORBIDDEN
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
SEMANTIC_STRUCTURED_UI = ALLOWED
REUSE_HARVEST_FIRST = YES
LLM_REWRITE_LICENSE_ERASURE = NO
```

## L1 evidence campaign

The active successor L1 campaign is tracked in [Issue #25](https://github.com/kaicreator-mm/app8/issues/25).

Required studies:

```text
SE10 = Semantic Capability extraction quality
SE11 = Falsification / Evidence quality
SE12 = One authority / many consumers
SE13 = Agent utility
SE14 = Capability search quality
SE15 = Non-pixel exportability
SE16 = Target-user pilot pull
Final Independent Product Review
```

The current research dependency structure is approximately:

```text
protocol authoring/review
        ↓
SE10 execution ─┐
SE11 execution ─┼─> SE12 execution ─> SE13 execution
                │
SE14 execution ─┼─────────────────────────┐
SE15 execution ─┤                         │
SE16 execution ─┘                         │
SE12 / SE13 results ──────────────────────┘
                                          ↓
                                 Product Freeze candidate
                                          ↓
                                 Final Independent Review
```

This is an **L1 research/evidence DAG**, not the formal implementation Task DAG.

The formal implementation Task DAG may only be created after:

```text
required successor L1 evidence PASS
-> Final Independent Product Review PASS
-> Product Freeze
-> L2 Architecture Evidence
-> formal Task DAG
-> implementation
```

For live execution status, use GitHub Issues/PRs as the source of truth rather than this README.

## Pinned development standard

```text
repository=kaicreator-mm/ai-development-standard
version=4.9.0
revision=7929012f36a2202dcc2edc7a414b8163adc7afbd
```

Do not implicitly follow the latest standard `main` for the frozen Product/L1 package.

## Product boundary

app8 owns the **Capability/Evidence factual authority** and its lifecycle. Generic CLI generation, MCP/Skill generation, discovery engines, evaluation infrastructure, routing, packaging and similar non-core mechanisms are reuse/harvest-first.

The product must report `UNSUPPORTED`, `BLOCKED` or `STALE` when appropriate rather than inventing support.

GitHub durable state is the project source of truth.
