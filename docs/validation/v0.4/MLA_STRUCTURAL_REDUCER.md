# V04-MLA-1 public-only pilot structural reducer

Supports [#165](https://github.com/kaicreator-mm/app8/issues/165); approved Product direction [V04-PO-MLA-001](../../product/v0.4/MULTI_LLM_OWNER_DECISION.md); protocol candidate [V04-MLA-1](../../product/v0.4/MULTI_LLM_SUCCESSOR_PROTOCOL.md).

**This is not a semantic Gold generator, a real-software behavior verifier, a trusted execution runner, an empirical scorer, a human-review attestation, or release qualification.** No attempt is made to repurpose historical `commit_gold.py` or `commit_hidden.py` human claims for LLM-created candidate data.

## Inputs and operation

The public-only schema is `research/mla/v04-mla-pilot-public.schema.json` with exactly 24 opaque case IDs, six for each of the four frozen assets. All cases are declared `reference_origin=LLM_PROPOSED`; each uses a verified frozen source anchor (path + Git Blob SHA1), P/R/X transcript SHA256 digests, optional *unverified* behavior observation digest, and `oracle_visible_to_predictor=false`. Semantic claims, hidden oracle labels, HMAC seeds, decisive fixtures and private execution outputs are **forbidden** in this public file.

```bash
python scripts/v04_mla_pilot_reducer.py \
  --pilot-public "<PUBLIC_ONLY_V04_MLA_24_CASE_JSON>" \
  --out "<PUBLIC_ONLY_RESULT_JSON>"

python -m pytest tests/qualification/test_v04_mla_pilot_reducer.py -q
```

The reducer checks: original frozen 76-file allowlist Git blob, source-pack identity, typed exact root/case fields (no extra private-semantic truth), exact four-asset 6×4 candidate cohort and unique opaque IDs, valid SHA fields, model candidate origin, no oracle visibility, and deterministic per-asset human-sample selection by precommitted SHA256 seed. **All unresolved high-impact cases enter the human queue even if every model agrees.** One seeded sample per asset is mandatory; when mandatory + sample exceeds 12 cards, return `BLOCKED_HUMAN_REVIEW_BUDGET` and exit 2. Do not change the original denominator.

Other structurally valid outputs return only `PROVISIONAL_REQUIRES_REAL_ORACLE_AND_HUMAN_REVIEW`. Observation SHA is a pointer, not a verified signature; hash length cannot certify a real runtime measurement. No source-only assertion, model vote or human `CONFIRM` may override a deterministic contradiction or become a verified runnable Capability without the later evidence-verifier integration.

## Test/qualification gates

13 synthetic tests cover exact cohort, reproducible sampling, mandatory unresolved cases, review budget overflow, fake human reference origin, consensus self-certification prevention, oracle leakage, additional private truth fields, source blob swap, duplicate case IDs/JSON keys, allowlist byte drift, and JSON Schema correspondence.

**Local exact-head tests required before merge:** targeted + `python -m pytest tests -q`; do not rerun unrelated Docker real probes. This is support-only and **not** the four-software 24-case evaluated trial. No true run has yet produced model predictions, executed the four approved targets or sampled human reviews.

```text
V04_MLA_STRUCTURAL_GATE=SOURCE_BOUND_CANDIDATE_ONLY
MODEL_GENERATED_HUMAN_GOLD=NEVER
REAL_EXECUTION_ORACLE=NOT_INTEGRATED
EVALUATED_STUDY=NOT_RUN
PRODUCT_RELEASE_QUALIFIED=NO
```
