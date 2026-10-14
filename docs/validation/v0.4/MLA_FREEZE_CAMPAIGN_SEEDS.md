# V04-MLA freeze identity and precommitted sampling seed (R2 P1-A/B groundwork)

R2 review: [Issue #166 — independent R2, P1-A/P1-B](https://github.com/kaicreator-mm/app8/issues/166#issuecomment-6172212383).

The host's **immutable HMAC-protected FREEZE event** now requires:

- `campaign_nonce`: unique operator-generated 256-bit random hex, not a reused placeholder;
- `source_selection_seed_sha256`: pre-output six×four source cohort selection identity;
- `human_selection_seed_sha256`: exact seed that the public reducer uses to choose audit cards;
- `r2_verdict_comment_id`: GitHub comment of the independent review decision, recorded but **not independently verified by the local ledger alone**;
- Existing exact protocol/scorer/source/job/model-input pins, J eligibility and token/currency/wall-clock budgets remain mandatory.

`verify_precommitted_human_seed(public_pilot)` rejects any post-freeze seed change. It does not accept H result labels. Host HMAC plus unique nonce prevents a single in-place freeze from being overwritten, but a privileged operator deleting/rebuilding the entire DB and replaying the same manifest **remains possible**.

**P1-A remains OPEN:** this PR does not perform GitHub API witness verification, does not detect GitHub comment editing, and does not implement an independent unique-run/transport proof. A later WEB change must verify the GitHub server-created witness before actual dispatch; absence must stop live calls. Do not claim that the R2 comment currently is pilot approval: the existing R2 verdict is **NEEDS_REVISION**. This is a **structural freeze hardening PR**, not pilot authorization, Gold or Release PASS.

Tests (synthetic, no LLM/network): `python -m pytest tests/qualification/test_v04_mla_ordered_host_ledger.py tests/qualification/test_v04_mla_https_dispatch.py -q`, then full `python -m pytest tests -q`.
