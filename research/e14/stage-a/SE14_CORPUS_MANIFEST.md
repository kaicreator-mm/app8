# SE14 Stage A — Frozen Candidate Corpus

Status: CANDIDATE_FOR_FRESH_REVIEW
Execution: INPUT_FREEZE_ONLY
Owning issue: #49
Protocol blob: 177c70ffa6c7e89da45d438738a809523e44c0d3
Source-pack authority: docs/product/v0.1-successor/l1/SE10_SOURCE_PACK_MANIFEST.md
Source-pack blob: 4b3c9b62b1899653524f19a286924f942605210a

## Purpose

Freeze the underlying search-item identities and source anchors before relevance judgments or search results exist. This is not the final REGISTRY/CAPABILITY index view and contains no relevance labels.

## Frozen allocation

Exactly 64 entries: 16 per asset across FFmpeg, pandas, MinIO and LibreOffice. All entries bind to files already frozen in SE10; no live-web expansion is allowed after result visibility.

| ID | Asset | Ordinary user-facing item | Native surface | Frozen source path | Source blob |
|---|---|---|---|---|---|
| F01 | FFmpeg | Transcode media between formats | CLI | `doc/ffmpeg.texi` | `5d2eb4d1e38d271baf908cea880ba323ce138129` |
| F02 | FFmpeg | Inspect media streams and metadata | CLI | `doc/ffprobe.texi` | `254de54f0b134170154c5d5d289a0aa6ff47b8b6` |
| F03 | FFmpeg | Apply video filter graph | CLI | `doc/filters.texi` | `04496d338feea803bbaec92ba0896ee4b5b12567` |
| F04 | FFmpeg | Apply audio filter graph | CLI | `doc/filters.texi` | `04496d338feea803bbaec92ba0896ee4b5b12567` |
| F05 | FFmpeg | Select and map streams | CLI | `doc/ffmpeg.texi` | `5d2eb4d1e38d271baf908cea880ba323ce138129` |
| F06 | FFmpeg | Stream-copy without re-encoding | CLI | `doc/ffmpeg.texi` | `5d2eb4d1e38d271baf908cea880ba323ce138129` |
| F07 | FFmpeg | Choose input container format | CLI | `doc/formats.texi` | `0722e3f5125c3c9d7f454588817ad9bbc59e6140` |
| F08 | FFmpeg | Choose output muxer | CLI | `doc/muxers.texi` | `a2489760fcd9d95cc8eda1371b1d29e4f3ddaf5e` |
| F09 | FFmpeg | Read a specific demuxer/input format | CLI | `doc/demuxers.texi` | `76100551931992472f6e138e95a503dffe286835` |
| F10 | FFmpeg | Use network/file protocols | CLI | `doc/protocols.texi` | `1d43fa6327fb5b5ea0486e5a58c2fe2fc9547e2e` |
| F11 | FFmpeg | Seek before or during processing | CLI | `doc/ffmpeg.texi` | `5d2eb4d1e38d271baf908cea880ba323ce138129` |
| F12 | FFmpeg | Limit output duration | CLI | `doc/ffmpeg.texi` | `5d2eb4d1e38d271baf908cea880ba323ce138129` |
| F13 | FFmpeg | Set or map metadata | CLI | `doc/ffmpeg.texi` | `5d2eb4d1e38d271baf908cea880ba323ce138129` |
| F14 | FFmpeg | Remux streams into another container | example | `doc/examples/remux.c` | `1a88f7efe6c7bd7e5b7262c2dd8a3816ee459981` |
| F15 | FFmpeg | Programmatic transcoding example | example | `doc/examples/transcode.c` | `5cad3e1aec23eed05912b19178159f33f7cca1d5` |
| F16 | FFmpeg | Programmatic audio filtering example | example | `doc/examples/filter_audio.c` | `ad77bf1f897981e19aaac785a43629e32b347389` |
| P01 | pandas | Read tabular data into a DataFrame | Python API | `doc/source/getting_started/intro_tutorials/02_read_write.rst` | `e46a0075edd05c36e87e493c74797fc17d4d0df8` |
| P02 | pandas | Write tabular data to external formats | Python API | `doc/source/getting_started/intro_tutorials/02_read_write.rst` | `e46a0075edd05c36e87e493c74797fc17d4d0df8` |
| P03 | pandas | Select rows and columns | Python API | `doc/source/getting_started/intro_tutorials/03_subset_data.rst` | `9805e3b6e995bfc3e89d3fab582b04b1eea2c38a` |
| P04 | pandas | Create plots from tabular data | Python API | `doc/source/getting_started/intro_tutorials/04_plotting.rst` | `e9f83c602d086a26250346e6bdd57989990f8c3a` |
| P05 | pandas | Create derived columns | Python API | `doc/source/getting_started/intro_tutorials/05_add_columns.rst` | `481c094870e129a86e9c7359a4e3ae2bb9c35a5f` |
| P06 | pandas | Calculate summary statistics | Python API | `doc/source/getting_started/intro_tutorials/06_calculate_statistics.rst` | `1399ab66426f4801b566d165350c133f4d622e9a` |
| P07 | pandas | Reshape table layout | Python API | `doc/source/getting_started/intro_tutorials/07_reshape_table_layout.rst` | `e4b34e3af57bfbd91757e323b6ca1cd8c9b0e02e` |
| P08 | pandas | Combine DataFrames | Python API | `doc/source/getting_started/intro_tutorials/08_combine_dataframes.rst` | `024300bb8a9b008f5f433edea74fe4892f869dac` |
| P09 | pandas | Work with time-series data | Python API | `doc/source/getting_started/intro_tutorials/09_timeseries.rst` | `820def3072b26d0629e4c4ba4d91d834489b7ae9` |
| P10 | pandas | Process string/text columns | Python API | `doc/source/getting_started/intro_tutorials/10_text_data.rst` | `8493a071863c43cfd37ddd6b41358ced56e45442` |
| P11 | pandas | Group and aggregate records | Python API | `doc/source/user_guide/groupby.rst` | `b7401f6ac20ca4e7c398169dcc32217dd1b889dd` |
| P12 | pandas | Merge and join tables | Python API | `doc/source/user_guide/merging.rst` | `339b10aa7fd73a5ccb02b3a7b17102dc698b061d` |
| P13 | pandas | Pivot and reshape data | Python API | `doc/source/user_guide/reshaping.rst` | `c43a425489c985da4428176a2f0d4c3759f83206` |
| P14 | pandas | Handle missing data | Python API | `doc/source/user_guide/missing_data.rst` | `64b76ad4f0d31e6805199d20fe223a1eef723efd` |
| P15 | pandas | Index and label-select data | Python API | `doc/source/user_guide/indexing.rst` | `b2a4a4115261ca3629a979b7919a3d653243f2e8` |
| P16 | pandas | Resample or transform time series | Python API | `doc/source/user_guide/timeseries.rst` | `d574ade09985edff667998cbf0cf525095c991eb` |
| M01 | MinIO | Configure bucket lifecycle rules | server/API | `docs/bucket/lifecycle/README.md` | `6888838f77eb0955f575754be289c43d75f5d086` |
| M02 | MinIO | Configure bucket notifications | server/API | `docs/bucket/notifications/README.md` | `062f75fe60dc6f5466e3c06e50f8aad6a85a0254` |
| M03 | MinIO | Configure bucket replication | server/API | `docs/bucket/replication/README.md` | `829d98f005cf276258d39014933d40ed5c12b68c` |
| M04 | MinIO | Configure object retention | server/API | `docs/bucket/retention/README.md` | `c5087b22acd4a451b025cbcd5e2f36444ca0a018` |
| M05 | MinIO | Enable bucket versioning | server/API | `docs/bucket/versioning/README.md` | `aeb9aa001804588e8be79492e3a45a7178f2cf90` |
| M06 | MinIO | Configure compression | server config | `docs/compression/README.md` | `cc7bac663f95aaf49a8efcf0bf78a44cccbf827d` |
| M07 | MinIO | Configure server settings | server config | `docs/config/README.md` | `9434752741b765ae9956452607411802c899d893` |
| M08 | MinIO | Use access-management plugin | plugin | `docs/iam/access-management-plugin.md` | `f18b1e11ca2d4c2045fb661b8fa4ad46e16ab439` |
| M09 | MinIO | Use identity-management plugin | plugin | `docs/iam/identity-management-plugin.md` | `01f80265d6f5a461d2b039b62fbb006ca40e40b2` |
| M10 | MinIO | Configure key management | server config | `docs/kms/README.md` | `86d9d8c0556d67fe5630e9cb5a555f5061a1b37a` |
| M11 | MinIO | Configure event/lambda targets | server config | `docs/lambda/README.md` | `7e571e850a479bda9211d1ebdc981ce2da8dfe14` |
| M12 | MinIO | Configure transport/security behavior | server config | `docs/security/README.md` | `9d56e4b81bb28bdedfc680c6ec3e7d42d49513c4` |
| M13 | MinIO | Query objects with Select | API | `docs/select/README.md` | `7aff355380009b54aa77a4b477fec5398a5400fb` |
| M14 | MinIO | Configure site replication | server/API | `docs/site-replication/README.md` | `8edcc09deedf3098c08fa29232f1ab11a86cb85f` |
| M15 | MinIO | Use STS temporary credentials | API | `docs/sts/README.md` | `62fa48b18584be1b5e21025c94c4486d191d9449` |
| M16 | MinIO | Assume a role through STS | API | `docs/sts/assume-role.md` | `8b9600f7fc0a6c3ffed147d503555d262cd5ea18` |
| L01 | LibreOffice | Import or export CSV in Calc | GUI/structured UI | `source/text/scalc/guide/csv_files.xhp` | `5e3cce6fa92a59cabfa371ecfc9ec9968794d3de` |
| L02 | LibreOffice | Apply filters in Calc | GUI/structured UI | `source/text/scalc/guide/filters.xhp` | `ed67334ccb84f228ae1d4342a8b14a84a2464497` |
| L03 | LibreOffice | Enter formulas in Calc | GUI/structured UI | `source/text/scalc/guide/formula_enter.xhp` | `f2232906a11e882f2d0272263fbb59d917c849d7` |
| L04 | LibreOffice | Create a pivot table in Calc | GUI/structured UI | `source/text/scalc/guide/datapilot_createtable.xhp` | `dbbdafdf18b0b93dc20a7ec4dce781ca796270d9` |
| L05 | LibreOffice | Insert a table in Writer | GUI/structured UI | `source/text/swriter/guide/table_insert.xhp` | `ac7b1c40fc37d36ad7b2152ed154a9c3ebb1d761` |
| L06 | LibreOffice | Insert an image in Writer | GUI/structured UI | `source/text/swriter/guide/insert_graphic.xhp` | `2271ece0a73cebf2dbb04f5d779e3ef5f5570429` |
| L07 | LibreOffice | Print a selection in Writer | GUI/structured UI | `source/text/swriter/guide/print_selection.xhp` | `aaccf8316b7890bda9dd82f95a4986941ec30ca0` |
| L08 | LibreOffice | Enable automatic spell checking | GUI/structured UI | `source/text/swriter/guide/auto_spellcheck.xhp` | `3ed8f195171ecdf8dec17e6f6e59f33117f7da29` |
| L09 | LibreOffice | Rearrange slides in Impress | GUI/structured UI | `source/text/simpress/guide/arrange_slides.xhp` | `3adbc326626c0098f37e45729372ede0f56e4e70` |
| L10 | LibreOffice | Apply slide transitions | GUI/structured UI | `source/text/simpress/guide/animated_slidechange.xhp` | `78d8b5a3a2323a8041a7f1701d4b06dd5ac83a68` |
| L11 | LibreOffice | Print a presentation | GUI/structured UI | `source/text/simpress/guide/printing.xhp` | `1450c7d424a54f9c0e01fe9c5f5884e042624742` |
| L12 | LibreOffice | Insert a table in Impress | GUI/structured UI | `source/text/simpress/guide/table_insert.xhp` | `631a815e5f3e848e727aa95e100256ae1a1004c9` |
| L13 | LibreOffice | Save a document | GUI/structured UI | `source/text/shared/guide/doc_save.xhp` | `15c4d8c071087d364b7fade01d7e0b78d80c0d9c` |
| L14 | LibreOffice | Export a document to PDF | GUI/structured UI | `source/text/shared/guide/pdf_params.xhp` | `a107c81def3499aab0f9f52c2c10eb8dcba72e1c` |
| L15 | LibreOffice | Insert a chart | GUI/structured UI | `source/text/shared/guide/chart_insert.xhp` | `2c8876398b8dee88c060fce46a33ef8d199011c6` |
| L16 | LibreOffice | Manage document templates | GUI/structured UI | `source/text/shared/guide/manage_templates.xhp` | `c88404b0d8497a51a16289dbfd4789e12b5a9973` |

## Fair-baseline rule

The final REGISTRY_BASELINE must retain every ordinary field naturally available for the same underlying item: operation/tool name, description, argument/input/output schema and parameter descriptions where present, categories/tags/keywords where present, provider/software/interface identity, install/package identity, documented version/platform/auth/runtime requirements, official help/examples and native error descriptions. Missing upstream fields remain missing; they are not synthesized to weaken or strengthen either arm.

The CAPABILITY_ARM uses the same 64 entries and all baseline fields, adding only app8-specific semantic Capability identity, evidence-backed variants/constraints/negative evidence/readiness/currentness/binding-equivalence semantics.

## Anti-cheating

- entry set is frozen before relevance labels and ranked results;
- no item substitution after query/result inspection;
- no arm-specific underlying item or software-version changes;
- future metadata extraction must retain provenance to these exact source blobs;
- relevance judgments remain independently authored and absent from this artifact.

```text
SE14_ENTRIES=64
ASSETS=4
ENTRIES_PER_ASSET=16
RELEVANCE_LABELS=NOT_CREATED
INDEX_VIEWS=NOT_BUILT
SEARCH_RESULTS=NOT_RUN
SE14_GATE_PASS=NO
PRODUCT_FREEZE=NO
L2_READY=NO
```
