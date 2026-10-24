# V04-MLA P/R/X provider-neutral transcript capture — structural boundary

Issue [#166](https://github.com/kaicreator-mm/app8/issues/166). Product decision [V04-PO-MLA-001](../../product/v0.4/MULTI_LLM_OWNER_DECISION.md).

`app8/mla/blind_capture.py::verify_blind_capture` validates a **trusted caller's** precommitted, public-safe prompt metadata envelope (one each for P tested app8 predictor, R independent reference proposer, X challenger) and three exact captured transcript byte digests. It does **not** call an LLM, log full transcripts into Git, build any Gold/hidden truth or certify provider-side isolation. Execute this function *only inside a trusted orchestration service* supplied with **actual sent** prompt metadata and actual received response bytes from a sealed store.

The freeze must precede all P/R/X outputs; required pins: frozen SE10 source pack blob, one common frozen source context SHA, exact P/R/X model family/provider/version, prompt/sampling SHA256 and actual envelope byte SHA256. Allowed role envelope keys are only `source_pack_git_blob`, `source_context_sha256`, `task_instruction_sha256`, `visibility_scope`, with role-specific visibility scope. No hidden truth, decisive fixture, oracle verdict or evaluator outcome fields are permitted. Duplicate JSON keys, nonfinite constants, role swapping, unknown context keys and changed prompt bytes are rejected. Pre-output materialization of exactly these freeze bytes, bound to the exact privileged outbound request digest, is scripted in `scripts/v04_mla_blind_freeze_materializer.py` (`MLA_BLIND_FREEZE_MATERIALIZATION.md`); the v4 pilot produced no such record and none may be created retroactively from sealed v4 results.

R and X should use different model families. Same-family R/X is flagged `PROVISIONAL_CORRELATED_MODEL_FAMILY` and never silently treated as independent model agreement. Optional later Judge J needs a separate, conflict-triggered gate; do not run J on every case. Preserve raw transcripts off-repo with scoped access; export only public role/config hash metadata and transcript SHA values. Any attempt to claim provider-origin execution, oracle isolation or behavior truth from this pure function is invalid; it always emits the corresponding proof flags as `false`.

Unit scope: 10 synthetic tests on typed role capture, changed prompt digest, unknown truth fields, swapped contexts, invalid sampling hashes, missing outputs and correlation warning. No local LLM credentials or real Docker needed for this structural source gate.

```bash
python -m pytest tests/qualification/test_v04_mla_blind_capture.py -q
python -m pytest tests -q
```

**Not yet performed:** invoking actual independent model providers, trusted provider-side raw transcript capture, source context reconstruction by exact original source bytes, independent real oracle calibration, 24-case pilot, human final cards, original SE10/SE11 PASS or Product Release.
