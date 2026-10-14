# V04-MLA P/R/X typed six-per-asset candidate payload ingress

Supports #166 and the preregistration R1 author-gap F02. `scripts.v04_mla_role_case_payloads.validate_role_case_payloads` composes the already merged authenticated-byte **structural** P/R/X capture (#169) and 24-case source/cohort batch digest link (#172).

Each of the 12 role×asset batch outputs must be strict UTF-8 JSON with `schema_version=v04-mla-role-batch-v1`, `study_id=V04-MLA-1`, matching `role`, `asset`, source context SHA256, and exactly **six distinct** case rows. Allowed case row keys: `case_id`, `source_anchor`, `origin=LLM_PROPOSED`, role-specific `kind`, untrusted `proposal` (≤2400 chars), bounded `constraints` (≤8, each ≤400 chars). P kind `P_CAPABILITY_PREDICTION`; R kind `R_SEMANTIC_REFERENCE_PROPOSAL`; X kind `X_ADVERSARIAL_COUNTERHYPOTHESIS`. All source case IDs/anchors must match the already validated pilot cohort. Extra hidden Gold, oracle labels, verdicts, duplicate/omitted IDs and changed identities reject.

The returned public report exposes **only case-payload SHA256 commitments**, original batch transcript digests, role/asset counts and explicit FALSE trust/release flags. Model texts remain private. There is **no inference transport, source semantic truth, frozen per-case user-job contract, decisive real-software Oracle, human authority or Release PASS** here. Real P/R/X prompt isolation cannot be inferred from JSON sent by a caller.

Synthetic exact-HEAD tests:

```bash
python -m pytest tests/qualification/test_v04_mla_role_case_payloads.py -q
python -m pytest tests -q
```

No provider credentials, private data, real execution or image build required.
