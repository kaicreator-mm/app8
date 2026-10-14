# V04 MLA privileged HTTPS model dispatch bridge

Implements one **real execution entrypoint** toward Issue #166, not a new Gold or scoring layer. `dispatch_frozen_completion` uses `OrderedMLAHostLedger.reserve` *before* a permitted HTTPS POST, hashes exact request bytes and a frozen provider/model/pricing profile into the ledger's 12 frozen model-input commitments, retains raw request/response bytes only in a separately secured local `EvidenceStore`, checks strict response model ID/finished text/provider token counts, and records a bounded conservative **estimated** usage with the HMAC event chain. An ambiguous transport/response leaves an unresolved reservation and prevents retries. No API calls are executed by synthetic tests.

The operator must supply an **out-of-repo protected** `approved_origins` set with HTTPS production endpoints; the adapter forbids IP-literal URLs, redirects, path traversal and dynamic provider URL changes. Secrets are only read from `APP8_MLA_PROVIDER_*` environment variables and must never be stored in Git or placed in model prompts. Local DNS/proxy restrictions, provider billing reconciliation, retention controls and prompt-visibility ACL must be enforced by the actual Build Host. This wrapper handles OpenAI-compatible chat completions with a concrete built-in HTTPS transport; provider-specific API responses that differ must fail closed, not be guessed.

`input_cost_microunits_per_million_tokens` and `output_cost_microunits_per_million_tokens` are **frozen operator pricing assumptions**, not a provider invoice. The adapter reports `trusted_remote_provider_identity_independently_verified=false`, `external_pre_prediction_time_witness_verified=false` and `independent_behavior_oracle_verified=false` even if HTTPS is used. A synthetic/mock transport also must never be accepted as model execution. **Optional J is not supported here** pending independently verified disagreement authorization. This code and #179 do not authorize live calls until independent R2 protocol review, real targets and calibrated oracle approval.

```bash
python -m pytest tests/qualification/test_v04_mla_https_dispatch.py -q
python -m pytest tests -q
```

Actual deployment and any credential/HTTPS test requires the user's local trusted host and explicit pilot authorization.
