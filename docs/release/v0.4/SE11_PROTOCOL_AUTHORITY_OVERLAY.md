# app8 v0.4 — SE11 protocol authority lineage (pre-evaluation overlay)

Scope: #150, parent #147. Status: **PROTOCOL_LINEAGE_RESOLVED / EVALUATED_SE11_NOT_RUN**.

The SE11 Stage-A historical host manifest (`research/e11/stage-a/manifest.json`) and Stage-B README refer to an older protocol Git blob `83abefb13e6a91e6b67a1c94937ca1bcce567aad`. They are immutable historical traceability, **not** the currently governing evaluated-run protocol.

## Audited authority transition

| Authority | Exact subject | Disposition |
|---|---|---|
| Historical Stage A / Stage B reference | protocol blob `83abefb13e6a91e6b67a1c94937ca1bcce567aad` | Preserve bytes as old research/provenance only; no new evaluated run against it |
| [PR #64](https://github.com/kaicreator-mm/app8/pull/64) | exact HEAD `61e6da619a3ff50e5ffe0bed8509273b67b3ea40`, tree `21ac87e56bddcfebff7e528ef4a5bf4f1a97c795`; squash merge `859cd3253962078ef15f9e0ae43c1090deee1674` | Merged source↔execution identity amendment |
| [Issue #65](https://github.com/kaicreator-mm/app8/issues/65#issuecomment-6123948872) | Fresh Web Review, P0/P1/P2 all 0, exactly five docs changed | PASS for amendment review only, **not** evaluated SE11 execution |
| `docs/product/v0.1-successor/l1/SE11_PROTOCOL.md` | current blob `1204c717eb590071a7b7f7e1cd3018b825ef1617` | **Current evaluation protocol**; T03 must pin this before corpus construction |
| `research/e11/stage-c/stage_c.py` | blob `50c9569746d5a6b9bdabfee6b9369cc1da3e3ae5` | Existing scorer emits `protocol_blob=1204c717eb590071a7b7f7e1cd3018b825ef1617`; scorer lineage consistent with current protocol |

## Permitted reuse and required gates

1. Historical Stage A identities (FFmpeg, pandas, MinIO, LibreOffice candidate) can be **rechecked**, not declared current without byte-level host verification. Source/Execution relationships and currentness cannot be inferred from historic filenames.
2. Before creation/freeze of **80 hidden claims**, independently approve a final `se11-execution-target-manifest-v1` with exact target artifacts, applicable source→execution relations, provenance and eligible evidence references; LibreOffice's Knowledge Source and official release diverge.
3. Freeze the old 20-claim/asset truth composition, current SE11 protocol thresholds and secret hidden verdict/decisive fixtures with preplanned isolation from tested LLM-B. An owner waiver of human review for L1→L2 scheduling does **not** mechanically prove semantic truth.
4. Only after frozen private data and approval may the Stage B commitment validator and Stage C planner/scorer be executed. Frozen plan must not receive hidden labels; private material must stay outside GitHub.
5. If private Gold/truth or independent applicability is missing, terminal = BLOCKED or NOT_RUN, not SE11 PASS. The v0.3 signed CPython JSON pilot is a narrower software demonstration, not an 80-claim aggregate.

This overlay **resolves which SE11 protocol bytes govern T03**. It does **not** bless historical host bytes, mutate either earlier manifest/README, bypass protocol's 80-claim denominator, establish an independent truth-curator, or authorize a production Release.

```text
PROTOCOL_LINEAGE_STATUS=RESOLVED_WITH_MERGED_PR64_AND_ISSUE65_PASS
CURRENT_SE11_PROTOCOL_BLOB=1204c717eb590071a7b7f7e1cd3018b825ef1617
SE11_CURRENT_TARGET_MANIFEST=NOT_FROZEN
SE11_PRIVATE_HIDDEN_TRUTH=NOT_CONFIRMED
SE11_EVALUATED_EXECUTION=NOT_RUN
SE11_EMPIRICAL_PASS=NOT_CLAIMED
PRODUCT_RELEASE_QUALIFIED=NO
```
