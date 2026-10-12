# SE11 Stage B — Hidden Truth Commitment Tooling

Status: TOOLING_CANDIDATE_FOR_REVIEW
Owning issue: #55
Parent execution issue: #43
Protocol blob: 83abefb13e6a91e6b67a1c94937ca1bcce567aad
Stage-A evidence merge: 0279968580d50e51843b09aa2b6e266b9967ff93
Identity-model amendment: PR #64 (must receive independent PASS+merge before this tooling is used for corpus freeze)

## Purpose

Provide mechanical validation and a public SHA-256 commitment for the sealed 80-claim SE11 hidden-truth corpus without exposing claim text, truth class, expected behavior or decisive fixtures to the future LLM-B planner.

This tooling does not create the corpus.

## Isolation rule

The curator/private context that sees `truth_class`, claim text, expected behavior and decisive fixtures must never become the tested LLM-B planning context.

The private truth file must be outside **every Git worktree** until the reviewed protocol explicitly permits reveal. The commitment tool rejects Git-backed private input. Claim IDs are opaque UUIDv4-shaped identifiers (`H_<32 lowercase hex>`) cryptographically derived as HMAC-SHA256 over a private per-corpus 256-bit secret and non-semantic claim nonce. The private secret/nonce mapping never enters the public commitment; this mechanically prevents sequential/asset/truth-class allocation from leaking through public IDs.

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
- per-asset frozen Source→Execution mapping with exact relation and independently PASS-reviewed applicability evidence SHA-256;
- per-claim structured target-applicability object with relation, evidence kind, exact evidence SHA-256 and independent PASS status (especially for DIVERGED release branches);
- replay/reset requirements.

Before corpus construction, an independently reviewed **Execution Target manifest** must freeze each asset's exact real target version/build/package, checksum or immutable digest, acquisition provenance, platform/runtime, and Source -> Execution mapping class. The commitment CLI requires the manifest as a separate input, recomputes its SHA-256 from exact bytes, requires schema `se11-execution-target-manifest-v1`, and rejects any hidden-corpus mapping that differs from the supplied manifest.

The validator rejects missing/unknown/extra fields, wrong types, IDs that are not HMAC-bound to the private secret/nonce, duplicate IDs/nonces, unresolved Source→Execution mappings, placeholder/non-SHA applicability evidence, relation mismatches, non-PASS applicability reviews, use of exact-source evidence for a DIVERGED/ancestor/descendant mapping, or incorrect class balance. Cryptographic structure still does not prove semantic truth: the independent reviewer must inspect the sealed evidence against the final Execution Target manifest.

The public commitment contains only:
- raw private-file SHA-256 and byte count;
- Execution Target manifest SHA-256;
- total count;
- per-asset count;
- aggregate class counts already fixed by protocol;
- sorted opaque IDs;
- Stage-A merge identity;
- isolation flags.

It intentionally emits no per-ID truth class or semantic content.

## LibreOffice boundary

The tooling requires 20 LibreOffice records because the protocol freezes 20 per asset. After the identity amendment is reviewed, LibreOffice may bind to a frozen **official LibreOffice release binary/package** with durable checksum/provenance and an explicit Source -> Execution mapping. An exact source build is required only if a claim is explicitly source-only/unreleased or no suitable official artifact exists.

The historical Stage-A `BLOCKED_ENVIRONMENT` finding applies to the attempted exact-commit source build; it must not be misrepresented as proof that an official release Execution Target is blocked.

## Workflow

```bash
python research/e11/stage-b/commit_hidden.py /secure/path/se11-hidden.json \
  --execution-target-manifest /reviewed/path/se11-execution-target-manifest.json \
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

## ID generation and blind isolation

Before authoring claims, the independent curator generates one cryptographically random 256-bit `id_secret_hex` and keeps it only inside the sealed private corpus. For every claim, choose a unique non-semantic `id_nonce`; `commit_hidden.py` derives the public ID with HMAC-SHA256(secret, nonce), truncates to 128 bits, and sets RFC4122 UUIDv4 version/variant bits. The validator recomputes every ID and rejects arbitrary/sequential UUID-shaped values.

The public commitment emits only a SHA-256 of the private ID secret, never the secret or nonce mapping. Claim order should still be independently shuffled. This mechanism establishes opaque ID derivation, but not curator/planner separation or semantic truth; those remain independent-review requirements.
