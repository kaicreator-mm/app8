# V04-MLA deterministic prospective 24-case source-anchor selection

Supports #166 (pilot). Implements the R1 preregistration's **6 distinct frozen anchor paths per asset** selection from the original SE10 reviewed 76-source allowlist, using SHA256 ordering of `seed_sha256:asset:path:git_blob`. Case IDs map deterministically to ranks 001–006 for FFmpeg/pandas/MinIO/LibreOffice. Any missing/duplicated/substituted mapping, drifted allowlist, invalid seed or changed cohort rejects before trial scoring.

`scripts.v04_mla_anchor_cohort.select_anchors` returns an auditable safe assignment digest. `validate_anchor_assignment` composes the public frozen-source pilot validator and exact slot comparison against the supplied seed. Retain the raw seed and snapshot independently in a **trusted pre-run ledger**. Source code alone cannot prove the caller fixed seed or user-job instruction before predictions; both functions explicitly return `pre_prediction_freeze_attested=false`. This is **source identity**, not model-produced human Gold, reviewed task semantics, an actual model run, behavioral Oracle or Product Release.

Exact HEAD tests required:
```bash
python -m pytest tests/qualification/test_v04_mla_anchor_cohort.py -q
python -m pytest tests -q
```

No real LLM credentials or Docker required. Historical SE10/SE11 source blobs unchanged, original studies NOT_RUN.
