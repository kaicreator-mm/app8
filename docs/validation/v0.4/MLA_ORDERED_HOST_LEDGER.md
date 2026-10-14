# V04-MLA privileged local ordering and reservation ledger

Supports #166 independent Fresh R1 **F01 chronology / F04 F05 runtime reservation / N1 N2 time-order** at the **local trusted-host boundary**.

`app8.mla.ordered_host_ledger.OrderedMLAHostLedger` implements one-tenant, private **SQLite WAL-free synchronous FULL** event chain. Each event has monotonic sequence, HMAC-SHA256 binding to the previous event, no-update/no-delete SQL triggers and `BEGIN IMMEDIATE` transactional inserts. The DB must use a durable absolute on-disk path (not `:memory:`, relative paths or a symlink). A **single immutable** pre-run freeze is required before the first model reservation, with all 12 exact P/R/X asset-role request digests, 24-case/claim/protocol/scorer digests, J-eligible case IDs and positive integer token/time/currency/cost ceilings.

All four P predictions must be dispatched and settled before R/X, and all twelve base batches must precede J. This strengthens local isolation order without establishing provider-side blindness. Every call must first obtain a durable `RESERVE` event. It cannot duplicate P/R/X, change input digest, exceed 24 total calls / 12 J, start J before all base calls, or exceed **worst-case** per-call/aggregate pre-dispatch reservation. Ambiguous pending response blocks further dispatch. `record_response` requires exact usage counters and response SHA, and checks reserved caps. Reopening the DB verifies the chain against the isolated service's secret key.

**Trust limits:** This is local ordered provenance, *not external independent timestamping*, attested remote API invocation, authenticated provider metering, genuine P/R/X blinding, semantic truth or approved real target. The caller must keep key and DB outside model/hostile process reach, perform **actual model calls through a privileged adapter** only after `reserve`, and retain transport identity + request/response evidence. An independent witness must anchor at least the initial and final chain MAC to protect against privileged DB rollback/replace. The 24-case pilot is still **not authorized** until independent approval of target/Oracle, protocol R2 and trusted provider integration. No releases/promotions.

Synthetic exact-HEAD tests:

```bash
python -m pytest tests/qualification/test_v04_mla_ordered_host_ledger.py -q
python -m pytest tests -q
```

Do not use host-local MAC/clock as independent Gold, behavior PASS or overall release approval.
