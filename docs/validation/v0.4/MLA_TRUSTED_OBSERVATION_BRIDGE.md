# V04 MLA — trusted execution Evidence bridge

Supports [#165](https://github.com/kaicreator-mm/app8/issues/165). Follows [owner-approved policy](../../product/v0.4/MULTI_LLM_OWNER_DECISION.md). This adds the **authenticated observation link** which the earlier [public pilot structural reducer](MLA_STRUCTURAL_REDUCER.md) intentionally did not implement.

`app8/evidence/mla_bridge.py::reconcile_observation` takes an opaque MLA candidate case, an existing complete `app8-evidence-v1` record, signed `app8-attested-evidence-v2` receipt, the privileged `AttestationGate`, the append-only `EvidenceStore` and an exact `FrozenExecutionScope`. The scope carries separate full SHA256 identities of source, target, frozen plan and fixture, plus the source→target mapping relation. The API is **trusted-service-only**; never expose `AttestationGate` or verification key to a model.

The adapter **requires all**:
- Original strict Evidence schema and matching opaque `claim_id`/MLA case ID.
- Exact source/target/plan/fixture SHA256 and source→target relation (rejects `DIVERGED/UNRESOLVED` until independently reviewed claim-specific applicability is supported by a separate future gate).
- `EXECUTED`, `DETERMINISTIC_EXECUTION_ADAPTER`, `DETERMINISTIC_ASSERTION_ENGINE` (no LLM-only verdict and no fake block-as-execution).
- The full same Evidence bytes already durably retained in append-only EvidenceStore.
- The same signed receipt authenticated by the existing AttestationGate and present in its durable accepted-nonce ledger; wrong MAC, runner/policy/image, nonce or payload fails closed.

Output contains only safe digests/identifiers, signed deterministic **assessor verdict**, and:
```text
STATUS=AUTHENTICATED_EXECUTION_NOT_INDEPENDENT_SEMANTIC_ORACLE
REAL_EXECUTION_RECEIPT_ACCEPTED=TRUE
INDEPENDENT_BEHAVIOR_ORACLE_VERIFIED=FALSE
CAPABILITY_PROMOTION_ALLOWED=FALSE
FORMAL_PRODUCT_RELEASE_QUALIFIED=FALSE
```

This is deliberately **not** a generic empirical PASS gate. A trusted runner signature is evidence that a bounded execution took place; independently calibrated task semantics/oracle applicability, hidden-truth isolation, human disagreement and scoring remain separate. An old `SUPPORTED` assertion does **not** automatically qualify an MLA claim. Future #166 may consume only trusted bridge receipts plus separately frozen calibrated behavioral oracles; no public caller may set a boolean to bypass that requirement.

13 synthetic unit tests verify authentic retained receipts, missing/forged signatures, incorrect claim ID/target/source/plan pin, absent store record, model-only assessments, nonexecuted results and DIVERGED source→target cases. Real target binaries/LLM/provider credentials/human review are not used.

```bash
python -m pytest tests/evidence/test_mla_bridge.py -q
python -m pytest tests -q
```

Run targeted/full tests at exact PR HEAD before merge. Do not rerun real Docker sandbox probes for this integration-only contract. Formal product Release remains NO.
