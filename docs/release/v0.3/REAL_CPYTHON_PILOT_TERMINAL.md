# app8 v0.3 — Real CPython JSON pilot, host-scoped verification

**Status: WINDOWS_DOCKER_DESKTOP_PASS / UBUNTU_WSL2_NATIVE_DOCKER_PASS / V03_ENGINEERING_SCOPE_COMPLETE / FULL_RELEASE_NO**

Controller: [#138](https://github.com/kaicreator-mm/app8/issues/138); real-host task [#140](https://github.com/kaicreator-mm/app8/issues/140).
Pilot executable PR [#143](https://github.com/kaicreator-mm/app8/pull/143), verified exact HEAD `7bb6435c2112a9980b48d909f7f3af1f0d314961`, tree `d8ed1a6890bb4d2cd75c346c86f50355826dd2fc`, merged to `f4c1692c73aac76ec127e45f5fc8d48d68bbd2e6`.
Operator redacted terminals: [Windows R3](https://github.com/kaicreator-mm/app8/issues/140#issuecomment-6153563183) and [Ubuntu WSL2 R4](https://github.com/kaicreator-mm/app8/issues/140#issuecomment-6154181907). Private raw logs, HMAC keys, SQLite EvidenceStores and artifacts were not uploaded.

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

## Ubuntu WSL2, native Linux Docker Engine (R4 terminal)

Ubuntu was a **WSL2 Ubuntu Unix environment with its own native Linux Docker Engine**, not an independent physical Ubuntu server. The local validator reported a clean exact-main worktree at `1d1cbe8578ef5a385a0bf16324507c1e184914a0`. [Detailed R4 terminal, Issue #140](https://github.com/kaicreator-mm/app8/issues/140#issuecomment-6154181907).

- Ubuntu targeted `tests/qualification`: **20/20 PASS**. Full 200-test pytest suite was **not repeated**; Windows R3 full pytest remains 200 PASS + 1 filesystem-privilege SKIP on the unchanged pilot source.
- Docker Linux client/daemon **29.1.3**, actual client `/usr/bin/docker` SHA256 `40cdaf7fd0f21089dd9e15b0c3a7dd7f2399027f010e366dac6304ae0615954a`. Frozen policy module SHA256 `099afa4e543c0f7479f8781b288ff60d6c5cd062405c14031cbf8731d1c1777b` was byte-identical to the Windows R3 source.
- Exact cached image `library/python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b`, no pull. Executing-image `json/__init__.py` content SHA256 `d5d41e2c29049515d295d81a6d40b4890fbec8d8482cfb401630f8ef2f77e4d5` matches Windows. CPython **3.12.15**, license review recorded.
- **P01 SUPPORTED / SCOPED_EXPORT_READY**, **N01 SUPPORTED / SCOPED_EXPORT_READY** as an independent error-boundary claim; **F01 signed REFUTED / BLOCKED**, **B01 BLOCKED_PRE_SPAWN** without creating evidence or spawning a container.
- Private append-only SQLite: 3 accepted signed Evidence rows (2 supported, 1 refuted), 3 receipt nonces, artifacts and scoped CLI/MCP/Skill/Docs/Search projection SHA256s in the Ubuntu R4 terminal. These are distinct from the Windows signatures, nonces, host identity and ledger. Zero containers left over according to the real-host report.

## v0.3 engineering terminal and release boundary

```text
IMPLEMENTATION_TASKS_TOTAL=18
V01_IMPLEMENTATION_TASKS_CLOSED=10_OF_10
V02_IMPLEMENTATION_TASKS_CLOSED=6_OF_6
V03_T01_#139=PASS_CLOSED
V03_T02_#140=WINDOWS_R3_AND_UBUNTU_WSL2_R4_REAL_PILOT_PASS
V03_CONTROLLER_#138=ENGINEERING_SCOPE_COMPLETE
IMPLEMENTATION_TASKS_CLOSED=18_OF_18
V03_DEFINED_ENGINEERING_TASKS_COMPLETE=YES
WINDOWS_QUALIFICATION_TESTS=20_OF_20_PASS
WINDOWS_FULL_PYTEST=200_PASS_1_SKIP
UBUNTU_WSL2_QUALIFICATION_TESTS=20_OF_20_PASS
UBUNTU_WSL2_FULL_PYTEST=NOT_REPEATED
WINDOWS_REAL_EVIDENCE_END_TO_END=PASS_SCOPED
UBUNTU_WSL2_REAL_EVIDENCE_END_TO_END=PASS_SCOPED
INDEPENDENT_PHYSICAL_UBUNTU_HOST_TEST=NOT_CLAIMED
SE10_SE11_GENERAL_PRODUCT_EFFECT=UNPROVEN
FULL_PRODUCT_RELEASE_QUALIFIED=NO
GITHUB_RELEASE_TAG_OR_PUBLICATION=NOT_CREATED
```

**Closure meaning:** The 18-task **defined engineering scope** through the narrowly scoped v0.3 real-software pilot is complete. The result is neither a generalized SE10/SE11 Capability-extraction benchmark nor independent Gold/human evaluation, and is **not** authorization to expose arbitrary model commands, market the product as production-ready, or publish a formal release.

The same pinned Docker policy and runner used the previously validated #125 and #133 host-security constraints; no unnecessary repeat of old isolation / runner suites occurred. Future broader product/release claims require separately scoped, real empirical qualification.

