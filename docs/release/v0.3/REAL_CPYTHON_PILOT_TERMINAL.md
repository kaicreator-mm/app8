# app8 v0.3 — Real CPython JSON pilot, host-scoped verification

**Status: WINDOWS_REAL_HOST_PASS / UBUNTU_INCREMENTAL_NOT_YET_RUN / FULL_RELEASE_NO**

Controller: [#138](https://github.com/kaicreator-mm/app8/issues/138); real-host task [#140](https://github.com/kaicreator-mm/app8/issues/140).
Pilot executable PR [#143](https://github.com/kaicreator-mm/app8/pull/143), verified exact HEAD `7bb6435c2112a9980b48d909f7f3af1f0d314961`, tree `d8ed1a6890bb4d2cd75c346c86f50355826dd2fc`, merged to `f4c1692c73aac76ec127e45f5fc8d48d68bbd2e6`.
Operator redacted terminal: [Issue #140 comment 6153563183](https://github.com/kaicreator-mm/app8/issues/140#issuecomment-6153563183). Raw logs, HMAC secret, EvidenceStore SQLite and artifacts remain private.

## Windows Docker Desktop terminal (real host)

- Exact HEAD qualification suite: **20/20 PASS**.
- Full repository `python -m pytest tests -q`: **200 PASS, 1 SKIP** (Windows symlink privilege unavailable; not counted as PASS).
- Docker Linux daemon/client 29.7.2, verified Docker client SHA256 `60028870931ea6e91955bfeaee358ec6c6920f6162c17a3d828c3c82ab3c3599`.
- Cached image `library/python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b`; `--pull=never`, `--network=none`, read-only, non-root, no host mounts.
- Source measured inside executed image: CPython 3.12.15, `/usr/local/lib/python3.12/json/__init__.py`, SHA256 `d5d41e2c29049515d295d81a6d40b4890fbec8d8482cfb401630f8ef2f77e4d5`.
- Operator license disposition: PSF-2.0 review recorded; this statement is scoped to the observed image/source, not broad upstream repo certification.

| Probe | Actual observed verdict | Capability disposition |
|---|---|---|
| P01 normal JSON canonicalization | EXECUTED, SUPPORTED, ASSERTIONS_PASSED | **SCOPED_EXPORT_READY** |
| N01 malformed JSON boundary | EXECUTED, SUPPORTED (independent error behavior claim) | **SCOPED_EXPORT_READY** for its separate boundary claim |
| F01 deliberately false assertion | EXECUTED, REFUTED with failed sentinel assertion | BLOCKED, signed refutation preserved |
| B01 target SHA drift | **BLOCKED_PRE_SPAWN** | No execution/no signed observation/no promotion |

Three attested Evidence records (2 SUPPORTED, 1 REFUTED), three accepted nonce receipts, append-only private SQLite rows and verified scoped projection hashes were reported. Full SHA256 values of each Evidence/snapshot/projection are in the linked operator terminal; no fake generated receipt is substituted. This is one **real observed software Capability pilot**, not general extraction accuracy.

## Qualification scope and remaining gate

```text
V01_IMPLEMENTATION_TASKS=10_OF_10_CLOSED
V02_IMPLEMENTATION_TASKS=6_OF_6_CLOSED
V03_T01_#139=PASS_CLOSED
V03_T02_#140=WINDOWS_R3_PASS_UBUNTU_INCREMENTAL_PENDING
IMPLEMENTATION_TASKS_CLOSED=17_OF_18
V03_CONTROLLER_#138=OPEN_NOT_COUNTED_AS_IMPLEMENTATION_TASK
PR_#143=MERGED
WINDOWS_REAL_CPYTHON_SOURCE_SHA_PIN=PASS
WINDOWS_REAL_EVIDENCE_END_TO_END=PASS_SCOPED
UBUNTU_CPTHON_SOURCE_AND_EXECUTION=NOT_YET_OBSERVED
SE10_SE11_GENERAL_PRODUCT_EFFECT=UNPROVEN
FULL_PRODUCT_RELEASE_QUALIFIED=NO
```

The **only pending v0.3 host delta** is a fresh, exact-main Ubuntu run of the same frozen CPython `inspect` → `execute` pilot, with actual local Docker client/server SHA, cached image digest, source hash/license review, P01/N01/F01/B01, nonce/EvidenceStore and projection digests recorded. Ubuntu must not reuse the Windows environmental identity or attestations. If image/daemon/client not available, report BLOCKED; do not pull or substitute a new target automatically. Use the [frozen protocol](../../validation/v0.3/CPYTHON_JSON_PILOT.md).

Do **not** rerun Windows's 200-test full suite, v0.1 LibreOffice installation, #125 22 Docker escape probes, or #133 42 runner smoke tests absent relevant baseline change.

**CLOSURE RULE:** Close #140 and #138 upon accepted Ubuntu delta or explicit owner reduction to Windows-only pilot. Neither choice makes the entire app8 product release-qualified: independent/general SE10/SE11 empirical results are still unproven.
