# V04-MLA-1 pre-output blind-freeze materialization — exact-byte record

Issue [#166](https://github.com/kaicreator-mm/app8/issues/166) Step H3.
Product decision [V04-PO-MLA-001](../../product/v0.4/MULTI_LLM_OWNER_DECISION.md).

`scripts/v04_mla_blind_freeze_materializer.py` materializes — before any
model response exists — the exact blind role input metadata the trusted
capture verifier demands: the four-field envelope per role
(`source_pack_git_blob`, `source_context_sha256`, `task_instruction_sha256`,
role-specific `visibility_scope`), the frozen P/R/X role configuration
(model family/provider/version, prompt/sampling SHA256, derived exact
envelope-byte `input_sha256`), and the binding to the exact privileged
outbound request bytes. It persists one canonical JSON record atomically
(refusing overwrite), returns its SHA256 anchor together with the exact
envelope bytes, and binds every role's outbound request with the production
`frozen_invocation_digest` (profile-validated envelope digest + raw body
SHA256) — the same digest the ordered host ledger reserves before the
response event.

## The v4 gap (counts only, no content)

The v4 pilot carried `frozen_before_first_response=true` as a caller
declaration inside its capture freeze, but produced **no materialized
pre-output freeze record**: no persisted, hashed artifact tying the blind
role input metadata to the exact privileged request bytes existed before the
first response. That gap cannot be repaired after the fact — creating such a
record from sealed v4 results is prohibited and would be a post-hoc
reconstruction, not a freeze.

## Exact-byte binding

- Each role's persisted envelope regenerates byte-for-byte to the frozen
  `input_sha256`; `load_materialized_freeze(record_bytes,
  expected_record_sha256=...)` fails closed unless the file bytes hash to the
  materialization-time anchor and every embedded envelope reproduces its
  frozen digest with the pinned context and per-role visibility scope.
- The loaded `freeze` + `role_inputs` are exactly the arguments
  `app8/mla/blind_capture.py::verify_blind_capture` consumes once response
  transcripts exist; any post-freeze byte divergence is rejected there.
- The privileged binding reuses `frozen_invocation_digest`, so a request that
  was never frozen against a valid profile fails closed at materialization,
  and at dispatch the envelope digest must equal the ledger reservation taken
  before the response event.

## What this does NOT prove

- The code cannot observe wall-clock time: "before first response" is a
  property of the caller's trusted orchestration, evidenced by the record
  anchor existing before dispatch and its privileged digests matching the
  pre-response ledger reservation (`pre_output_ordering_proven_by_code` is
  always False).
- No provider invocation, provider-side isolation, oracle, semantic gold,
  promotion or release qualification is attested; every authority flag stays
  False.
- A materialized freeze says nothing about response format; the offline
  rehearsal gate (`MLA_ROLE_RESPONSE_CONTRACT.md`) covers output shape and
  can only examine real response bytes after the producing call is metered.

## Unit scope and commands

15 targeted tests: end-to-end into the real `verify_blind_capture`,
production digest equality, deterministic record bytes + pre-output flag,
exact four-field envelope shape, digest-anchor mismatch, embedded envelope
tamper, downgraded frozen flag, unknown record identity, profile
family/provider mismatch, invalid precommitted digests, missing role,
unbound request body, post-freeze byte divergence rejected by the real
verifier, and overwrite refusal. No credentials, network or Docker needed.

```bash
python -m pytest tests/qualification/test_v04_mla_blind_freeze_materializer.py -q
python -m pytest tests -q
```

**Not yet performed:** any real v5 materialization against real frozen case
payloads, any privileged dispatch, any provider response capture; the
materializer has only ever run on synthetic test inputs.
