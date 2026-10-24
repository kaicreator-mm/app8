# V04-MLA-1 role-batch response format contract (v5 rehearsal gate)

**State:** structural output-format contract + offline rehearsal gate, added
after the v4 pilot finding in issue #166 Step H. No model was invoked to
produce or validate this contract; it pins how a *future* P/R/X response must
be rendered, so the defect classes v4 actually hit can be caught in zero-cost
rehearsal. Conformance of a real provider response can only be checked after
the call that produced it is already metered — see the rehearsal-gate section
below.

## v4 lesson (counts only, no content)

All 12 settled v4 batches were structurally bound, bounded and context-pinned,
but **72/72 case rows rendered `source_anchor` as a string** (four different
ad-hoc text shapes across batches) instead of the frozen `{path,blob}` object
the typed contract requires. Every sealed P batch therefore failed the official
`ingest_p_batch_via_app8` ("P source scope or hypothesis kind swapped") and no
P candidate reached the real app8 hypothesis compiler. An in-memory anchor
normalization diagnosis (issue #166 comment 6382634430) showed the anchor form
was the **only** schema defect: once normalized, 4/4 P batches were accepted by
the compiler, all proposals already within the 2000-character bound.

## v5 contract (what a response must look like)

1. **Strict machine-parseable JSON**: exactly one JSON object as the full
   response content. No markdown code fences, prose preamble or wrapper. The
   rehearsal gate detects fence wrappers with a distinct error before any
   structural check — in v4, all four sealed R batches were markdown-fenced
   (```` ```json ```` … ```` ``` ````), so their raw bytes failed strict JSON
   parsing and needed an off-contract fence-strip to inspect at all.
2. **`source_anchor` object form**: each case carries the exact frozen
   `{path, blob}` JSON object for its slot. String renderings fail closed.
3. **Bounds pinned at the strictest enforcement point**: proposal ≤ 2000
   characters (the app8 ingress bound; the 2400-character role-payload bound
   is looser and must not be aimed at), constraints ≤ 8 items × 400 characters.
4. **Identity**: `v04-mla-role-batch-v1`, study `V04-MLA-1`, correct asset/role,
   per-asset `source_context_sha256`, kind per role, `origin=LLM_PROPOSED`.

The machine-readable shape lives in
`research/mla/v04-mla-role-batch-response-contract.schema.json`; the
authoritative binding (frozen slots, role↔kind, context digest) is code, not
schema.

## Rehearsal gate (zero-cost on synthetic bytes only)

```python
from scripts.v04_mla_role_response_contract import validate_response_contract

validate_response_contract(
    role="P", asset="FFmpeg",
    content_bytes=candidate_content_bytes,
    frozen_slots=frozen_six_slots,
    source_context_sha256=pinned_context_sha256)
```

`scripts/v04_mla_role_response_contract.py` is offline and read-only: it
parses the exact candidate bytes, fails closed on every deviation with a
distinct error, and returns digests/metadata only. Run it on synthetic
rehearsal bytes before dispatch — that rehearsal costs nothing. The gate
cannot validate unknown future provider response bytes: the first real
response can only be run through it after the call that produced the bytes
is already metered, and passing rehearsal fixtures does not prove any real
response will conform. If a real sealed response fails the gate, the paid
call is preserved fail-closed as an incident; never silently retry, autofix
sealed output or promote post-hoc normalization into pre-output validity. A
pass proves format conformance of the examined bytes only — never transport
identity, semantic gold, behavior oracle, promotion or release
qualification.
