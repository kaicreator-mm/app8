# SE11 Stage A — Local Real-Host Readiness / Frozen Executable Identity

Issue: #43 (dispatch: "Local Real-Host Stage A dispatch")
Protocol: `docs/product/v0.1-successor/l1/SE11_PROTOCOL.md` (blob `83abefb13e6a91e6b67a1c94937ca1bcce567aad`)
Branch: `task/app8-i43-se11a` (based on `origin/main` = `b989075`)

This package contains ONLY Stage A infrastructure identity and non-evaluative smoke
readiness for the four frozen SE11 source subjects, produced on one real local host.
It creates no hidden truth, runs no decisive fixtures, and produces zero SE11
capability evidence.

## Hard-constraint state (verbatim from the dispatch)

~~~text
HIDDEN_TRUTH=NOT_CREATED_OR_NOT_VISIBLE_TO_PLANNER
DECISIVE_FIXTURES=NOT_RUN
LLM_B_EVALUATED_PLAN=NOT_RUN
SE11_RESULT=NOT_RUN
NO_SOURCE_REVISION_SUBSTITUTION (enforced: HEAD==pinned verified locally per asset)
NO_FAKE_PASS (smoke tests are infrastructure checks, not capability evidence)
PRODUCT_FREEZE=NO
L2_READY=NO
~~~

## Real host identity

~~~text
OS        Microsoft Windows 11 专业版, 10.0.26300, x64 (see host/host-identity.txt)
CPU       AMD Ryzen 7 7840HS, 8C/16T
RAM       55.2 GB
Shell     Git Bash (MINGW64) — orchestration only
Container Docker 29.7.2 (see host/docker-identity.txt, host/docker-image-digests.txt)
Linux     ubuntu:24.04 (digest sha256:534baea6…0eb55) and python:3.12-bookworm containers
~~~

## Frozen source subjects — exact identity (verified locally)

| asset | pinned commit | local HEAD | tree (shared with SE10 where naturally identical) |
|---|---|---|---|
| FFmpeg/FFmpeg | `f2bf7a2440d1e49023e4b3ed0e224a8806d388b8` | equal ✓ | `e12649cf34daed3184ad91f6a94c3c6499ad748d` |
| pandas-dev/pandas | `82c18c170b9aea7cbb96ef54b8005bed07c94220` | equal ✓ | `c3531d0e0dc0b9c1f75b8a5912b2f43eb203e493` |
| minio/minio | `7aac2a2c5b7c882e68c1ce017d8256be2feea27f` | equal ✓ | `376b09b793c57170a905208e64590164d8ab7a3b` |
| LibreOffice/core | `016fd5d049256dc849111f60870f15201fcd1526` | equal ✓ | `a4626696016cd1cb87226ecb8cd5007976910e6e` |

Local clones are shallow (`--depth 1` at the exact pinned SHA) and byte-faithful:
`core.autocrlf=false`, `core.eol=lf`; `git status --porcelain` is empty against HEAD
for every asset (script `scripts/fetch-source.sh` asserts HEAD==pinned and
worktree-vs-blob faithfulness; any smudge would surface as a dirty entry).
Tree hashes above are intrinsic Git object identities of the pinned commits —
naturally identical to the trees SE10 verifies its source pack against;
no SE10-specific pack files were consulted or copied.
LibreOffice `helpcontent2` submodule identity is not resolved in Stage A
(`.gitmodules` still points at it; submodule fetch/build was out of budget — see below).

## Per-asset result summary

| asset | status | build host | artifact | smoke |
|---|---|---|---|---|
| FFmpeg @ f2bf7a2 | **READY** | ubuntu:24.04 container (gcc 13.3.0) | `ffmpeg` sha256 `fb2e2c6895f9e8a740587b0e540dfdce888387d4dc73a5e6c50d5ce8cba56023`; `ffprobe` sha256 `bedd1eade64dffd2d72e9f8aa23d3487841b3501e9a74dad209c4f7b14bc0a2f` | `-version` exit 0, `-h` exit 0 |
| pandas @ 82c18c1 | **READY** | python:3.12-bookworm container (gcc 12.2.0, CPython 3.12.15) | wheel `pandas-0+untagged.1.g82c18c1-cp312-cp312-linux_x86_64.whl` sha256 `e57b0784bf6fe3abd3f292284c124ffc1c6367e35e5b97cc298f63d53431ce08` | import from site-packages exit 0, identity print only |
| MinIO @ 7aac2a2 | **READY** | Windows 11 native (go 1.27.1 windows/amd64) | `minio.exe` sha256 `94d0b2677e6ed5a719fe1fc5fccbd60669beecb9901a3bb6a8bc71507bd55981` | `--version` exit 0; server startup + `GET /minio/health/live` → 200 |
| LibreOffice/core @ 016fd5d | **BLOCKED_ENVIRONMENT** (bounded attempt, no substitution) | ubuntu:24.04 container attempt; Windows native impossible (no MSVC) | none built | none — see below |

Details for every required dispatch output (1–9) are in `manifest.json`;
raw logs with hashes are under `logs/<asset>/`.

## LibreOffice — BLOCKED_ENVIRONMENT finding (explicit, per dispatch)

~~~text
LIBREOFFICE_STATUS=BLOCKED_ENVIRONMENT
SUBSTITUTED_SOURCE=NONE (no distro binary, no newer upstream, no feature-reduced configure)
~~~

Facts recorded (raw logs under `logs/libreoffice/`):

1. Windows-native path is impossible on this host: no MSVC installed
   (`logs/libreoffice/host-native-toolchain.txt`: `where cl` not found);
   LO Windows builds require Visual Studio plus Cygwin/Java dependency chain.
2. Bounded Linux-container attempts with documented dependency waves and
   default-feature `./autogen.sh` (no feature-reduced configure):
   - round 0: exact terminal error `configure: error: Could not find CUPS.
     Install libcups2-dev or cups-devel.` (`autogen.sh` line 338) —
     `logs/libreoffice/round0-*`;
   - round 1: invalidated — the sole failed apt archive was
     `openjdk-21-jdk-headless` (connection failed), aborting the whole apt
     transaction, so the CUPS fix was never installed; superseded
     (`logs/libreoffice/round1-driver.log`);
   - round 2 (final): first wave + `libcups2-dev`/GTK3/X11, apt retry, no JDK
     (LO treats missing JDK as feature degradation, not fatal). Configure
     **passed the CUPS check** (`checking for cupsPrintFiles in -lcups... yes`)
     and then failed at the next dependency:
     `The missing Perl modules are: Archive::Zip` —
     `logs/libreoffice/autogen.log`, `attempt-final.txt`, `attempt.log`;
   - round 3 (TERMINAL by pre-declared stop rule): added exactly the reported
     gap (`libarchive-zip-perl`); configure progressed through STL/ccache
     checks and failed at the next mandatory dependency:
     `configure: error: Java not found. You need at least JDK 8`. Three
     successive remediations, each exposing the next requirement — the
     default-feature build path is a long mandatory chain.
3. Budget reality (not silently weakened): a full LO core build needs tens of GB
   of build space beyond the 1.8 GB source and multi-hour `make` on this 16-thread
   host; this exceeds the Stage-A session budget, so even a configure success was
   treated as NOT a runnable binding.

If SE11 later requires a LibreOffice binding, it needs a dedicated build session
or host; Stage B must treat all LibreOffice claims as BLOCKED unless such a
binding is produced first.

## Smoke invocations are NOT SE11 capability evidence

Every smoke above is a non-evaluative infrastructure check (invocation, identity,
startup readiness). None exercised any capability claim, none produced a verdict,
and none will be reused as decisive fixtures in Stage B/C.

## Incident log (audit trail)

- `logs-attempt1-*` material in the worktree evidence dir (not committed):
  the first build wave ran against a CRLF-smudged working tree
  (`core.autocrlf=true` inherited), surfacing as
  `./configure: cannot execute: required file not found` for FFmpeg.
  All four sources were re-materialized byte-faithfully and every build/smoke
  evidence in this package comes from the re-materialized (byte-faithful) trees.
  minio/pandas artifact hashes differ between the two waves because Go/CPython
  embed source bytes; the committed hashes are the byte-faithful wave.
- Round-1 CLI kill + zombie container: the round-1 `docker run` CLI was
  SIGKILLed (exit 137) when its session ended, but the container survived and
  kept running (`cp -a /work/src /build` for 20+ min) while still bound to the
  mounted evidence log dir; it was killed (`docker kill`) before it could
  overwrite round-2 log files with stale round-1 content.
- Round-2 attached run killed by host ~6.5 min in: the container was destroyed
  mid-apt-download and the CLI returned 137
  (`logs/libreoffice/apt-r2-attached-killed.log` truncated at `Get:192`,
  `driver-round2-attached.log`). This host has a prior history of containers
  dying 137. Rounds 2b/3 therefore re-invoked the identical payload detached
  (`docker run -d` + `docker wait`), decoupling container survival from any
  Windows-side CLI lifetime; both completed normally.
- Evidence blob CRLF normalization (caught in verification): commit `82e26e3`
  was created with host `core.autocrlf=true`, so two PowerShell-generated
  evidence files (`host/host-identity.txt`,
  `logs/libreoffice/host-native-toolchain.txt`) were stored CRLF-normalized —
  their blobs no longer matched `SHA256SUMS.txt`. Fixed by committing
  byte-faithful blobs under `research/e11/stage-a/.gitattributes` (`* -text`,
  no EOL conversion for the whole evidence tree) and re-verifying all
  SHA256SUMS entries. The same `autocrlf=true` had earlier smudged the source
  trees (first incident above) — evidence directories must never rely on
  host EOL config.
- `logs/libreoffice/attempt-audit.log` in `82e26e3` was copied before the
  round-3 wrapper appended its final three lines; completed in this commit
  (round-3 container id, `LIBREOFFICE_ROUND3_EXIT=1`, terminal verdict).

## Reproducibility

From a clean host with Docker + Go + Git:

~~~bash
bash scripts/fetch-source.sh minio minio/minio 7aac2a2c5b7c882e68c1ce017d8256be2feea27f
bash scripts/fetch-source.sh pandas pandas-dev/pandas 82c18c170b9aea7cbb96ef54b8005bed07c94220
bash scripts/fetch-source.sh ffmpeg FFmpeg/FFmpeg f2bf7a2440d1e49023e4b3ed0e224a8806d388b8
bash scripts/fetch-source.sh libreoffice LibreOffice/core 016fd5d049256dc849111f60870f15201fcd1526
bash scripts/build-smoke-minio.sh
bash scripts/build-smoke-pandas-docker.sh
bash scripts/build-smoke-ffmpeg-docker.sh
# LibreOffice bounded dependency-chain rounds (round 3 is terminal):
bash scripts/attempt-libreoffice-docker.sh      # round 0: CUPS missing
bash scripts/attempt-libreoffice-round1.sh      # round 1: invalidated (apt abort)
bash scripts/attempt-libreoffice-round2.sh      # round 2 attached (was host-killed here)
bash scripts/attempt-libreoffice-round2b.sh     # round 2b detached: Archive::Zip missing
bash scripts/attempt-libreoffice-round3.sh      # round 3 detached terminal: JDK 8+ required
~~~

Source packs live outside this repo (re-creatable from the pinned SHAs above);
Docker image digests are pinned in `host/docker-image-digests.txt`.
