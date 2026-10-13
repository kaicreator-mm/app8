# v0.4 SE10 source-anchor curation workpack

Issue [#157](https://github.com/kaicreator-mm/app8/issues/157), prerequisite of [#149](https://github.com/kaicreator-mm/app8/issues/149). **Not** an SE10 Gold dataset, prediction, independent review or empirical score.

On a clean exact-SHA repository checkout (requires only Python stdlib):

```bash
python scripts/v04_se10_source_workpack.py --out /tmp/app8-se10-source-anchors.json
python -m pytest tests/qualification/test_v04_se10_workpack.py -q
```

Script reads **only** the reviewed 76-file source-anchor allowlist and its frozen source-pack manifest; validates original exact Git blob byte identities, fixed 14/21/18/23 source counts, creates stable public index `{asset,source_path,source_blob_sha1}`, and exits 2 on drift. It never reads private Gold or predicts any semantic Capability. For Windows checkout, six pinned inputs already have `text eol=lf` from PR #155.

The public workpack helps a **separate independent** source reader locate task documentation in the already materialized frozen source pack. That curator must **actually read** the source files in a sealed environment and author semantic Gold (≥12 assessable semantic Capabilities/asset) entirely separately from the model under evaluation. A distinct reviewer must verify references, label quality and exact byte SHA before `research/e10/stage-b/commit_gold.py` emits public commitment; neither script does that human job.

What is still missing: independent semantic Gold, independent exact-SHA attestation, public commitment, blind model prediction, independent adjudication and metric result. Until then `SE10=NOT_RUN` and `PRODUCT_RELEASE_QUALIFIED=NO`.

Do not put semantic Gold, reviewer identities, hidden facts or HMAC secrets in public outputs; this workpack contains **only non-semantic source pointers**.
