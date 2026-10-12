# SE11 / SE15 — Execution Target Selection Candidate

Status: CANDIDATE_FOR_FRESH_REVIEW
Depends on: PR #64 identity-model amendment PASS + merge
Owning issues: #43, #50, #55
Historical Stage-A evidence merge: 0279968580d50e51843b09aa2b6e266b9967ff93

## 1. Purpose

Freeze a cost-efficient real-execution target **selection** after separating Knowledge Source identity from Execution Target identity.

This file does not authorize hidden-truth construction or evaluated execution. Runtime installation/smoke identity for LibreOffice is still required before a final Execution Target manifest is committed.

## 2. Selection rule

Preferred order:

1. official publisher release binary/installer/package;
2. official publisher package-registry/container artifact;
3. publisher-recommended build with durable provenance;
4. source build only when already available, when no suitable official artifact exists, or when a Capability is source-only/unreleased.

Existing exact-source builds from SE11 Stage A remain valid and are reused; the amendment removes a **requirement** to source-build ordinary released software, not the validity of already-produced exact-source artifacts.

## 3. Candidate targets

### FFmpeg

- Knowledge Source: `FFmpeg/FFmpeg@f2bf7a2440d1e49023e4b3ed0e224a8806d388b8`
- Execution Target class: `EXACT_SOURCE_BUILD`
- Reuse evidence: Stage-A merge `0279968580d50e51843b09aa2b6e266b9967ff93`
- `ffmpeg` SHA-256: `fb2e2c6895f9e8a740587b0e540dfdce888387d4dc73a5e6c50d5ce8cba56023`
- `ffprobe` SHA-256: `bedd1eade64dffd2d72e9f8aa23d3487841b3501e9a74dad209c4f7b14bc0a2f`
- Relation: `SAME`
- Runtime readiness: `HISTORICAL_READY_REUSE_REQUIRES_CURRENT_BINARY_HASH_AND_CONTAINER`

Reuse is valid **only within the original Ubuntu 24.04 x86_64 Docker/WSL2-compatible execution lane** (container image digest `sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55`). Before evaluated execution, prove the exact artifact bytes remain available on the real host and freeze the compatible container/runtime. The ELF binary must **not** be treated as directly runnable on the Windows host. If the original artifact was deleted, artifact re-materialization and smoke must be independently evidenced; previous hash alone does not prove current availability.

### pandas

- Knowledge Source: `pandas-dev/pandas@82c18c170b9aea7cbb96ef54b8005bed07c94220`
- Execution Target class: `EXACT_SOURCE_BUILD`
- Reuse evidence: Stage-A merge `0279968580d50e51843b09aa2b6e266b9967ff93`
- Wheel SHA-256: `e57b0784bf6fe3abd3f292284c124ffc1c6367e35e5b97cc298f63d53431ce08`
- Wheel identity: `pandas-0+untagged.1.g82c18c1-cp312-cp312-linux_x86_64.whl`
- Relation: `SAME`
- Runtime readiness: `HISTORICAL_READY_REUSE_REQUIRES_CURRENT_WHEEL_HASH_CONTAINER_AND_PINNED_DEPS`

The frozen wheel is `cp312-cp312-linux_x86_64` and runs **only in a compatible CPython 3.12 Linux x86_64 environment**, not the Windows Python installation. Preserve the original `python:3.12-bookworm` image digest `sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b`. Before evaluated execution, re-verify the exact wheel bytes and freeze/pin runtime dependencies (Stage-A smoke had unpinned numpy/python-dateutil/six). If wheel/artifact or compatible container no longer exists, do not claim READY from historical evidence alone.

### MinIO

- Knowledge Source: `minio/minio@7aac2a2c5b7c882e68c1ce017d8256be2feea27f`
- Execution Target class: `EXACT_SOURCE_BUILD`
- Reuse evidence: Stage-A merge `0279968580d50e51843b09aa2b6e266b9967ff93`
- Binary SHA-256: `94d0b2677e6ed5a719fe1fc5fccbd60669beecb9901a3bb6a8bc71507bd55981`
- Embedded VCS revision: `7aac2a2c5b7c882e68c1ce017d8256be2feea27f`
- Relation: `SAME`
- Runtime readiness: `HISTORICAL_READY_REUSE_REQUIRES_CURRENT_EXE_HASH`

This is a **Windows x64 native** `minio.exe` produced by Go 1.27.1 for windows/amd64. Reuse only if the original binary SHA-256 is verified on the actual Windows execution host; do not try to execute it as Linux ELF in the FFmpeg/pandas containers. If no longer preserved, re-materialization requires fresh provenance and smoke evidence.

### LibreOffice

**Knowledge Source**

- Repository: `LibreOffice/core`
- SE10 snapshot: `016fd5d049256dc849111f60870f15201fcd1526`

**Execution Target candidate**

- Publisher: The Document Foundation
- Product release: LibreOffice `26.8.1`
- Package version: `26.8.1.1`
- Architecture: Windows x86-64
- Official installer:
  `https://download.documentfoundation.org/libreoffice/stable/26.8.1/win/x86_64/LibreOffice_26.8.1_Win_x86-64.msi`
- Installer SHA-256:
  `C6298B10CFA1748BCBEDAD94C62CE771E240E5021BFD6D7A967CD571B04B5312`
- Official download page reports 26.8.1 as the current stable release for Windows x86-64.
- winget provenance:
  - repository: `microsoft/winget-pkgs`
  - manifest path: `manifests/t/TheDocumentFoundation/LibreOffice/26.8.1.1/TheDocumentFoundation.LibreOffice.installer.yaml`
  - manifest blob: `7fab0752ca301762c433c28a7901be3a3bb9cdca`
  - PackageIdentifier: `TheDocumentFoundation.LibreOffice`
  - ReleaseDate: `2026-10-08`
  - ProductCode x64: `{87B289F9-6172-4C3D-A091-EE36A40E1287}`

**Publisher source-release mapping**

- annotated tag: `libreoffice-26.8.1.1`
- tag object: `f3b61cf45f5198919f352f5163cd1dc2c000ba28`
- release source commit: `bf6ef2662401c7d6dce671ab4deb26ee0af3a7c1`
- Execution Target class: `OFFICIAL_RELEASE_MAPPED`

**Knowledge Source -> release-source relation**

GitHub compare between release source commit `bf6ef266...` and SE10 Knowledge Source `016fd5d...`:

- relation: `DIVERGED`
- merge base: `e6d16d8cd2b4e8b4535e1c5827e3c676fb83ad02`
- compared direction release->knowledge: ahead_by=3317, behind_by=352

Therefore the SE10 Knowledge Source must **not** be treated as exact runtime truth for LibreOffice 26.8.1.

Before hidden-truth expectations or SE15 binding coverage are scored:

- selected LibreOffice Capability semantics must be shown applicable to release 26.8.1 using publisher release-specific source/tag/help/release metadata or independent deterministic target evidence;
- source-only/master-only behavior is ineligible for ordinary 26.8.1 expected-success claims;
- an applicability failure is a version/currentness boundary, not a reason to swap the target after outcomes.

**Runtime readiness**

`PENDING_OFFICIAL_INSTALL_AND_NON_EVALUATIVE_SMOKE`

Required local completion is limited to:

1. use **only the exact official MSI above** for the supported install path; winget is provenance evidence only and is not an alternate install path for the frozen run;
2. verify downloaded package SHA-256;
3. record installed product version/ProductCode and principal executable identities/checksums;
4. verify the required x64 Visual C++ v14 runtime dependency is already present, and record its exact installed DisplayName/DisplayVersion/ProductCode; registry DisplayName may use either the historical `Microsoft Visual C++ 2015-2022 Redistributable (x64)` family or the current `Microsoft Visual C++ v14 Redistributable (x64)` family, with an optional exact `" - <DisplayVersion>"` suffix; if no exact accepted identity is present, BLOCK instead of silently installing/substituting it;
5. record Windows/runtime identity;
6. perform only non-evaluative `--version` / headless startup or equivalent readiness smoke;
7. preserve raw logs.

No LibreOffice source build is required for this ordinary release target. The winget manifest declares dependency package identifier `Microsoft.VCRedist.2015+.x64`; that package identifier is **not** treated as the registry DisplayName. The accepted registry identity is a bounded Microsoft Visual C++ v14 x64 name family: historical `Microsoft Visual C++ 2015-2022 Redistributable (x64)` or current `Microsoft Visual C++ v14 Redistributable (x64)`, each optionally suffixed by the exact installed DisplayVersion. Publisher/version/GUID and exactly-one guards still apply. #69 must freeze the **observed exact installed VC runtime identity/version/ProductCode** as part of the final runtime manifest. Until that happens, `LIBREOFFICE_RUNTIME_READY=NO`.

## 4. Cross-host compatibility gate

These are not four interchangeable executables on one host. The studied host is Windows 11 plus a WSL2 Docker runtime. Asset-specific lanes:

| Asset | Runtime lane | Condition for reuse |
|---|---|---|
| FFmpeg | Linux x86_64 Ubuntu 24.04 Docker | SHA-256 artifact still present + same compatible image/runtime |
| pandas | Linux x86_64 CPython 3.12 bookworm Docker | frozen wheel present + image digest + pinned dependencies |
| MinIO | Windows x64 native | SHA-256 EXE present and runnable |
| LibreOffice | Windows x64 native | official MSI SHA-256, ProductCode + installed EXE identity (pending) |
| Notepad (SE15 only) | Windows 11 frozen Store app | frozen package/host/UIA identities, no UIA inspection before sample freeze |

**Historical smoke = evidence of historical readiness, not proof the runtime/artifact is still present today.** Never carry a Linux wheel/ELF over to the native Windows lane, and never silently move the pinned Windows Notepad/UIA target. If reusing the same host does not work, record a new host/identity freeze before evaluation, never patch the denominator or swap a target after outcomes.

## 5. Freeze consequences

After PR #64 and this selection are independently reviewed:

- FFmpeg/pandas/MinIO may reuse existing Stage-A artifacts;
- LibreOffice gets a small official-package install/smoke task instead of a multi-hour source build;
- the final Execution Target manifest must add the locally verified installer and installed-runtime identities;
- hidden truth remains HOLD until that final manifest is frozen and independently reviewed.

```text
EXECUTION_TARGET_SELECTION=FROZEN_CANDIDATE
FFMPEG=HISTORICAL_READY_REUSE_IF_ARTIFACT_PRESENT_LINUX
PANDAS=HISTORICAL_READY_REUSE_IF_WHEEL_AND_DEPS_PINNED_LINUX
MINIO=HISTORICAL_READY_REUSE_IF_ARTIFACT_PRESENT_WINDOWS
LIBREOFFICE=OFFICIAL_26_8_1_PENDING_LOCAL_SMOKE
LIBREOFFICE_SOURCE_BUILD_REQUIRED=NO
LIBREOFFICE_SOURCE_RELATION=DIVERGED
SE11_HIDDEN_TRUTH=HOLD
SE11_STAGE_C=HOLD
SE15_BINDING_EXECUTION=HOLD
PRODUCT_FREEZE=NO
L2_READY=NO
```

## 6. What Was NOT Proven

This target-selection artifact does not prove LibreOffice runtime readiness, target applicability for any individual Capability, SE11 falsification quality, SE15 binding coverage, Product Freeze, L2 readiness, or release qualification.
