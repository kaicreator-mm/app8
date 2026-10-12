# SE10 Stage A — Frozen Source Pack Manifest

Status: CANDIDATE_FOR_FRESH_REVIEW
Execution stage: SOURCE_PACK_FREEZE_ONLY
Owning issue: #42
Protocol: docs/product/v0.1-successor/l1/SE10_PROTOCOL.md
Protocol blob: 08f9244a04275c780f778d50f638e332aa5807a2

## 1. Purpose

Freeze the exact source material available to the later SE10 Capability-prediction run.

This manifest is intentionally committed **before** reference/gold construction and before any tested prediction output exists.

No file outside the lists below may be supplied to the SE10 predictor without an independently reviewed protocol amendment made before prediction.

Git blob SHA is the durable content identity. Paths are interpreted relative to the named repository/revision.

## 2. Selection rule

The pack is deliberately user-facing and bounded.

- Prefer official user guides, task tutorials, manuals, built-in/help source and examples.
- Include API/reference material only where it expresses a normal user task or important boundary.
- Exclude test results, issue discussions, future prediction/gold files and app8-generated interpretations.
- Exclude images/static assets unless later protocol amendment proves text is insufficient; no such amendment exists now.
- Do not recursively follow links/includes into unlisted files during prediction.
- Source code is excluded from the predictor pack except explicit upstream examples listed below.
- Missing coverage is scored as a miss; it is not repaired by expanding this pack after predictions.

## 3. FFmpeg

Repository/revision:

~~~text
FFmpeg/FFmpeg
commit = f2bf7a2440d1e49023e4b3ed0e224a8806d388b8
doc tree = 12d67bb6d8bc92ece04fe8ba2bf4fdd9184d0fdb
~~~

Frozen files:

| Path | Blob |
|---|---|
| README.md | cb2acb1ef0926e9c315741057bc44a1727019e9c |
| doc/ffmpeg.texi | 5d2eb4d1e38d271baf908cea880ba323ce138129 |
| doc/ffprobe.texi | 254de54f0b134170154c5d5d289a0aa6ff47b8b6 |
| doc/filters.texi | 04496d338feea803bbaec92ba0896ee4b5b12567 |
| doc/formats.texi | 0722e3f5125c3c9d7f454588817ad9bbc59e6140 |
| doc/codecs.texi | b85f405cf6eaf8c420761be92b0736e3ddef89d1 |
| doc/protocols.texi | 1d43fa6327fb5b5ea0486e5a58c2fe2fc9547e2e |
| doc/muxers.texi | a2489760fcd9d95cc8eda1371b1d29e4f3ddaf5e |
| doc/demuxers.texi | 76100551931992472f6e138e95a503dffe286835 |
| doc/faq.texi | a9872fc2d290c2433f0bbc46fc5254b3df17eb51 |
| doc/examples/README | 6cb4b6e17a2c65cab098e60573d4dddb5c21efbc |
| doc/examples/transcode.c | 5cad3e1aec23eed05912b19178159f33f7cca1d5 |
| doc/examples/remux.c | 1a88f7efe6c7bd7e5b7262c2dd8a3816ee459981 |
| doc/examples/filter_audio.c | ad77bf1f897981e19aaac785a43629e32b347389 |

## 4. pandas

Repository/revision:

~~~text
pandas-dev/pandas
commit = 82c18c170b9aea7cbb96ef54b8005bed07c94220
doc tree = add6affb8bc022dcc9e39c1439418d14732f5841
doc/source tree = d50aabc68afaa7b148d224fdd80dc504e27c35c2
~~~

Frozen files:

| Path | Blob |
|---|---|
| README.md | d2eb7fbb3f6af25086675d8ff8f15a0ad7103a1a |
| doc/source/getting_started/intro_tutorials/01_table_oriented.rst | 55f9a100ce7fced09f0bba9b8ba5a4fc8ee3aac8 |
| doc/source/getting_started/intro_tutorials/02_read_write.rst | e46a0075edd05c36e87e493c74797fc17d4d0df8 |
| doc/source/getting_started/intro_tutorials/03_subset_data.rst | 9805e3b6e995bfc3e89d3fab582b04b1eea2c38a |
| doc/source/getting_started/intro_tutorials/04_plotting.rst | e9f83c602d086a26250346e6bdd57989990f8c3a |
| doc/source/getting_started/intro_tutorials/05_add_columns.rst | 481c094870e129a86e9c7359a4e3ae2bb9c35a5f |
| doc/source/getting_started/intro_tutorials/06_calculate_statistics.rst | 1399ab66426f4801b566d165350c133f4d622e9a |
| doc/source/getting_started/intro_tutorials/07_reshape_table_layout.rst | e4b34e3af57bfbd91757e323b6ca1cd8c9b0e02e |
| doc/source/getting_started/intro_tutorials/08_combine_dataframes.rst | 024300bb8a9b008f5f433edea74fe4892f869dac |
| doc/source/getting_started/intro_tutorials/09_timeseries.rst | 820def3072b26d0629e4c4ba4d91d834489b7ae9 |
| doc/source/getting_started/intro_tutorials/10_text_data.rst | 8493a071863c43cfd37ddd6b41358ced56e45442 |
| doc/source/user_guide/10min.rst | fa810f8270f1da227334b5dc4e112ba552d42b0c |
| doc/source/user_guide/basics.rst | 43eea38b49426ea69700e252c0f4b243691fca9c |
| doc/source/user_guide/indexing.rst | b2a4a4115261ca3629a979b7919a3d653243f2e8 |
| doc/source/user_guide/groupby.rst | b7401f6ac20ca4e7c398169dcc32217dd1b889dd |
| doc/source/user_guide/merging.rst | 339b10aa7fd73a5ccb02b3a7b17102dc698b061d |
| doc/source/user_guide/reshaping.rst | c43a425489c985da4428176a2f0d4c3759f83206 |
| doc/source/user_guide/io.rst | 7a44f9e1a6487a3ea0896c1b91e153f24baaa4ab |
| doc/source/user_guide/timeseries.rst | d574ade09985edff667998cbf0cf525095c991eb |
| doc/source/user_guide/text.rst | 6344f6a2921e4c1a8090fb5d13d5e5c3ecb7c829 |
| doc/source/user_guide/missing_data.rst | 64b76ad4f0d31e6805199d20fe223a1eef723efd |

## 5. MinIO

Repository/revision:

~~~text
minio/minio
commit = 7aac2a2c5b7c882e68c1ce017d8256be2feea27f
docs tree = c837af04d61e18dae4eeb7f9c6ac86866f6b6086
~~~

Frozen files:

| Path | Blob |
|---|---|
| README.md | 84e49277432b54d5e84de2a5be59c75950746d37 |
| docs/bucket/lifecycle/README.md | 6888838f77eb0955f575754be289c43d75f5d086 |
| docs/bucket/notifications/README.md | 062f75fe60dc6f5466e3c06e50f8aad6a85a0254 |
| docs/bucket/replication/README.md | 829d98f005cf276258d39014933d40ed5c12b68c |
| docs/bucket/retention/README.md | c5087b22acd4a451b025cbcd5e2f36444ca0a018 |
| docs/bucket/versioning/README.md | aeb9aa001804588e8be79492e3a45a7178f2cf90 |
| docs/compression/README.md | cc7bac663f95aaf49a8efcf0bf78a44cccbf827d |
| docs/config/README.md | 9434752741b765ae9956452607411802c899d893 |
| docs/erasure/README.md | 48b3cb6bbfe1b5ce6c481939ecc34c089ccd6f44 |
| docs/iam/access-management-plugin.md | f18b1e11ca2d4c2045fb661b8fa4ad46e16ab439 |
| docs/iam/identity-management-plugin.md | 01f80265d6f5a461d2b039b62fbb006ca40e40b2 |
| docs/kms/README.md | 86d9d8c0556d67fe5630e9cb5a555f5061a1b37a |
| docs/lambda/README.md | 7e571e850a479bda9211d1ebdc981ce2da8dfe14 |
| docs/security/README.md | 9d56e4b81bb28bdedfc680c6ec3e7d42d49513c4 |
| docs/select/README.md | 7aff355380009b54aa77a4b477fec5398a5400fb |
| docs/site-replication/README.md | 8edcc09deedf3098c08fa29232f1ab11a86cb85f |
| docs/sts/README.md | 62fa48b18584be1b5e21025c94c4486d191d9449 |
| docs/sts/assume-role.md | 8b9600f7fc0a6c3ffed147d503555d262cd5ea18 |

## 6. LibreOffice

Product source identity:

~~~text
LibreOffice/core
commit = 016fd5d049256dc849111f60870f15201fcd1526
README.help.md = 542cabf61dd88b89e0d7b81812a7d1da7437e81e
helpcontent2 gitlink = 4631d63148d55831c47ce7497dd3bd91ceb8ab5b
.gitmodules maps helpcontent2 -> ../help
~~~

User-help repository identity:

~~~text
LibreOffice/help
commit = 4631d63148d55831c47ce7497dd3bd91ceb8ab5b
source/text tree = 439b13676875141fe7bbe9cecf31446dbd060009
~~~

Frozen files:

| Repository | Path | Blob |
|---|---|---|
| LibreOffice/core | README.md | 8f2a1a887ab8966f1555d5cf1c9f69503cb77371 |
| LibreOffice/core | README.help.md | 542cabf61dd88b89e0d7b81812a7d1da7437e81e |
| LibreOffice/help | README.md | f30f215d6c24eb778c16f5124b67fe8c291d481e |
| LibreOffice/help | source/text/scalc/guide/main.xhp | b1bcb5f72cd1f8023fc7dae6c2d4765e9e452f65 |
| LibreOffice/help | source/text/scalc/guide/csv_files.xhp | 5e3cce6fa92a59cabfa371ecfc9ec9968794d3de |
| LibreOffice/help | source/text/scalc/guide/filters.xhp | ed67334ccb84f228ae1d4342a8b14a84a2464497 |
| LibreOffice/help | source/text/scalc/guide/formula_enter.xhp | f2232906a11e882f2d0272263fbb59d917c849d7 |
| LibreOffice/help | source/text/scalc/guide/datapilot_createtable.xhp | dbbdafdf18b0b93dc20a7ec4dce781ca796270d9 |
| LibreOffice/help | source/text/swriter/guide/main.xhp | 333c83ec91a838a95f309716c6e300e60e7fe3d0 |
| LibreOffice/help | source/text/swriter/guide/table_insert.xhp | ac7b1c40fc37d36ad7b2152ed154a9c3ebb1d761 |
| LibreOffice/help | source/text/swriter/guide/insert_graphic.xhp | 2271ece0a73cebf2dbb04f5d779e3ef5f5570429 |
| LibreOffice/help | source/text/swriter/guide/print_selection.xhp | aaccf8316b7890bda9dd82f95a4986941ec30ca0 |
| LibreOffice/help | source/text/swriter/guide/auto_spellcheck.xhp | 3ed8f195171ecdf8dec17e6f6e59f33117f7da29 |
| LibreOffice/help | source/text/simpress/guide/main.xhp | 924358ca58205fd48ae86a63936dadb8accf7626 |
| LibreOffice/help | source/text/simpress/guide/arrange_slides.xhp | 3adbc326626c0098f37e45729372ede0f56e4e70 |
| LibreOffice/help | source/text/simpress/guide/animated_slidechange.xhp | 78d8b5a3a2323a8041a7f1701d4b06dd5ac83a68 |
| LibreOffice/help | source/text/simpress/guide/printing.xhp | 1450c7d424a54f9c0e01fe9c5f5884e042624742 |
| LibreOffice/help | source/text/simpress/guide/table_insert.xhp | 631a815e5f3e848e727aa95e100256ae1a1004c9 |
| LibreOffice/help | source/text/shared/guide/doc_save.xhp | 15c4d8c071087d364b7fade01d7e0b78d80c0d9c |
| LibreOffice/help | source/text/shared/guide/pdf_params.xhp | a107c81def3499aab0f9f52c2c10eb8dcba72e1c |
| LibreOffice/help | source/text/shared/guide/chart_insert.xhp | 2c8876398b8dee88c060fce46a33ef8d199011c6 |
| LibreOffice/help | source/text/shared/guide/manage_templates.xhp | c88404b0d8497a51a16289dbfd4789e12b5a9973 |
| LibreOffice/help | source/text/shared/guide/data_im_export.xhp | c610286d230e32c230753ad90fdb6c896ca6efa0 |

## 7. Predictor access boundary

The prediction agent/model may receive:

- the textual contents of the exact files above;
- generic app8 SE10 prediction instructions;
- frozen asset identity.

It may **not** receive:

- SE10 gold/reference Capability labels;
- SE11 truth claims/fixtures;
- results from another predictor;
- unlisted docs/source/web pages;
- live internet search;
- issue/PR discussions about the selected software;
- downstream app8 projection/evaluation artifacts.

If tooling cannot enforce this access boundary, SE10 prediction is BLOCKED until isolation is established.

## 8. Stage-A status

~~~text
SOURCE_ASSET_COUNT = 4
FFMPEG_FILES = 14
PANDAS_FILES = 21
MINIO_FILES = 18
LIBREOFFICE_FILES = 23
SOURCE_PACK_FILES_TOTAL = 76

SOURCE_PACK_SELECTION_RULE = FROZEN_CANDIDATE
SOURCE_PACK_EXACT_BLOBS = RECORDED
REFERENCE_GOLD = NOT_CREATED
PREDICTIONS = NOT_RUN
OUTCOMES_VISIBLE = NO

SE10_STAGE_A_WEB_PORTION = COMPLETE_CANDIDATE
FRESH_REVIEW_REQUIRED = YES
SE10_GATE_PASS = NO
PRODUCT_FREEZE = NO
L2_READY = NO
~~~

## 9. What Was NOT Proven

This manifest does not prove the selected files are sufficient, that 12 semantic Capabilities per asset exist, that extraction will pass, or that any described behavior is true in a real executable. Documentation is source material, not behavioral Evidence.
