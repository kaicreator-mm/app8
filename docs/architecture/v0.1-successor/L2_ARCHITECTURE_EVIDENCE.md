# app8 L2 Architecture Evidence — core baseline v0.1

Status: ARCHITECTURE_DESIGN_ADOPTED_WITH_OWNER_L1_WAIVER
Authorities: Issue #92; Issue #94; main@5f5c68bf9695c66453b4f82927e6b4155c9db76f
Empirical SE10/SE11: UNPROVEN. Release qualified: NO. Independent Product Review: OWNER_WAIVER_NOT_PASS.

## Architecture decisions

| ID | Adopted choice | Negative boundary |
|---|---|---|
| ADR01 | A single versioned Capability IR owns semantics, constraints, variants, failure modes and binding alternatives | CLI/MCP/Skill cannot maintain independent semantic truth |
| ADR02 | Append-only content-addressed Evidence store, with negative/contradictory evidence retained | Model prose and documentation alone are not real behavioral evidence |
| ADR03 | LLM-A proposes hypotheses; LLM-B proposes bounded falsification plans; deterministic execution adapter records observations; policy computes readiness | No model self-scores its plans as real observation |
| ADR04 | SQLite plus local content-addressed artifacts by default, PostgreSQL/S3 optional | No mandatory database/service cluster |
| ADR05 | Bindings: CLI, SDK/library, API, IPC/RPC, thin OSS adapter, structured UIA/accessibility | Pixel, OCR and coordinate-derived automation forbidden |
| ADR06 | Projections CLI/MCP/Skill/Agent-docs/Search derive from one immutable Capability revision and Evidence snapshot | No projection may upgrade readiness |
| ADR07 | Source/target/environment drift invalidates readiness pending revalidation | No version alias silently reuses evidence |
| ADR08 | OSS harvest/reuse-first, with license and source identity retained | LLM rewrite never erases licensing obligations |

## Contract structure

Logical types:
- Capability: id, revision, semantic job, inputs/outputs, variants, constraints, negative boundaries, failure modes, side effects; source+version+license; target/mapping; bindings; Evidence references; derived readiness.
- Evidence: claim+capability, source identity, execution target identity and mapping, fixture hash, bounded plan, real observation/hash, assessment reason, replay manifest.
- Projection: projection-kind, source Capability id/revision and Evidence snapshot, status, inherited constraints/errors/side effects, deterministic generator identity.

Machine contract skeletons: contracts/capability-v1.schema.json and contracts/evidence-v1.schema.json. JSON schema validity is NOT sufficient to qualify Evidence or ExportReady: cross-record policy and real execution checks are required.

## State/reducer policy

DISCOVERED -> HYPOTHESIZED -> EVIDENCED -> COMPILED -> EXPORT_READY is a possible happy path, not an automatic sequence.
REFUTED / BLOCKED / STALE must prevent ExportReady. A COMPILED artifact may exist before evidence but stays unready.
ExportReady must be a deterministic computed result from a current exact target, valid scoped positive real observation, satisfied assertions, no unresolved material counterevidence, and projection provenance.
Only append-only events may change Evidence and readiness history. A positive probe never overwrites refutation.

## Orchestration and execution

discovery -> LLM-A hypothesis -> LLM-B adversarial plan -> strict executable plan freeze -> sandbox execution -> observation -> evidence assessment -> Capability state -> projections.
LLM-A and LLM-B may generate text and test plans. Neither can certify behavioral facts; only deterministic real observations/authorized human operator evidence may supply them.
Execution adapters enforce per-test time, output size, network and side-effect allowances; default network and destructive mutation DENY.
Separate Knowledge Source revision from Execution Target version/hash. DIVERGED or UNRESOLVED requires target applicability proof before promotion.
Semantic UIA/accessibility nodes allowed where available; pixel-derived fallback forbidden.

## Negative tests required in formal Task DAG

| ID | Counterexample | Required failure behavior |
|---|---|---|
| N01 | LLM text but no execution | NOT_EXPORT_READY |
| N02 | Model self-certification of Evidence | REJECT_EVIDENCE_AUTHORITY |
| N03 | Exit status 0 but expected artifact absent | NOT_EVIDENCED |
| N04 | Frozen source newer/older than target | REQUIRE_MAPPING_APPLICABILITY |
| N05 | Target checksum or environment drift | STALE/BLOCKED |
| N06 | Material refutation not resolved | PREVENT_EXPORT_READY |
| N07 | Pixel/OCR/coordinate UI discovery | REJECT_BINDING |
| N08 | Projection built from different Capability revision | REJECT_PROJECTION_DRIFT |
| N09 | Secret truth fixture visible to planner in a blind evaluation | INVALIDATE_EVALUATION |
| N10 | AI design seed passed off as independent Gold | REJECT_EVIDENCE_ORIGIN |
| N11 | Unapproved network or mutation | DENY_EXECUTION |
| N12 | OSS-derived module without license provenance | HOLD_REUSE |

## Source-asset adoption

- SE10 frozen 76-file source pack blob 4b3c9b62b1899653524f19a286924f942605210a -> discovery/provenance test asset.
- SE10 Stage B/Stage C (#85 and unmerged hardening PR #90) -> validator/scorer negative-test patterns; no empirical success claim.
- SE11 Stage-A merge 0279968580d50e51843b09aa2b6e266b9967ff93 plus Stage B/C -> target mapping, isolation and replay contract patterns.
- #69 official LibreOffice runtime operator-reported complete; public manifest/redacted evidence not yet in GitHub. Never fabricate or reinstall.
- SE12 projection invariants, SE14 BM25 64 index items and 48 queries, SE15 non-pixel binding, SE16 adoption instrument -> mapped downstream per Adoption Matrix.
- Model-authored 16-case seed pack -> REFERENCE_ONLY illustrative contract inputs, NOT real evidence, hidden truth or Gold.

## L2 scope closure

Architecture decisions and contract schemas are accepted under #92 owner's explicit no-human-review process waiver. This is L2 **design** completeness, not runtime or release qualification.
Before formal Implementation Task DAG: record exact architecture blob/SHA; source-to-L2 adoption; test matrix; open risks and module write boundaries.
Real target testing and empirical SE10/SE11 accuracy are L3/Release acceptance gates, not L2-entry gates.

ARCHITECTURE_DESIGN=ADOPTED_WITH_OWNER_WAIVER
REAL_EXECUTION_VALIDATION=NOT_CLAIMED
RELEASE_READY=NO
