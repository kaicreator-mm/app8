# CC04 minimal real-software demo assets

**Status: BUILD_NOT_RUN, HOST_EVIDENCE_NOT_RUN, AGENT_USE_NOT_RUN.** These inputs fill one real gap, not a new validation framework. See [original frozen Stage-A manifest](../../research/e11/stage-a/manifest.json) and [CC04 #208](https://github.com/kaicreator-mm/app8/issues/208).

## Why this exists

The archived Stage-A base images do not themselves contain the source-built FFmpeg binary or pandas wheel. The current trusted Docker runner forbids Host mounts and runs only pinned OCI repository digests. Therefore its original bare Ubuntu/Python images cannot execute these two source-built tools. We package the **already-existing pinned artifacts** into two small immutable image variants, retaining the original runner and its existing allowlist.

## Existing exact inputs to reuse

- FFmpeg source `f2bf7a2440d1e49023e4b3ed0e224a8806d388b8`, executable SHA256 `fb2e2c6895f9e8a740587b0e540dfdce888387d4dc73a5e6c50d5ce8cba56023`, base image `ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55`.
- pandas source `82c18c170b9aea7cbb96ef54b8005bed07c94220`, built wheel SHA256 `e57b0784bf6fe3abd3f292284c124ffc1c6367e35e5b97cc298f63d53431ce08`, base image `python:3.12-bookworm@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b`.
- Existing Stage-A installed pandas dependencies `numpy==2.5.4`, `python-dateutil==2.9.0.post0`, `six==1.17.0`. Their individual wheel hashes were **not frozen there**; verify/hash actual compatible wheels locally before evaluating. The Dockerfile uses offline `--no-index` installation and pins those versions.

## Local operator-only preparation

1. On the previously trusted Host, recheck each exact FFmpeg and pandas SHA against the **actual file**. Put the FFmpeg binary at ignored `examples/cc-mvp/ffmpeg/ffmpeg`; put the named pandas wheel plus all matching dependency wheels at ignored `examples/cc-mvp/pandas/wheelhouse/`. Never commit these binary artifacts, source data or credentials.
2. Use existing Docker to build the two Dockerfiles. Exact binary/wheel checks occur inside image creation; real image build, installed version, runtime dependencies and CLI behavior must be recorded **on Host**. No assumption that source-built FFmpeg has all runtime-linked libraries; validate it by actually running the final image. The pandas CLI fixed entry point is `/opt/ccmvp/pandas-job`.
3. The current runner requires a real repository `image@sha256:digest` reference and uses `--pull=never`. Local tag or image config ID is **not** a RepoDigest. Resolve/store the new image under an **already approved registry** and verify the digest exists locally. If none is available, mark `IMAGE_NOT_ADMITTED/NOT_RUN` and do not modify the existing DockerPolicy or create a registry solely to force a PASS.
4. Independently check source/target `SAME` and source license compatibility using existing evidence; record unknown as `BLOCKED`. Pin actual Docker client binary SHA, image RepoDigest, runner identity/policy, environment, execution plan, and the operator-owned real signing key/nonce DB. Never place keys or original private logs in this repo.

## Two small user-jobs and negative boundaries

| Software | Frozen CLI address | Positive task | Expected-invalid-input boundary |
|---|---|---|---|
| FFmpeg | `/opt/ccmvp/ffmpeg` | Generate a 0.25-second 440 Hz WAV: `-hide_banner -f lavfi -i sine=frequency=440:duration=0.25 -f wav pipe:1` (bounded stdout) | Unsupported filter, expected nonzero exit with observed stderr predicate |
| pandas | `/opt/ccmvp/pandas-job` | `--group-by category` on fixed bundled CSV: `{"count":4,"totals":{"seeds":10,"tools":15}}` | `--group-by wrong` must fail parsing with exit 2 |

An expected-error observation can substantiate the documented input boundary; do **not** record it as a contradictory `REFUTED` record unless the claimed behavior actually failed. The bundled CSV proves the packaging and consumption loop **only for this fixture**, not arbitrary user files. The sandbox does not support general host-file transfer.

## Acceptance (CC04, not a packaging PR)

After CC02 #211 and CC03 #212 pass their independent focused tests and merge `version/v0.4`, choose one real attributed model-origin task-level Capability per asset, preserve proposal origin, verify source/license/target authority, use the existing `RealDockerRunner.execute_attest` and `import_signed_observation` to produce genuine signed evidence, and run the full `qualify_stored_capability` ledger. The actual Agent consumes the scoped-ready Capability through the CC03 bridge and receives bounded real output bytes; a **second distinct actual task/session** must reuse the stored Capability without source reread or model-generation and have credible external Agent context (not a caller-supplied session string alone). Maintain the exact evidence snapshot tuple, real exit/result and honest `PASS/PARTIAL/BLOCKED` for each asset.

**Current test scope:** Only the Python `pandas-job` algorithm has been executed outside the target container, using different installed pandas (2.2.3): fixed CSV => totals seeds=10, tools=15, exit 0; invalid group => argparse exit 2. The source-built wheel and FFmpeg bundle, actual Docker Host, signatures, model evidence, two Agent sessions and original SE10/SE11 Gold/hidden are **NOT_RUN**. This source-example PR is not a Release gate pass.

## Minimal Host Evidence join (operator only)

`host_evidence.py` now connects each reviewed selected Capability and 1–4 fixed cases to **existing** `RealDockerRunner.execute_attest`, `import_signed_observation`, `EvidenceStore` and `qualify_stored_capability`. It does **not** synthesize a model proposal, silently set `REVIEWED_COMPATIBLE` or `SAME`, authenticate a real Agent, or qualify a product release.

Create one private JSON job per asset with exactly:

```json
{
  "capability": "<full selected app8-capability-v1 JSON object, NOT a string>",
  "docker": {
    "client_path": "<absolute approved Docker CLI binary>",
    "client_sha256": "<actual independently pinned 64-hex SHA256>",
    "runner_id": "<operator-approved runner ID>",
    "environment_id": "<identical to capability.target.environment_id>"
  },
  "cases": [
    {
      "claim_id": "claim:bounded-user-job",
      "args": ["<reviewed exact arguments>"],
      "assertions": ["exit_code==0"],
      "fixture": {
        "content_sha256": "<64-hex SHA256 of the reviewed fixture>",
        "input_description": "<bounded real input description>",
        "reset_procedure": "ephemeral pinned image; no network or Host mount"
      }
    }
  ]
}
```

Here `capability` is a **JSON object**, not the illustrative placeholder string. Input Capability must already have independent license `REVIEWED_COMPATIBLE`, target `SAME`, exactly one reviewed read-only CLI binding and **empty** `evidence_refs`; these are required prerequisites, not statements made by this program. Use actual binary/wheel OCI RepoDigest and exact runner environment; do not substitute bare parent images.

```sh
export APP8_RUNNER_HMAC_KEY_FILE=/private/operator-owned-runner-key
python examples/cc-mvp/host_evidence.py --job /private/reviewed-ffmpeg.json --private-dir /private/cc04-ffmpeg-new
python examples/cc-mvp/host_evidence.py --job /private/reviewed-pandas.json --private-dir /private/cc04-pandas-new
```

All cases are checked for Docker policy conformance, exact argv and supported frozen assertion syntax **before the first Host execution**. `host-report.json` records the CC04 join identity (`capability_id`, revision, `semantic_sha256`, source SHA, target SHA, OCI identity, environment ID, binding ID, Evidence snapshot SHA and per-case frozen plan SHA). Compare those exact values across real Agent first/second use; a matching session label alone is insufficient.

Run only on an explicitly authorized real Host and an **empty output directory**, one per asset. Nonzero exit means blocked/unready, never a silent PASS. Evidence artifacts, signed sidecars and selected Capability stay outside Git in the private directory. The emitted `host-report.json` deliberately says `agent_first_use=NOT_RUN`, `agent_second_use=NOT_RUN`, `mvp_release=NOT_QUALIFIED`. Afterwards an independently authenticated actual Agent must consume that persisted selected Capability via CC03's narrowly scoped `run_agent_cli`, then a **different** actual Agent task/session must reuse it without re-reading source or rerunning the proposal model. Store the externally verified Agent identities/results with the final CC04 report. A caller-supplied `session_id` string and two manual terminal invocations do not meet that gate.

**This script and its Host images have not yet been run on the approved Host; execution, signatures and real Agent proof remain NOT_RUN.** Run focused Python tests on the exact joined source before real Host use.
