# app8 — Evidence-backed Software Capability Compiler

app8 aims to turn existing software knowledge and **real observed behavior** into reusable Capabilities, then project a single factual authority into CLI, MCP, Skill, Agent documentation and search.

## Current delivery state: v0.4 empirical evaluation reentry (package: v0.1.0a0 alpha)

[v0.3 two-environment real CPython pilot terminal](docs/release/v0.3/REAL_CPYTHON_PILOT_TERMINAL.md): Windows Docker Desktop and Ubuntu WSL2 native Linux Engine P01/N01 scoped signed Evidence PASS, F01 signed REFUTED, B01 drift BLOCKED; Windows full pytest 200 passed / 1 skipped; Ubuntu targeted 20/20 PASS. **These are two runtime environments, not independently proven physical machines.** [v0.2 security engineering terminal](docs/release/v0.2/SECURE_EXECUTION_SCOPE_TERMINAL.md) and [v0.1 technical preview](docs/release/v0.1/TECHNICAL_PREVIEW_TERMINAL.md) are retained. **Full Product Release PASS has not been demonstrated.**

| Area | Status |
|---|---|
| Product definition | Scope/design owner-approved (#92); empirical qualification not claimed |
| L2 architecture | ADR01–ADR08 adopted (#94 / PR #96) |
| Task DAG | Engineering **18/18 scoped PASS**; v0.4 **1/4 formal Task complete, 3/4 open**; support #157/#158 completed via merged PR #159/#160 with exact-host tests; **0/2 empirical studies PASS**; formal Release NO |
| Python package | Source/doc discovery, hypothesis and falsification plan freezing, SQLite evidence ledger, readiness reducer, in-memory BM25, projection metadata, CLI preview |
| Windows host validation | v0.1 R2 84/84; v0.2 Docker isolation 11/11, trusted runner R1 21/21; Evidence-integrity fix 72/72 source tests |
| Ubuntu WSL2 validation | v0.1 R2 84/84; v0.2 Docker isolation 11/11, runner R1 21/21; v0.3 source identity verified, 20/20 targeted qualification and scoped signed JSON pilot PASS |
| LibreOffice official target | #69 26.8.1.1 install identity/non-evaluative smoke documented, scope PASS |
| OS-level sandbox | **Scoped PASS** on documented Windows/Ubuntu Docker hosts and fixed digest-pinned policy; no blanket security certification |
| Trusted Evidence | Privileged Docker runner, signed v2 receipts, durable nonce and SQLite ingress; real pinned JSON Capability scoped PASS on Windows and Ubuntu WSL2 |
| SE10/SE11 empirical studies | **NOT_RUN / BLOCKED**: independent SE10 Gold + separate reviewer attestation absent; SE11 approved final target/applicability and independent 80-claim hidden truth absent. Public structural preflight and Stage B tests PASS, not empirical evidence |
| Full release qualification | **NO** |

The installed `app8` CLI currently produces **`ILLUSTRATIVE_UNVERIFIED` Capability previews**, not authorized executable exports. CLI/MCP/Skill/Docs/Search projections are metadata representations of a single Capability snapshot, not working MCP/Skill installers or complete runtime adapters.

### Quick start (source/package preflight)

Requires Python 3.11+, `jsonschema` and `setuptools` available in the environment.

```bash
python -m pip install -e . --no-build-isolation
app8 --help
python scripts/release_preflight.py --out app8-preflight.json
```

The preflight runs nine unit/integration suites, builds an offline wheel, checks exact frozen L2 schema content hashes and its CLI entrypoint, and explicitly reports `release_qualified=false`. It does **not** verify operating-system sandbox isolation or real-software Capability quality. Do not represent a passing preflight as Release PASS.

The preview CLI requires an **exact source SHA256**, source revision and explicit model-output hypothesis/plan JSON files; see `tests/integration/test_preview.py` for executable fixtures. Output stays `real_execution_status=NOT_RUN`, `release_ready=false`. No claim can be promoted to `EXPORT_READY` from model prose alone.

### Safety boundaries

- Source snapshot, execution binary and environment are separate identities; evidence is version/scope-bound.
- Model-produced Capability hypotheses and test plans are **proposals**, never behavioral evidence.
- Refuted, blocked, stale or unobserved claims cannot become `EXPORT_READY`.
- Pixel/OCR/coordinate-driven automation is forbidden; structured semantic UI adapters may be supported later.
- The unsafe direct `app8.execution.adapter.run_invocation` path is **disabled**. `app8.execution.docker_runner.RealDockerRunner` is an operator-provisioned, digest-pinned real-host runner, **not a model-callable API**. It requires a reviewed image/command allowlist, actual Docker isolation and a private signing key. A successful synthetic smoke does not prove general Capability quality or formal release readiness.
- No human independent review is required for L1/L2 scheduling by product-owner decision #92; this is a documented waiver, not an independent-review PASS.
- Existing human Gold/hidden truth protocols and adversarial studies are preserved as deferred release-quality research assets; results must not be invented.

### Authoritative references

- [Product PRD and owner r3 decision](docs/product/v0.1-successor/PRD.md)
- [Owner r3 product scope/evidence split](docs/product/v0.1-successor/L1_OWNER_DESIGN_FREEZE_R3.md)
- [L2 architecture decisions](docs/architecture/v0.1-successor/L2_ARCHITECTURE_EVIDENCE.md)
- [Current Task DAG (18 scoped engineering PASS + 4 v0.4 terminalized)](docs/implementation/CURRENT_TASK_DAG.md), [v0.4 empirical BLOCKED terminal](docs/release/v0.4/CORE_EMPIRICAL_TERMINAL.md), [SE10/SE11 research reuse audit](docs/release/v0.4/SE10_SE11_REUSE_AUDIT.md), [original v0.1 Task DAG](docs/implementation/v0.1-successor/TASK_DAG.md)
- [v0.2 secure execution terminal](docs/release/v0.2/SECURE_EXECUTION_SCOPE_TERMINAL.md), [v0.1 technical preview](docs/release/v0.1/TECHNICAL_PREVIEW_TERMINAL.md) and [historical deferred empirical work](https://github.com/kaicreator-mm/app8/issues/95)

The older `docs/product/v0.1/` Admission/Governance product thesis is superseded. Historical SE10–SE16 protocols and evidence remain retained, but are not current pre-L2 gates. GitHub exact commits and Issue terminals are the live state authority.
