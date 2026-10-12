# SE10 Stage B — Human Gold Freeze Tooling

Status: TOOLING_CANDIDATE_FOR_REVIEW
Owning issue: #58
Parent execution issue: #42
Protocol blob: 08f9244a04275c780f778d50f638e332aa5807a2
Source-pack blob: 4b3c9b62b1899653524f19a286924f942605210a

## Purpose

Reduce mechanical error in the independent-human SE10 gold freeze without allowing an LLM to author semantic gold.

The private gold file must be in a sealed access-controlled store outside any **Git-discoverable** worktree. The tool uses both ancestor `.git` detection and `git rev-parse` worktree discovery, while the independent reviewer must separately audit the private-store declaration because no local tool can prove absence from every arbitrary external Git index. IDs are opaque `G0001`–style identifiers (never semantic labels), and every anchor must match the frozen `source_anchor_allowlist.json` path/blob pair. For LibreOffice, source paths are disambiguated by a `LibreOffice/core:` or `LibreOffice/help:` prefix.

The private gold file stays outside Git. This directory contains only:
- the gold JSON schema;
- the exact 76-entry frozen source-anchor allowlist;
- a validator / SHA-256 commitment generator;
- a gitignore guard for private material.

## Human-only boundary

The semantic values of `canonical_identity`, `purpose`, variants, constraints, negative boundaries, failure semantics, binding-equivalence groups, explicit duplicate/over-splitting disposition, ambiguity decisions and source-anchor selection must be authored/reviewed by independent humans using only the frozen 76-file source pack.

ChatGPT/LLMs must not fill those semantic gold fields.

## Private file workflow

1. Create the sealed private gold file outside the repository.
2. Validate it against `gold.schema.json`.
3. Run:
   ```bash
   python research/e10/stage-b/commit_gold.py /secure/path/se10-gold.json \
     --out /tmp/se10-public-commitment.json
   ```
4. Review the generated public commitment.
5. Commit only the public commitment/hash after independent review. Never commit the semantic gold file before prediction is irreversibly frozen and the protocol permits reveal.

The tool refuses:
- wrong source-pack blob;
- any runtime allowlist bytes that do not equal reviewed Git blob `5be0ed7674fcdfd7361a57fd4f29a6f9655c1df1`;
- source anchors outside that exact frozen 76-path/blob allowlist;
- semantic or duplicate reference IDs;
- private gold in a Git-discoverable repository/worktree;
- source/output pathname or existing hardlink/inode aliases;
- unknown/extra fields and incorrect field types;
- `model_generated_gold != false`;
- `predictor_gold_visibility != false`;
- unknown assets;
- duplicate IDs;
- missing required semantic fields, including explicit duplicate/over-splitting disposition;
- contradictory/missing frozen human-author/reviewer identity classes, isolation declaration, adjudication hashes or private-store review metadata;
- empty source-anchor sets;
- fewer than 12 references for any asset.

## Public commitment intentionally excludes

- canonical identities;
- purposes;
- source paths/blobs;
- variants;
- constraints;
- negative boundaries;
- failure semantics;
- binding-equivalence groups;
- truth/adjudication notes.

Only opaque IDs, counts, ambiguity count, source-pack/allowlist identity, raw-file SHA-256, and non-semantic independently auditable human-author/reviewer/isolation/adjudication/private-store metadata are emitted.

```text
SEMANTIC_GOLD_IN_REPO=NO
MODEL_GENERATED_GOLD=FORBIDDEN
PREDICTOR_GOLD_VISIBILITY=NO
SE10_PREDICTION_AUTHORIZED=NO
SE10_GATE_PASS=NO
PRODUCT_FREEZE=NO
L2_READY=NO
```
