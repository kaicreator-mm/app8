# L2 Question Register — app8 v0.1 Successor r2

Status: READY_AFTER_CORE_PRODUCT_FREEZE  
Product Freeze: NO  
L2 Ready: NO  
Convergence authority: Issue #80

This register records candidate architecture questions only. It cannot redefine Product/L1.

## Transfer rule

A question is L2_REQUIRED if a negative answer for one implementation path causes architecture pivot rather than falsifying the core Product thesis or a Product invariant.

Under convergence r2, SPCL-003/SPCL-005/SPCL-006 are validated alongside the corresponding L2 architecture questions. A negative downstream result may narrow those deferred claims without retroactively invalidating SPCL-001/SPCL-002 unless it exposes a core contradiction.

## Candidate L2 questions

### Q-L2-S01 — Evidence-backed Capability IR

How should Capability semantics, variants, constraints, bindings, evidence refs, provenance, currentness and projections be represented and versioned?

The representation must preserve Product invariants around negative evidence, scoped evidence, one factual authority and historical evidence.

### Q-L2-S02 — Evidence store / replay

What storage, content-addressing, lineage and replay mechanism should hold source claims, fixtures, observations, artifacts, results and refutations?

Product/L1 determines what evidence is sufficient; L2 determines the mechanism.

### Q-L2-S03 — Discovery module architecture

How are documentation, CLI, library, API, source, binary, IPC, Web/Electron and semantic-UI discovery modules composed?

The architecture may reuse/harvest mature OSS. It cannot reduce the Product input domain without L1 disposition.

### Q-L2-S04 — LLM-A/B/C orchestration

How are UNDERSTAND, FALSIFY and COMPILE implemented, routed, cached, prompted and constrained?

Model/provider choice is L2 unless L1 evidence shows the Product claim depends on a specific model/cost envelope.

The architecture must keep real behavioral observation distinct from model judgment.

### Q-L2-S05 — Deterministic execution harness

What sandbox/process/container/host mechanism executes generated tests, captures observations and binds evidence to the actual software/environment?

This is not an Admission/Governance product boundary.

### Q-L2-S06 — Projection/export architecture

How are CLI, MCP, Skill, Agent docs and search metadata generated from one frozen Capability/Evidence authority while preventing semantic drift?

Projection providers may be:

- app8-native;
- reused OSS;
- harvested/reimplemented modules;
- external generators behind a contract.

SE12 is the retained executable validation for this question. If no plausible architecture can satisfy one-authority-many-consumers, narrow SPCL-003 or reopen Product authority only if the failure also contradicts the frozen core thesis.

### Q-L2-S07 — Structured semantic UI binding

How should Windows UI Automation/accessibility trees, semantic DOM roles or equivalent machine-readable UI surfaces be discovered, stabilized and invoked?

Hard Product constraint: no pixel-derived fallback.

SE15 assets are the retained validation input for this question; source-only curator/binding work must be reused rather than regenerated.

### Q-L2-S08 — Reverse engineering and fork lifecycle

How are recovered internal interfaces, generated shims and minimal OSS forks tracked against upstream versions and optionally upstreamed?

Authorization/license/access-control policy is not an implementation loophole.

### Q-L2-S09 — Capability search/index

Which lexical/vector/graph/hybrid index and ranking architecture should serve natural-language Capability search?

SPCL-005 remains an explicit deferred claim. SE14's frozen 64-item corpus, 48 queries, fairness gates and BM25 harness are retained L2/L3 validation assets; the production index/ranker remains an L2 choice.

### Q-L2-S10 — Currentness / revalidation

How are docs, software versions, evidence, bindings, capabilities and projections invalidated/revalidated when upstream software changes?

Silently treating stale evidence as current is forbidden.

### Q-L2-S11 — LLM-0 ecosystem/module harvesting

How should app8 analyze open-source projects and extract reusable engineering patterns or module candidates without becoming a runtime bundle of upstream projects?

The architecture should support three dispositions:

~~~text
LEVEL_1_PATTERN
LEVEL_2_REIMPLEMENTED_MODULE
LEVEL_3_DIRECT_REUSE
~~~

Required concerns include:

- source/provenance identity;
- license classification;
- functional-contract extraction;
- clean separation between learned pattern and source-derived code;
- independent module validation;
- KEEP / ADAPT / DIRECT_REUSE / DROP decision;
- upstream version/currentness.

Failure to automate this lane may fall back to curated patterns/direct reuse and does not by itself falsify the Product.

### Q-L2-S12 — Harvested module contract registry

What common module contracts should exist for discovery, evidence acquisition, validation, projection and evaluation so extracted/reused functionality can remain replaceable?

Possible module families include:

~~~text
discovery/*
knowledge/*
evidence/*
evaluation/*
projection/*
binding/*
~~~

The register must not become a second Capability authority.

### Q-L2-S13 — License/provenance enforcement

What machine-readable records/checks should ensure:

~~~text
LLM_REWRITE != LICENSE_ERASURE
~~~

and distinguish:

- inspiration/pattern;
- functional-spec reimplementation;
- modified/derived source;
- vendored/direct dependency?

This is primarily architecture/process enforcement. Legal conclusions for specific upstreams may require separate review.

## Current terminal

~~~text
L2_READY = NO
ENTRY_GATE = SE10_PASS + SE11_PASS + FINAL_CORE_PRODUCT_REVIEW_PASS + PRODUCT_FREEZE
DEFERRED_L2_VALIDATION = SE12,SE14,SE15
DEFERRED_L3_RELEASE_VALIDATION = SE13
DEFERRED_PRODUCT_RELEASE_VALIDATION = SE16
NEXT = finish core L1 only, then start L2
~~~
