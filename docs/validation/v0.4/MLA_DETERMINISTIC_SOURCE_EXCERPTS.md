# V04-MLA-1 FFmpeg deterministic source excerpt — pre-output candidate

**Scope:** Issue #166 prospective four-software **24-case** campaign only; six FFmpeg slots selected by frozen seed. This helper compiles source context, **not** new cases, extra LLM calls, behavioral observations, real signed evidence, Gold, or release. **State: SOURCE RULE IMPLEMENTED, NOT REVIEWER FROZEN / NOT A PROVIDER RUN.**

## Rationale

The exact six FFmpeg source blobs include a 970 KB filter manual, which by itself breaches the existing 500,000-byte sealed HTTPS request ceiling. The contract requires **four assets × one batch per P/R/X role** (12 base invocations); neither silent batch splitting nor a bigger request cap is approved. The raw 24 source Git blob identities stay unchanged.

## Fixed, input-independent rule

For each of the same six frozen FFmpeg paths, first verify its COMPLETE source bytes against the reviewed allowlist Git blob and its own exact Git SHA-1. **If full blob size is <=32,768 bytes, copy all bytes; otherwise use the exact leading bytes up to the last LF at or before byte 32,768.** Do not search/cherry-pick favorite sections, append context, change offsets after any model output, vary the rule by P/R/X, or substitute a selected anchor. The same six excerpts, byte-for-byte, must be supplied to all P/R/X roles; only the authorized blinded role instruction differs. Six times 32,768 bytes caps total source excerpt payload at **196,608 bytes** before outer JSON encoding and role prompt; final exact HTTPS request body MUST independently pass the existing 500,000-byte cap.

The emitted private envelope records per selected case ID the **original full source blob Git SHA1, original size, partial/full label, complete-prefix byte size and excerpt SHA256**. Raw text and audit markers remain in the sealed, out-of-repository store. The final request body hash, `frozen_invocation_digest`, 12 model input pins and campaign admission subject MUST be computed on final exact serialized request bytes **after** applying this fixed rule, then approved/frozen before any evaluated P output.

## Claim-semantic fail-closed gate

The selected source excerpt is NOT the full source. Before pre-output admission, a DIFFERENT independent reviewer verifies that all six exact unchanged private user jobs and required claim/negative-boundary text have adequate evidence **within their resulting excerpts**. The compiler receives private `private_required_markers_by_case`, 1–12 bounded verbatim snippets for each of the six jobs, and refuses any missing marker. Audit markers are coverage checks only and do NOT influence which bytes the compiler returns. An absent claim/section => **BLOCKED with this six-case denominator intact**, or change the rule via a newly reviewed pre-output protocol amendment, never silently classify behavior as source-only.

The author preview inspected the selected FFmpeg six cases against the **first 32 KiB** of each frozen blob: generic codec bitrate/bitexact, whitelist/build protocols, automatic selection/-map and option ordering (automatic selection appears after 16 KiB but before 32 KiB), raw data muxer, split/crop/vflip/overlay filtergraph, and examples build workflows are all represented. **This is author source inspection, not independent semantic approval.**

## Proof and limitations

- Only an independently reviewed exact-head host check of `scripts/v04_mla_deterministic_source_excerpt.py` and its original six private blobs can approve the source-coverage subgate. All markers are private and must not be put in Git.
- The source digest remains the original full blob, not the excerpt digest. Both are recorded: no presenting truncated source context as entire reviewed source pack.
- Prevents oversized FFmpeg private prompt without changing 24-case selection, without obtaining outcome-based evidence and without exceeding 12 base invocations.
- No permission to dispatch: operator still must explicitly pin P app8 predictor, R/X independent families, real credentials, model/version/sampling/pricing, budget/J eligibility, protocol/scorer, independent provisional admission and an external GitHub witness. Runtime behavior needs exact approved targets and calibrated oracle; five behavior-intent cases remain BLOCKED until then. Original SE10/SE11 = NOT_RUN; Release = NO.
