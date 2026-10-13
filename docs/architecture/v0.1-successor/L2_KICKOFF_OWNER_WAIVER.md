# app8 L2 Architecture Kickoff — owner-waived entry

Status: ARCHITECTURE_WORK_AUTHORIZED / DECISIONS_PROPOSED_NOT_IMPLEMENTED  
Authority: #92, `L1_OWNER_DESIGN_FREEZE_R3.md`.  
Scope: product-design entry, not evidence-validation PASS.

## Design spine

```text
Software Source/Manifest
  -> Discovery/source adapters (Q-L2-S03)
  -> LLM-A semantic Capability hypothesis (Q-L2-S04)
  -> Adversarial Plan from LLM-B (Q-L2-S04)
  -> Bounded deterministic real execution (Q-L2-S05)
  -> Immutable scoped Evidence observations (Q-L2-S02)
  -> Claim adjudication / falsification (Evidence != model confidence)
  -> Capability IR + readiness policy (Q-L2-S01)
  -> deterministic/reused projections (Q-L2-S06/07/09)
  -> currentness/revalidation (Q-L2-S10)
```

No production implementation is authorized merely by this kickoff. L2 must resolve interface contracts and negative cases before Task DAG.

## Proposed first three contract slices

**L2-C01: Capability IR (Q-L2-S01).** Versioned JSON schema; immutable Capability ID; semantic job, input/output, constraints, side effects, failure modes, binding variants, provenance, evidence pointers; lifecycle DISCOVERED → HYPOTHESIZED → EVIDENCED → COMPILED → EXPORT_READY. REFUTED/BLOCKED/STALE are explicit invalidating states; readiness is computed, never accepted from LLM prose.

**L2-C02: Evidence envelope (Q-L2-S02/05).** Required: claim id/hash; source revision/blob; execution-target binary/container checksum; source↔target mapping/relation; environment/OS/dependencies; fixture/checksum; bounded invocation; result stdout/stderr/state/artifact hashes; replay; observer; outcome; timestamp/currentness. Exclude secrets and unsafe/destructive probe categories by default. Append-only observation/events. SQLite + local artifact store default; PostgreSQL adapter optional. Source-authority/protocol files are retained examples, not production services.

**L2-C03: Harness + projection contract (Q-L2-S04/06).** LLM-A proposes hypotheses; LLM-B plans falsification; execution adapter alone may assert observation; adjudicator consumes observation but cannot rewrite it. CLI/MCP/Skill/Docs/Search projections consume the same snapshot, cannot upgrade readiness or fork semantic authority.

## Reuse adoption

| Existing asset | Planned L2 use |
|---|---|
| SE10 source pack 76 anchors + `research/e10/stage-b` | source identity/provenance validator patterns |
| SE10 Stage C #85 and #90 | predicted semantics/scoring negative fixtures, not evidence authority |
| SE11 Stage A logs/manifest | target/runtime/fixture/replay envelope exemplar |
| SE11 Stage B/C | claim commitments, plan isolation, no-self-score patterns |
| #69 Windows release identity script | native host target identity adapter reference; import SHA later |
| SE12 | projection invariants/tests in L2-C03 |
| SE14 64-item/48-query BM25 | Q-L2-S09 ranking benchmark seed |
| SE15 | non-pixel structured-UI binding adapter and negative cases |
| SE16 | later Product/Release market evidence, not architecture blocker |
| `research/design-seeds/core_capability_scenarios_v1.json` | MODEL_AUTHORED_DESIGN_SEED only; 16 candidate positive/negative/overbroad/boundary fixtures |

## Architecture stop/go

Proceed with contract design under owner waiver. Before closing L2 and authorizing Task DAG, check schema fixtures, negative cases, executable contract tests, exact artifacts and reused asset dispositions. Do not mislabel synthetic tests as SE10/SE11 empirical PASS. Release Qualification must independently bind real observations.
