# App8 v0.4 — Capability Compiler MVP L2 delta (R1)

> Product target: [CC-MVP scope](../../product/v0.4/CAPABILITY_COMPILER_MVP_SCOPE_R1.md). **Status: DESIGN_CANDIDATE_FOR_INDEPENDENT_REVIEW**. Existing `capability-v1` and `evidence-v1` source contracts are pinned, unchanged. This document approves no unsafe runtime. No new mandatory governance subsystem or architectural platform.

## 1. Existing module reuse and only needed interfaces

| Stage | Reused current source | Narrow missing integration |
|---|---|---|
| Pin/read | `app8.discovery.discover_source` | Bounded multiple context fragments only if demanded by chosen job; source hash stays exact |
| Understand/plan | `app8.orchestration.freeze_hypotheses`, `freeze_falsification_plan`, `scripts/v04_mla_app8_p_ingress.py` | Minimal model-proposal→user-job semantic/compiler assembler. Model output, retrieved source and bindings stay untrusted until typed checks; retain P-role provenance |
| Observe/verify | `app8.execution.docker_runner.RealDockerRunner`, `app8.evidence.ingress.import_signed_observation`, `EvidenceStore`, `AttestationGate` | Specific source/target/binding/case mapping; only genuinely runner-attested observations admitted; use existing R24/#150 reference observations as *candidate* not auto-signed Evidence |
| Readiness/compiler | `app8.qualification.qualify_stored_capability`, `app8.readiness.evaluate_readiness` | Durable one-Capability assembly including all negative/stale events; existing `SCOPED_EXPORT_READY` behavior retained |
| Project/search | `app8.projections.build_projections` and `CapabilityIndex` | Metadata-to-runnable **one** narrow consumer with typed request/result and allowlisted target; preserve identical Capability revision/source/evidence SHA |
| Consume/reuse | Current trusted runner through a controlled adapter | One real Agent/CLI usage plus second independent use reading a persisted Capability; do not add generic `subprocess` executor or treat `invocation_enabled` as authorization |

**Explicit existing gaps**: `app8/cli/main.py:_candidate_capability` fills semantic inputs/outputs as empty lists and has `bindings=[]`, `license_disposition=UNKNOWN`, mapping `UNRESOLVED`. Current CLI is an **unverified preview**. `app8/projections/render.py` outputs CLI/MCP/Skill **descriptions**, not installed/runnable interfaces. `app8/execution/adapter.py:run_invocation` deliberately blocks unsandboxed execution. `app8/qualification/service.py` requires verified signed sidecars and `mapping_relation=SAME`. **None of those can be bypassed in the MVP.**

## 2. Minimal safe data contracts / constraints

- **Candidate envelope:** `source_sha256`, immutable `hypothesis_sha256`, `origin` and prompt/model provenance if available; user job + semantic I/O/constraints; target package sha and `mapping_relation`; intended binding ID, kind and schema; `observation_status=NOT_RUN` until reality is checked. `MODEL_PROPOSAL_ONLY` never claims evidence. Prefer existing schema fields; introduce an app8-specific schema only when truly missing.
- **Proof envelope:** `capability_id/revision`, exact source and target/effective version, admitted `binding_id`, fixture, independent positive+negative assertions, real runner receipt / verifier-owned signature and nonce DB; `EvidenceStore` event history including refutations. A useful FFmpeg004 prior R24 observation does not equal a signed `app8-evidence-v1` receipt until genuine attestation and claim mapping are established.
- **Capability package:** `app8-capability-v1`, `app8-evidence-v1`, frozen semantic SHA, source/target identity, Evidence digest, scoped computed readiness and concrete target binding. Retain all negative evidence. Only a valid `SCOPED_EXPORT_READY` can become an active consumer target.
- **Runnable consumer:** structured arguments validated against the selected Capability binding; target is read from stored trusted binding/manifest, never from a caller-supplied executable path. One already trusted runner/connector with actual permission boundaries performs invocation. Return typed output/error, consumed Capability revision and evidence digest, observable target/fixture result. No shell injection, no assumed identity from a raw JSON boolean; no implicit install/network/mutation rights.
- **Persistence/reuse:** second task or agent loads exactly the same signed/reviewed Capability/target mapping from existing storage and consumes without rerunning model prompt or parsing source. Refuted/stale / unsafe proposal returns non-invocable outcome.

## 3. No duplicate platform extraction

Use Python stdlib/jsonschema already installed and existing runner + SQLite HMAC chain; mature FFmpeg/pandas native interfaces for real work. FFmpeg CLI should use direct argv via approved isolated runner; pandas library through existing reviewed Python path. No new model dispatcher, S3 client, auth framework, headless UI runtime or high-order plugin SDK. If reusing older evidence fails for a precise case, prefer one minimal bounded real Host execution to months of new evidence trust infrastructure.

## 4. Test seams and version closure

- Unit/contract tests: model-only never ready; extra/missing I/O; malicious executable/argv; source hash drift; stale version; mismatched binding; negative evidence; unavailable projection; cannot invoke when not ready.
- Real host qualification: limited FFmpeg + pandas with independent output expectations, one positive and one negative per chosen Capability; existing #150 observations reused if compatible, new run only for actual missing admissible receipt or consumer effect.
- Integration: one code path source→candidate→evidence→Capability→real consumer→second use; counts and typed failures in a scoped report. Do **not** score unverified source quotations as semantics or metadata as runnable MCP.
- Version state: Product/L2 independent review for scoped acceptance, focused PR tests per lane, one full version regression + independent scoped Release Qualification, only then consider `version/v0.4`→`main`. CI absence is `WAIVER/NOT_RUN` with truthful alternative Host receipts, never simulated success.

## 5. Architecture stop condition

If an enhancement does not directly unblock one of **two demonstrable real consumer journeys**, refuse it unless required to prevent a credible P0 safety defect. Deferred advanced benchmark/MinIO/LibreOffice work cannot silently become a CC-MVP dependency. A scoped capability may remain `BLOCKED`; that is an accurate negative result, not a license to fabricate observations.
