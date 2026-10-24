# V04-MLA model budget calibration from real dispatch telemetry

Derived exclusively from the V04-MLA-1 campaign's own sealed dispatch records
(v1: 3 settled + 1 truncated; v2: 7 settled + 1 truncated; raw transcripts in
the private sealed stores, per-call meters published in Issue #166). These are
**observed behaviors of the called models on this task family**, not provider
documentation, and they are the reason the v3 budget differentiates
`max_tokens` per body instead of one uniform value.

## Observed per-call data

| call | model | max_tokens | finish_reason | completion | reasoning | content chars |
|---|---|---|---|---|---|---|
| P-FFmpeg | deepseek-v4-pro | 8192 | stop | 7,285 | — | — |
| P-pandas | deepseek-v4-pro | 8192 | stop | 6,385 | — | — |
| P-MinIO | deepseek-v4-pro | 8192 | stop | 6,279 | — | — |
| P-LibreOffice (v1) | deepseek-v4-pro | 8192 | **length** | 8,192 | 6,547 | 6,629 (cut) |
| R-FFmpeg | glm-5.3-flash | 16384 | stop | — | — | — |
| R-pandas | glm-5.3-flash | 16384 | stop | — | — | — |
| R-MinIO | glm-5.3-flash | 16384 | stop | — | — | — |
| R-LibreOffice (v2) | glm-5.3-flash | 16384 | **length** | 16,384 | 14,517 | ~7,844 (cut) |

P-FFmpeg/pandas/MinIO/LibreOffice all completed at 16384 in v2; wall-clock
observed 65–83s per call at 6–7k completions (~90–110 output tokens/s on
deepseek-v4-pro).

## Lessons (each paid for by a real truncated call)

1. **Thinking tokens share the completion budget.** `reasoning_tokens` is
   metered inside `completion_tokens` for both deepseek-v4-pro and
   glm-5.3-flash; a response truncated at exactly `max_tokens` with a large
   reasoning share is the signature.
2. **Reasoning scales with the granted budget.** glm-5.3-flash reasoning on
   the LibreOffice six-case task consumed 14,517 of 16,384 (~89%); sizing the
   budget barely above the observed need does not cap reasoning.
3. **The answer itself is small.** Six-case typed JSON needs only ~2–7k
   content tokens per asset; the budget driver is reasoning, not output
   volume. Splitting a batch into more calls does not shrink reasoning.
4. **LibreOffice is the reasoning-heavy asset** (verbose xhp/XML sources);
   FFmpeg/pandas/MinIO completed well inside 16,384 for every role tried.
5. **Input size was never the constraint** (39–402KB bodies, up to ~105k
   prompt tokens, all billed and completed normally).
6. **Truncation is expensive by design**: the call is billed in full, the
   dispatch fails closed, the ledger reservation stays outstanding, and no
   retry is permitted — budget must be sized before dispatch, with margin
   above observed reasoning, not at it.

## Sizing rule for future campaigns

`max_tokens >= observed_reasoning_on_the_asset / 0.6` (i.e. keep reasoning
under ~60% of the budget), and never size exactly at a previous truncation
point. For this study: P/X bodies 16384 everywhere except LibreOffice-pair
32768; per-call wall 420,000 ms at the observed token rate. Input excerpts and
batching (6 cases/call) stay as frozen: input is not the binding constraint
and smaller batches would triple the call count without shrinking reasoning.
