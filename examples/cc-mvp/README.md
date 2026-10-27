# CC04 minimal real-software demo assets

**Current truth (2026-10-28):** These checked-in Dockerfiles and the `pandas-job` CLI are the **original operator-authored packaging demos**, *not* the later model-origin executable capabilities. The approved Host independently built/reran the pinned FFmpeg/pandas demos and produced genuine signed Evidence; [#208 model-origin Host receipt](https://github.com/kaicreator-mm/app8/issues/208#issuecomment-6454284485) separately reports **two new model-origin task implementations**, real signed positive/negative observations and independent GLM/Kimi reuse for each asset. Their **new** CLI entrypoints and build recipes remain outside the repository pending byte-exact safe source import. See [scoped RQ evidence and reproducibility candidate](../../docs/release/v0.4/CC_MVP_SCOPED_RQ_CANDIDATE.md). Neither these examples nor the Host report constitute Release PASS.

## Why this exists

The archived Stage-A base images do not themselves contain the source-built FFmpeg binary or pandas wheel. The trusted Docker runner forbids Host mounts and runs only content-addressed targets: either an already-approved registry RepoDigest **or**, for the approved local-only Host, the full Docker image ID `sha256:<64 lowercase hex>` (new scoped mode, pending exact-HEAD Host verification). These are different identifiers and must never be interchanged. Therefore its original bare Ubuntu/Python images cannot execute these two source-built tools. We package the **already-existing pinned artifacts** into two small immutable image variants, retaining the original runner and its existing allowlist.

## Existing exact inputs to reuse

- FFmpeg source `f2bf7a2440d1e49023e4b3ed0e224a8806d388b8`, executable SHA256 `fb2e2c6895f9e8a740587b0e540dfdce888387d4dc73a5e6c50d5ce8cba56023`, base image `ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55`.
- pandas source `82c18c170b9aea7cbb96ef54b8005bed07c94220`, built wheel SHA256 `e57b0784bf6fe3abd3f292284c124ffc1c6367e35e5b97cc298f63d53431ce08`, base image `python:3.12-bookworm@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b`.
- Existing Stage-A installed pandas dependencies `numpy==2.5.4`, `python-dateutil==2.9.0.post0`, `six==1.17.0`. Their individual wheel hashes were **not frozen in Stage-A**, but were later recorded with exact filenames, versions and SHA256 values in [`research/mla/v04-mla-four-target-reentry-candidate.json`](../../research/mla/v04-mla-four-target-reentry-candidate.json). This is a **DATA_ONLY_CANDIDATE_NOT_APPROVED** record: file bytes were cross-checked, but runtime wheel installation/import ABI and case-specific applicability remain **NOT_RUN/UNAPPROVED**. This Dockerfile now checks the exact four wheel SHA256s before offline `--no-index` installation, reusing those known bytes rather than collecting them again.

## Local operator-only preparation

1. On the previously trusted Host, recheck each exact FFmpeg and pandas SHA against the **actual file**. Put the FFmpeg binary at ignored `examples/cc-mvp/ffmpeg/ffmpeg`; put the named pandas wheel plus exactly the 3 dependency wheels documented in the existing [MLA reentry candidate](../../research/mla/v04-mla-four-target-reentry-candidate.json) at ignored `examples/cc-mvp/pandas/wheelhouse/`. The Dockerfile verifies those **historically known** exact wheel bytes before install. Do **not** re-download/recalculate the candidate hashes as a prerequisite if the archived wheels are still available; if local bytes differ, fail and investigate, never replace expected SHA. Never commit artifacts, source data or credentials.
2. Use existing Docker to build the two Dockerfiles. Exact binary/wheel checks occur inside image creation; real image build, installed version, runtime dependencies and CLI behavior must be recorded **on Host**. No assumption that source-built FFmpeg has all runtime-linked libraries; validate it by actually running the final image. The pandas CLI fixed entry point is `/opt/ccmvp/pandas-job`.
3. Use the **exact image reference** approved for this run: a real `repository/path@sha256:<RepoDigest>` if an already-approved registry exists, or (after independently testing the new local mode on the actual approved Docker Host) the actual local content-addressed `sha256:<full-image-ID>` returned by `docker image inspect --format '{{.Id}}' <local-tag>`. **Do not** fabricate `repository/path@sha256:<image-config-ID>`: a config ID is not a registry RepoDigest. The local mode retains `--pull=never`, disabled network, exact command allowlist, unchanged signing and environment pins; it does not imply an exportable/portable image or software-release qualification. Recreate new signed Evidence if changing the target identity; **never** relabel an existing signed ledger. If neither mode passes real Host verification, record `IMAGE_NOT_ADMITTED` without adding infrastructure.
4. Independently check source/target `SAME` and source license compatibility using existing evidence; record unknown as `BLOCKED`. Pin actual Docker client binary SHA, image RepoDigest, runner identity/policy, environment, execution plan, and the operator-owned real signing key/nonce DB. Never place keys or original private logs in this repo.

## Two small user-jobs and negative boundaries

| Software | Frozen CLI address | Positive task | Expected-invalid-input boundary |
|---|---|---|---|
| FFmpeg | `/opt/ccmvp/ffmpeg` | Generate a 0.25-second 440 Hz WAV: `-hide_banner -f lavfi -i sine=frequency=440:duration=0.25 -f wav pipe:1` (bounded stdout) | Unsupported filter, expected nonzero exit with observed stderr predicate |
| pandas | `/opt/ccmvp/pandas-job` | `--group-by category` on fixed bundled CSV: `{"count":4,"totals":{"seeds":10,"tools":15}}` | `--group-by wrong` must fail parsing with exit 2 |

An expected-error observation can substantiate the documented input boundary; do **not** record it as a contradictory `REFUTED` record unless the claimed behavior actually failed. The bundled CSV proves the packaging and consumption loop **only for this fixture**, not arbitrary user files. The sandbox does not support general host-file transfer.

## Acceptance (CC04, not a packaging PR)

After CC02 #211 and CC03 #212 pass their independent focused tests and merge `version/v0.4`, choose one real attributed model-origin task-level Capability per asset, preserve proposal origin, verify source/license/target authority, use the existing `RealDockerRunner.execute_attest` and `import_signed_observation` to produce genuine signed evidence, and run the full `qualify_stored_capability` ledger. The actual Agent consumes the scoped-ready Capability through the CC03 bridge and receives bounded real output bytes; a **second distinct actual task/session** must reuse the stored Capability without source reread or model-generation and have credible external Agent context (not a caller-supplied session string alone). Maintain the exact evidence snapshot tuple, real exit/result and honest `PASS/PARTIAL/BLOCKED` for each asset.

**Evidence scope now:** The original `pandas-job` non-target 2.2.3 smoke was followed by actual pinned Docker Host builds, executions and HMAC-ledger tests at PR #216/#218 (see linked source receipts). Those successes **do not transform the original operator-authored demos into model-generated tasks**. Separately, issue #208 reports V04-FFMPEG-004 and V04-PANDAS-002 model-origin Host journeys with new CLI entrypoints and exact pinned images. Actual new executable sources, original sealed-model-to-CC01 typed candidate provenance and independent final RQ must be reviewed as outlined in the [scoped RQ candidate](../../docs/release/v0.4/CC_MVP_SCOPED_RQ_CANDIDATE.md). Original SE10 Gold48 / SE11 Hidden80 remain NOT_RUN; main Release remains HOLD.

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

## Actual Agent-facing consumer from persisted Evidence (CC04 final gate)

`agent_consume.py` provides the **minimal executable handoff** from the private, already-qualified Host ledger to the existing `run_agent_cli` API. It does not create Evidence or a new sandbox/signature/client framework. It rechecks the original reviewed operator-job Capability (ignoring only populated `evidence_refs`), frozen case index, operator Docker client SHA, exact target/binding/environment, every signed receipt and complete-ledger readiness **on each call**. The selected args must match an authenticated previously-supported plan.

Use this only after `host_evidence.py` has produced `capability.json`, `signed-attestations.json`, `accepted-nonces.sqlite3` and `store/` for the asset, with `SCOPED_EXPORT_READY` obtained from actual approved Host execution.

```sh
# Called by one independently authenticated real Agent task A,
# NOT directly interpreted as proof of who issued the command:
python examples/cc-mvp/agent_consume.py \
  --job /private/reviewed-ffmpeg.json \
  --private-dir /private/cc04-ffmpeg-new \
  --case-index 1 --session-id REAL_AGENT_TASK_A

# A different independently authenticated real Agent task B uses
# the SAME stored Capability, job and private Evidence directory:
python examples/cc-mvp/agent_consume.py \
  --job /private/reviewed-ffmpeg.json \
  --private-dir /private/cc04-ffmpeg-new \
  --case-index 1 --session-id REAL_AGENT_TASK_B
```

Repeat for pandas, replacing the two private paths with the pandas job and ledger. Only use a case whose assertions were genuinely `SUPPORTED`; an expected invalid-input boundary may return nonzero and is not a successful Agent task by itself. The JSON result includes base64-encoded bounded stdout/stderr, real exit/status, invocation SHA, complete Evidence snapshot and the full CC04 join tuple: Capability ID/revision, semantic SHA, source SHA, target SHA/OCI identity, environment ID and binding ID. Compare these to the independently verified private `host-report.json` for both actual Agent calls. The event ledger stores hashes, not raw stdout/stderr.

**Authentication limitation:** A `--session-id` string is **not** evidence that a separate real Agent was involved. The host-side Agent orchestrator must authenticate and retain two independent caller/task records, exact invocation and output hashes, snapshot and binding tuple; absent this, `session_authentication=EXTERNALLY_REQUIRED_NOT_PROVEN_BY_THIS_CLI` and `release_qualified=false` remain mandatory. Source-reading/LLM proposal regeneration must not occur between uses. Running this script twice manually proves only an operator smoke, never the two-Agent CC04 gate.

Only the approved real Host should run this script with access to its private signing key and nonce database. Do not expose these paths or key to an untrusted Agent; the Host invokes the tool on behalf of authenticated Agents.

**Execution status:** this consumer itself, real Docker image builds, actual signed Host executions and authenticated two-Agent reuse remain **NOT_RUN** until confirmed by independent Host receipts.
