# V04-MLA-1 R2 P1-C — independent-from-operator mandatory H routing

The new `derive_mandatory_h_review(...)` operates on exactly 24 frozen job intents and all four source-bound P/R/X typed captures (6×4×3). It reuses `verify_role_job_context` and `validate_role_case_payloads` before deriving H-required exceptions. Every prospective `BEHAVIOR_CANDIDATE` with a P positive candidate and X nonempty challenge requires H/deferral; operator-declared `high_impact_unresolved=false` **cannot suppress** that mandatory card. Operator can only add more mandatory H. `assess`'s fixed per-asset hash-selected baseline cards remain included. If more than 12 cards are required, status is `BLOCKED_HUMAN_REVIEW_BUDGET`, never sample/cherry-pick downward.

All typed role outputs are *model candidate claims*, not independent semantic contradictions or Gold. The deterministic predicate is intentionally conservative, so up to 24 behavior-intent slots may cause a legitimate BLOCKED pilot. Source-only P/X challenges count as **unverified candidate disagreements** for stratified metrics, not as high-impact behavior exceptions automatically. Independent reviewer must approve this rubric before output and inspect frozen 24 job texts versus intent. The existing public-only `assess` remains a structural preview, **not** the authoritative H routing entrypoint. The new report refuses to assert real provider calls, calibrated Oracle, authoritative H or release.

This PR stacks on PR #183, which freezes the intent field; do not merge or independently qualify this branch before #183 is merged and its exact-head tests passed. Tests here are no-network synthetic. Relevant R2 review: [#166 R2](https://github.com/kaicreator-mm/app8/issues/166#issuecomment-6172212383).

```bash
python -m pytest tests/qualification/test_v04_mla_conflict_router.py -q
python -m pytest tests -q
```
