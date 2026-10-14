# V04-MLA J/H bounded candidate-queue gate

Supports #165 and #166. Reuses the merged exact 24-case/76-source public validation and deterministic human queue. The untrusted metadata ingress accepts **J** only for a predeclared `high_impact_unresolved` case, at most once per case, recording model/prompt/config/output hashes without model-asserted truth. **H** is restricted to the already selected (one per asset + required exceptions, at most 12) cases and reports `CONFIRM/REJECT/DEFER` with digest references and explicit origin `HUMAN_SELF_REPORT_UNVERIFIED`.

No raw LLM transcripts, hidden labels, reviewer identity or decisive fixtures are stored in these public outputs. A caller may fabricate hashes; therefore even complete H self-reports yield `PROVISIONAL_H_SUBMISSIONS_UNVERIFIED` and `human_identity_and_decision_verified=false`. Missing/deferred H decisions or review budget overflow yield `BLOCKED`. J agreement cannot certify Gold or override deterministic evidence; neither H nor J may promote Capability through this gate.

Real independently attested human authority, sealed evidence access, deterministic software Oracle and true model/provider invocations are **not implemented in this PR** and remain #166 validation gates. No empirical SE10/SE11 PASS, formal release NO.

```bash
python -m pytest tests/qualification/test_v04_mla_jh_queue.py -q
python -m pytest tests -q
```

This is a research-only tool under `scripts/`, not an installed runtime API. Unit fixtures are synthetic; no host or provider calls.
