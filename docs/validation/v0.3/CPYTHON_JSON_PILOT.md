# app8 v0.3 — Real CPython JSON Capability pilot (one bounded vertical slice)

Status: **TEST DESIGN FROZEN / REAL BEHAVIOR NOT YET OBSERVED**  
Owner scope: #138; execution task: #140; prerequisite qualification contract: #139 / PR #141.  
Evidence origin: **MODEL_AUTHORED_TEST_DESIGN / NOT_GOLD / NOT_REAL_EXECUTION**.

## Target and source identity

- Reuse only if locally cached: `library/python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b` (from #133; no pull/tag aliases). Verify local image digest and `/usr/local/bin/python` via trusted #133 Runner.
- Freeze host-specific Docker client SHA256, daemon version, policy source SHA256, environment, exact image config and approved invocation. Existing #125 OS isolation probes remain valid only if policy/daemon/image boundary is unchanged.
- Authoritative *Knowledge Source* for this pilot: actual CPython `json` package source **inside that exact image**. Obtain `json.__file__`, package/module source bytes SHA256 and Python version from deterministic read-only `python -I -c` probes. Record exact source bytes/content digest outside runtime logs; no invented revision. Repository label `python/cpython` is a source origin label, **not a claim that a particular upstream Git commit matches this image**.
- `SOURCE_SHA256`, target version, executable binary SHA, and any license/reuse disposition are initially `UNRESOLVED`. Set `REVIEWED_COMPATIBLE` only after operator verifies provenance and Python license; do not infer it from model text. Set source→target mapping to `SAME` only when source is actually measured from the exact executing image; otherwise block.

## Exactly scoped Claim

**Capability**: Decode a valid UTF-8 JSON object via Python standard library `json.loads`, report canonical sorted-key JSON on stdout without network access or durable side effects.

```text
CLAIM_ID=claim:cpython-json-normalize
CAPABILITY_ID=cap:cpython-json-normalize
SOURCE_REVISION=FROM_REAL_IMAGE_MEASUREMENT
SOURCE_SHA256=FROM_REAL_IMAGE_MEASUREMENT
TARGET=LIBRARY_PYTHON_DIGEST_ABOVE_IF_CACHED
BINDING_KIND=CLI
BINDING_ADDRESS=/usr/local/bin/python
AUTHORITY=TRUSTED_OPERATOR_FROZEN_IMAGE_AND_ARGV
EXPECTED_RESULT=HYPOTHESIS_ONLY
```

## Minimum positive / negative tests

| Case | Trusted frozen runner command arguments | Assertion hypothesis | Reality gate |
|---|---|---|---|
| P01 valid JSON | `-I -c "import json;print(json.dumps(json.loads('{\"b\":2,\"a\":1}'),sort_keys=True,separators=(',',':')))"` | exit_code 0 + stdout_contains `{"a":1,"b":2}` | Real Runner execution, raw output SHA, signed v2 Evidence |
| N01 malformed input boundary | `-I -c "import json;json.loads('{invalid')"` | exit_code nonzero + stderr_contains `JSONDecodeError` | Supported only as a **separate bounded negative-behavior claim**, not a blanket refutation of P01 |
| F01 adversarial false assertion | execute valid P01 but assert stdout_contains `never-produced-sentinel-9fa4` | FAIL / REFUTED is the expected *test-plan* outcome | Signed REFUTED must remain in EvidenceStore and prevent promotion of any claim depending on this assertion |
| B01 currentness drift | mutate expected target digest / source hash or environment pin without changing actual image | no execution / BLOCKED before signing | No stale observation can qualify |

These are model-authored fixture intentions, **not human Gold, hidden truth or empirical SE10/SE11 scores**. Prepare actual frozen plan via `freeze_execution_plan(binding_id, assertions, request)` **after** exact request/image/args have been operator reviewed; no direct LLM→Docker invocation. Do not run raw shell commands supplied by the model.

## E2E acceptance contract

1. Reuse #133 existing verified Docker policy; operator decides exact source/target and CLI binding. No pixel automation or ambient host bind/network.
2. Execute P01 (and N01 as separate claim), collect actual output/exit/hash/replay manifest with the privileged Docker Runner; auto-assertions only on real observations. Use fresh nonce and private HMAC key outside Git.
3. Import signed Evidence via `import_signed_observation` into a private append-only SQLite EvidenceStore; preserve both success and negative cases. Refuted evidence cannot be selected away.
4. Run #139 `qualify_stored_capability` on the **complete** scoped ledger using attestation gate; require strict source/target identity, reviewed license, CLI binding, and deterministic projection checks.
5. Export only source/revision/evidence/projection digest identifiers and scoped verdict to GitHub #140. Keep keys, raw logs, fixtures containing sensitive data, and private DB local.
6. Run incremental Windows + Ubuntu host validation only for changed product path; reuse existing #125 isolation tests and #133 smoke. If digest/image/source not available, mark BLOCKED without changing target or pulling unknown images.

## Terminal statuses

```text
DESIGN_CASES=4
REAL_IMAGE_IDENTITY=RECHECK_REQUIRED
REAL_SOURCE_CONTENT_SHA256=NOT_YET_OBSERVED
REAL_POSITIVE_EVIDENCE=NOT_YET_OBSERVED
REAL_NEGATIVE_EVIDENCE=NOT_YET_OBSERVED
SCOPED_PRODUCT_CAPABILITY_READY=NOT_YET_CLAIMED
SE10_SE11_GENERAL_QUALITY=UNPROVEN
FORMAL_PRODUCT_RELEASE_QUALIFIED=NO
```

**Stop after this one product slice.** Do not begin another general tool adapter or research corpus until the pilot is evaluated.

## Privileged host pilot driver (#140)

Run only from a clean exact-SHA worktree after the current candidate PR has
passed `python -m pytest tests/qualification -q` and `python -m pytest tests -q`.
Set the host-specific values from the actual reviewed Docker client and daemon,
not from model-generated suggestions.

**Phase A — inspect the already-cached digest-pinned image**:

```sh
python scripts/v03_cpython_json_pilot.py inspect \
  --docker-client "<ABSOLUTE_DOCKER_CLI>" \
  --docker-client-sha256 "<REAL_SHA256>" \
  --environment-id "<FROZEN_HOST_ENVIRONMENT_ID>" \
  --server-version "<REAL_ENGINE_VERSION>" \
  --ledger-root "<PRIVATE_ABSOLUTE_LEDGER_OUTSIDE_REPO>" \
  --out "<PRIVATE_ABSOLUTE_PATH>/cpython-json-source.json"
```

This invokes the trusted Docker policy but produces only
`SOURCE_INSPECTED_NOT_EVIDENCE` with the measured `json.__file__`, module
content SHA256 and interpreter version. It **does not** approve the source
license or create an Evidence record. The image must be locally cached; no
fallback to `:latest` or automatic `docker pull`.

**Phase B — operator-approved real assertions, signing and projection**:

```sh
python scripts/v03_cpython_json_pilot.py execute \
  --docker-client "<ABSOLUTE_DOCKER_CLI>" \
  --docker-client-sha256 "<REAL_SHA256>" \
  --environment-id "<FROZEN_HOST_ENVIRONMENT_ID>" \
  --server-version "<REAL_ENGINE_VERSION>" \
  --ledger-root "<PRIVATE_ABSOLUTE_LEDGER_OUTSIDE_REPO>" \
  --key-file "<PRIVATE_32_BYTE_OR_LONGER_KEY_FILE_OUTSIDE_REPO>" \
  --source-sha256 "<SOURCE_SHA256_FROM_INSPECT_AND_OPERATOR_REVIEW>" \
  --license-review-reference "<VERIFIABLE_PYTHON_LICENSE_REVIEW_RECORD>" \
  --out "<PRIVATE_ABSOLUTE_PATH>/cpython-json-terminal.json"
```

The driver executes exactly three separately scoped behavioral claims with
fixed argv, records signed positive and negative Evidence, and then explicitly
checks that target drift is rejected before execution. `SCOPED_EXPORT_READY`
may be reported for the reviewed P01 claim and separate N01 error behavior;
F01 must remain a signed refutation. All host keys, logs and SQLite files stay
private. In GitHub #140, submit **redacted hashes/verdicts only**, and report
BLOCKED rather than substituting an unpinned target or a synthetic test.

These commands are **not** a general production API, nor evidence of SE10/SE11
product accuracy or a formal Release qualification.
