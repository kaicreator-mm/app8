# V04-MLA fixed model-call/resource cap preflight

Supports #166 independent R1 review F04/F05. The operator **must choose concrete** positive integer, precommitted maximum token/cost/time budgets before any real invocation; no defaults are an authorization. Use cost in smallest integer micro-units of the operator's declared currency, not floating-point USD. The code fixes **12 base calls** (P/R/X × four assets), **up to 12 J calls**, hard **24 total calls**; one J per independently eligible case, no repeated model debates. The previous J public queue cap is corrected from 24 to 12.

`scripts.v04_mla_budget_gate.check_budget` validates a complete declared cap object, exact per-asset/role call uniqueness, J eligibility, nonnegative measured counters and per-call/aggregate ceilings. Missing 12 baseline calls => BLOCKED. It reports all usage as **untrusted/caller-reported**, with `trusted_usage_and_provider_identity_verified=false` and `pre_dispatch_budget_enforcement_verified=false`.

**Security boundary:** This deterministic validator is not a provider, live dispatcher, authenticated billing source or trusted ledger. A local trusted model-invocation adapter must atomically reserve budgets *before* each request, retain actual provider usage receipts/cumulative spending and stop on timeouts, then recheck the same fixed caps; no user-supplied cost counters or timestamps may certify a real pilot. Numeric examples in tests are synthetic only and are **not owner-approved budgets**. Independent protocol/metric freeze, real Oracle and human decision proof remain open; no empirical PASS or Release.

```bash
python -m pytest tests/qualification/test_v04_mla_budget_gate.py tests/qualification/test_v04_mla_jh_queue.py -q
python -m pytest tests -q
```
