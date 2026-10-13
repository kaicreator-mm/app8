# app8 — Evidence-backed Software Capability Compiler

app8 aims to turn existing software knowledge and **real observed behavior** into reusable Capabilities, then project a single factual authority into CLI, MCP, Skill, Agent documentation and search.

## Current delivery state: v0.1.0a0 technical-preview candidate

| Area | Status |
|---|---|
| Product definition | Scope/design owner-approved (#92); empirical qualification not claimed |
| L2 architecture | ADR01–ADR08 adopted (#94 / PR #96) |
| Implementation Task DAG | 9/10 source tasks implemented; real-host/release #107 remains |
| Python package | Source/doc discovery, hypothesis and falsification plan freezing, SQLite evidence ledger, readiness reducer, in-memory BM25, projection metadata, CLI preview |
| Windows real-host validation | R1: 83/84 tests; CRLF test and frozen JSON byte issues fixed in PR #120; R2 pending |
| Ubuntu real-host validation | R1: 84/84 tests, wheel install and CLI smoke PASS |
| LibreOffice official target | #69 26.8.1.1 install identity/non-evaluative smoke documented, scope PASS |
| OS-level sandbox | **BLOCKED** on both hosts; no verified network/filesystem containment backend |
| SE10/SE11 empirical studies | **UNPROVEN** |
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
- `app8.execution` is currently an experimental exact-binary subprocess **observation adapter**, **not** an OS sandbox. Do not pass untrusted model-generated commands or treat caller-supplied isolation flags as verified boundaries. Automatic real execution is not release-qualified.
- No human independent review is required for L1/L2 scheduling by product-owner decision #92; this is a documented waiver, not an independent-review PASS.
- Existing human Gold/hidden truth protocols and adversarial studies are preserved as deferred release-quality research assets; results must not be invented.

### Authoritative references

- [Product PRD and owner r3 decision](docs/product/v0.1-successor/PRD.md)
- [Owner r3 product scope/evidence split](docs/product/v0.1-successor/L1_OWNER_DESIGN_FREEZE_R3.md)
- [L2 architecture decisions](docs/architecture/v0.1-successor/L2_ARCHITECTURE_EVIDENCE.md)
- [Formal implementation Task DAG](docs/implementation/v0.1-successor/TASK_DAG.md)
- [Release qualification](https://github.com/kaicreator-mm/app8/issues/107) and [deferred empirical work](https://github.com/kaicreator-mm/app8/issues/95)

The older `docs/product/v0.1/` Admission/Governance product thesis is superseded. Historical SE10–SE16 protocols and evidence remain retained, but are not current pre-L2 gates. GitHub exact commits and Issue terminals are the live state authority.
