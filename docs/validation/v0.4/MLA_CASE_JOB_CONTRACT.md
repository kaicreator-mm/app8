# V04-MLA per-case prospective user-job/claim freeze digest

Supports #166 independent Fresh R1 **F01** code-side gap. The former anchor-only 24 slots were not exact user jobs. `scripts.v04_mla_case_job_contract.prepare_case_job_commitments` now validates 24 operator-proposed **untrusted** `user_job`, `claim_contract`, `negative_boundary`, `evaluation_intent`, case/source identities and publishes only their digests. Six job digests per asset define one source-context SHA256. `verify_role_job_context` checks P/R/X input capture source-context digests against exactly those prospective jobs and the source selection seed.

This closes **structural** per-slot semantic-job identity drift and prohibits caller self-declaration of human Gold. The operator must retain raw jobs, user-task authoring context, provenance and review decisions privately; never publish sensitive task/fixture text.

**Not yet proof:** actual semantic correctness, independence of the job author, trusted pre-prediction freeze time, provider request bodies, blinded isolation, human authority, signed Oracle or Release. A caller could create both jobs and matching outputs after the fact; trusted append-only chronology is still required. Functions return `trusted_pre_prediction_freeze_attested=false` and `trusted_provider_invocation_proven=false`.

```bash
python -m pytest tests/qualification/test_v04_mla_case_job_contract.py -q
python -m pytest tests -q
```

No Docker, model credentials or private Gold required for synthetic tests.
