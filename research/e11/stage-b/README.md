# SE11 Stage B — Hidden Truth Commitment Tooling

Status: TOOLING_CANDIDATE_FOR_REVIEW
Owning issue: #55
Parent execution issue: #43
Protocol blob: 83abefb13e6a91e6b67a1c94937ca1bcce567aad
Stage-A evidence merge: 0279968580d50e51843b09aa2b6e266b9967ff93

## Purpose

Provide mechanical validation and a public SHA-256 commitment for the sealed 80-claim SE11 hidden-truth corpus without exposing claim text, truth class, expected behavior or decisive fixtures to the future LLM-B planner.

This tooling does not create the corpus.

## Isolation rule

The curator/private context that sees `truth_class`, claim text, expected behavior and decisive fixtures must never become the tested LLM-B planning context.

The private truth file stays outside Git until the reviewed protocol explicitly permits reveal.

## Required shape

Exactly 80 claims, exactly 20 per asset.

Per asset:
- 8 TRUE;
- 4 MATERIALLY_FALSE;
- 4 OVERBROAD;
- 4 NEAR_MISS.

Every private claim requires:
- opaque ID;
- asset;
- truth class;
- claim text;
- exact binding ID;
- decisive fixture reference;
- expected behavioral truth;
- provenance;
- replay/reset requirements.

The public commitment contains only:
- raw private-file SHA-256 and byte count;
- total count;
- per-asset count;
- aggregate class counts already fixed by protocol;
- sorted opaque IDs;
- Stage-A merge identity;
- isolation flags.

It intentionally emits no per-ID truth class or semantic content.

## LibreOffice boundary

The tooling requires 20 LibreOffice records because the protocol freezes 20 per asset. A curator must not populate a valid runnable binding/decisive fixture unless a reviewed exact-pinned LibreOffice runnable exists. Stage-A BLOCKED cannot be bypassed by a distro/newer binary.

## Workflow

```bash
python research/e11/stage-b/commit_hidden.py /secure/path/se11-hidden.json \
  --out /tmp/se11-public-commitment.json
```

Commit only the reviewed public commitment. Do not commit the sealed truth file.

```text
HIDDEN_TRUTH_IN_REPO=NO
TRUTH_VISIBLE_TO_LLM_B=NO
DECISIVE_FIXTURES_VISIBLE_TO_LLM_B=NO
SE11_STAGE_C_AUTHORIZED=NO
SE11_GATE_PASS=NO
PRODUCT_FREEZE=NO
L2_READY=NO
```
