# L2 Question Register — app8 v0.1 Successor

Status: DRAFT_FOR_INDEPENDENT_REVIEW  
Product Freeze: NO  
L2 Ready: NO

This register records candidate architecture questions only. It cannot redefine Product/L1.

## Transfer rule

A question is L2_REQUIRED only if a negative answer for one implementation path would cause architecture pivot rather than falsify SPCL-001..007 or a product invariant.

## Candidate L2 questions

### Q-L2-S01 — Capability IR representation

How should Evidence-backed Capability, variants, constraints, bindings, provenance and export projections be represented and versioned?

Constraint: the representation must preserve SINV-003/004/005/009.

### Q-L2-S02 — Evidence store / replay format

What storage, content-addressing, lineage and replay mechanism should hold source claims, fixtures, observations, results and refutations?

Product/L1 determines what evidence is sufficient; L2 determines the mechanism.

### Q-L2-S03 — Source/surface adapter architecture

How are documentation, CLI, library, API, source, binary, IPC and semantic-UI analyzers plugged into a common discovery pipeline?

This cannot reduce the successor input domain without L1 disposition.

### Q-L2-S04 — LLM orchestration

How are LLM-A capability analysis, LLM-B evidence planning and LLM-C export synthesis implemented, routed, cached and constrained?

Model choice is L2 unless L1 evidence shows the product claim depends on a specific model capability/cost.

### Q-L2-S05 — Test/execution harness

What sandbox/process/container/host mechanism executes generated tests and captures observations across supported environments?

This is not an Admission/Governance product boundary.

### Q-L2-S06 — Exporter architecture

How are CLI, MCP, Skill, Agent docs and search metadata generated from one frozen capability/evidence authority while preventing semantic drift?

If no plausible architecture can satisfy one-model-many-exports, that becomes L1_BLOCKING rather than deferred.

### Q-L2-S07 — Structured semantic UI adapter

How should Windows UI Automation/accessibility trees, semantic DOM roles or equivalent structured UI surfaces be discovered, stabilized and invoked?

Hard product constraint: no pixel-derived fallback.

### Q-L2-S08 — Reverse engineering and fork lifecycle

How are recovered internal interfaces, generated shims and minimal OSS forks tracked against upstream versions and optionally upstreamed?

Legal/license/access-control policy remains a product/process constraint, not an implementation loophole.

### Q-L2-S09 — Search/index implementation

Which lexical/vector/graph/hybrid index and ranking architecture should serve natural-language capability search?

SPCL-005 relevance/readiness behavior is Product/L1; storage/ranking implementation is L2.

### Q-L2-S10 — Currentness / regeneration

How are docs, software versions, evidence and exports invalidated/rebuilt when the upstream software changes?

Currentness mechanics are L2; silently treating stale evidence as current is forbidden by successor evidence semantics.

## Current terminal

~~~text
L2_READY = NO
NEXT = successor Product/L1 independent review and L1 evidence
~~~
