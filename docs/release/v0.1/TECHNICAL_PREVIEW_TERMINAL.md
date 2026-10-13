# app8 v0.1.0a0 — Technical Preview Scope Terminal

Status: **TECHNICAL_PREVIEW_CANDIDATE_ACCEPTED / FORMAL_RELEASE_NOT_QUALIFIED**  
Owner-directed design gate: Issue #92; L2 architecture adopted #94 / PR #96.  
Validated source subject (pre-this-record): `bef2014f0184117b77e724389970c72632afa86c`.  
Validated cross-host R2: Issue #95 comment `6145343021`.  
Baseline comparison / Windows F1/F2: Issue #107 comment `6143243171`; fix PR #120.  
LibreOffice execution-target-only freeze: Issue #69, terminal imported from #107 R1.

## Shipping classification

```text
DELIVERY_CLASS=SOURCE_AND_WHEEL_TECHNICAL_PREVIEW_CANDIDATE
VERSION=0.1.0a0
TECHNICAL_PREVIEW_SOURCE_PACKAGE_R2=PASS
FULL_RUNTIME_CAPABILITY_COMPILER=NOT_PROVEN
AUTOMATED_UNTRUSTED_EXECUTION=NOT_AUTHORIZED
REAL_BEHAVIORAL_CAPABILITY_EXPORT=NOT_QUALIFIED
FORMAL_RELEASE_QUALIFICATION=NO
PRODUCT_EMPIRICAL_SE10=UNPROVEN
PRODUCT_EMPIRICAL_SE11=UNPROVEN
INDEPENDENT_HUMAN_REVIEW=OWNER_WAIVED_NOT_PASS
```

This record **does not** publish a signed artifact, GitHub Release or semver tag. `0.1.0a0` is the package's existing alpha version, not a claimed full release.

## Verified on exact R2 source

| Gate | Windows 11 Python 3.14.7 | Ubuntu 26.04.1 WSL2 Python 3.14.4 | Authority |
|---|---|---|---|
| Nine unit/integration suites | **84/84 PASS** | **84/84 PASS** | Issue #95 R2 comment 6145343021 |
| Local source/package preflight exit | 0, `errors=[]` | 0, `errors=[]` | same |
| Frozen schema bytes | LF, SHA matched | LF, SHA matched | same |
| Offline wheel | PASS | PASS | same |
| Frozen schema embedded in wheel | MATCH | MATCH | same |
| Installed `app8 --help` | EXIT 0 | EXIT 0 | same |
| Actual real-software semantic/evidence experiment | NOT_RUN | NOT_RUN | not part of R2 |
| OS-level network/filesystem sandbox | **BLOCKED** | **BLOCKED** | #107 R1 escape probes |

Frozen L2 contract content hashes:
- Capability: `9e784ed03985d8357b8d96cb978acc18fe38a694988d7401300fde5ee7daa4c7`
- Evidence: `c3b88f973b3963c8f893750e71b0cbee2aac1dfe1f3b58011e9e7ba67e35728a`

Wheel file SHA256 is **not expected to be reproducible across Windows/Ubuntu**, because wheel zip metadata/timestamps differ; judge frozen schema payload bytes and installed package behavior separately.

## Official LibreOffice target

Existing Windows official LibreOffice 26.8.1.1 installed with ProductCode `{87B289F9-6172-4C3D-A091-EE36A40E1287}`, verified official MSI SHA256 `c6298b10cfa1748bcbedad94c62ce771e240e5021bfd6d7a967cd571b04b5312`; non-evaluative `soffice --headless --version` smoke EXIT 0. Private runtime manifest SHA256 `38595986f5ae39518891649ea484c582c268a61a41c9df470366b0060e63a63c`; hash receipt at #69/#107. **No reinstall or repeat smoke required for this scope.** This does not verify SE11 falsification accuracy, UI bindings or a sandbox.

## Alpha API boundaries

Allowed for **technical preview**:
1. Read exact SHA256-bound source text and construct model-origin capability hypotheses.
2. Strictly freeze model-designed positive/negative falsification plans.
3. Produce unready Capability/package projection metadata for CLI/MCP/Skill/docs/search; inspect offline preview with `app8`.
4. Build and inspect local wheel/schema data and exercise deterministic tests; use SQLite evidence ledger for developer-controlled fixtures.

Not represented as validated:
- Real executable MCP server, installed Skill runtime, stable user API or successful Agent utility;
- verified host network/filesystem confinement or streamed hard output limits;
- empirical SE10 semantic coverage/precision and SE11 claim falsification success;
- any `EXPORT_READY` Capability sourced solely from model text or synthetic fixtures.

**Prohibition:** Until an OS-constrained runner with verified least-privilege controls exists, model-authored or untrusted commands must not be dispatched through the experimental `app8.execution.adapter`. Caller-provided `network_isolation_verified`/`filesystem_isolation_verified` booleans are **not proof**. A process reaching host network or escaping a working directory was observed at #107 R1. This is an actual security limitation, not an optional documentation gap.

## Deferred release blockers, retained evidence

| Obligation | Explicit status | Source / downstream |
|---|---|---|
| Cross-platform OS sandbox network and filesystem containment; hard stdout limit | BLOCKED, release blocking | #107 escape evidence; retained #95 |
| Empirical SE10 capability extraction effectiveness | UNPROVEN | SE10 source pack, Stage B/C scorer; old PR #90 is closed **unmerged**, do not use vulnerable scorer |
| Empirical SE11 falsification against real behavior | UNPROVEN | #69 real target, original Stage A/B/C tools, private/hidden-truth method retained |
| Actual CLI/MCP/Skill execution and integration | UNPROVEN | SE12 and L3 acceptance, projection metadata alone insufficient |
| SE13 agent utility, SE14 search quality, SE15 non-pixel real binding, SE16 adoption | UNPROVEN_DEFERRED | L1→L2 Adoption Matrix |
| Compliance with independently human-reviewed Product gate | OWNER_WAIVER_NOT_PASS | #92 |

## Closure decision

Scope decision: `v0.1.0a0` **technical preview implementation + cross-platform source/package validation are completed**. Full behavioral/security/release qualification is **not completed**, and must be evaluated under separate qualification authority before enabling automated real execution or making evidenced Product claims.

```text
TECH_PREVIEW_R2_TESTS=168/168_PASS_ACROSS_2_HOSTS
TECH_PREVIEW_WHEEL_AND_CLI=PASS_BOTH_HOSTS
OS_SANDBOX=BLOCKED
EMPIRICAL_SE10_SE11=UNPROVEN
RELEASE_READY=NO
NO_REPEAT_ALREADY_COMPLETED_INSTALL_OR_R2=YES
```
