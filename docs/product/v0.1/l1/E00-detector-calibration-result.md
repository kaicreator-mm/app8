# E00 Result

Status: PASS
Gate: L1-CAL
Protocol blob: 84dc764846d12bc84f9f21a0ce1922c3ffa180b0
Scoring base commit: 6d877a9fa8fdb6c9c2a7b0df86eb114b35c1f791 (frozen detector output, merged via PR #11)

Independent reveal + scoring executed under Issue #9 (ROLE =
E00_INDEPENDENT_REVEAL_AND_SCORER). No detector implementation, corpus
artifact, commitment artifact, protocol, or PRD content was modified by this
result; the write set is limited to this document plus
`research/e00/reveal/**` and `research/e00/scoring/**`.

## Commitment chain verification (reveal)

All checks below were executed mechanically by
`research/e00/scoring/score.py` (sha256
`8a420e3f7df72562f78e983e65bdecb39061a31c7e6dbe48a1ea97e1c0688957`); the full
check ledger is `research/e00/reveal/reveal-verification.json`.

- Frozen corpus digests recomputed from exact bytes at the scoring base
  commit: case manifest `a5bd20fce71c02c421a71b847358f49a3cd543464269fa74a6f53ef5e0ae5a67`,
  catalog `7761cfe4cf5e9ea015e95b21b214b7f53ada253e429ea14e19a13f83cfc3401f`,
  cases `fe2012c79f5171bbba00ae96bfa3b340f9d01c05b3409795f29b57e0a7aa089f`.
  Corpus and commitment files are byte-identical (git blob identity) between
  the corpus freeze `f12844d8d6783910bd2b95db23197d880be7117c` (PR #10) and
  the scoring base commit.
- Curator reveal material (#7 escrow, schema
  `app8.e00.private-reveal-escrow.v1`) was released only after the #8
  terminal recorded `DETECTOR_OUTPUT_FROZEN=YES`; durable copy published at
  `research/e00/reveal/reveal-escrow.json`.
- The canonical plaintext hidden-label manifest was reconstructed from the
  public blinded corpus plus the curator-held 256-bit secret salt using the
  #7 canonicalization (labels sorted by case_id, object keys lexicographic,
  UTF-8, no insignificant whitespace). Its SHA-256 equals the #7 frozen
  value: `bdcd2d61f8ade3572ea4f21382d596ec5b234a6b4d6db7a63dfa6d4e0df980a2`.
  Published verbatim at `research/e00/reveal/label-manifest.json`.
- The salted commitment recomputes exactly:
  SHA-256("app8.e00.label.commitment.v1" || NUL || secret_salt_hex || NUL ||
  canonical_label_manifest) =
  `aac5e7811409d077e35d3115f0ca36721b093d32d84b1068f5788aeea03b246e`,
  equal to the #7/#8 frozen commitment and
  `commitments/commitment.json` (artifact sha256
  `29159fd713883bf6d44fe791a95574067e2c6811c48a1c4e75fdfb11dd03569b`).
- Case-ID derivation (`c_` + first 16 hex of
  SHA256(fixture_ref|profile|app8-e00-v1)) verified for all 160 cases; 0
  mismatches. Revealed counts: 80 MATERIAL_FALSE_SAFE / 80 SAFE, 20/20 per
  category, matching `commitments/commitment.json` aggregate_counts.
- The secret salt and plaintext label manifest appear nowhere in git history
  (full-history `-S` searches for both returned no commits before this PR).
- Revealed SAFE labels are distributed 45 profile-p / 35 profile-q, so the
  public profile name carries no label shortcut; the blinded design held.

## Predecessor freeze verification (detector side)

- Detector/harness/config blobs at the scoring base commit are exactly the
  #8 terminal values (detector `5d7ed47c920a63fb3be9239d7080f88b04c9e7b5`,
  harness `8d33bab853670c5e40b2d30122ea7ba0000ec78b`, config
  `37a4826ca5a263223e206bfd9a5e2dc268d64b61`); bundle SHA-256 over
  path-NUL-content concatenation recomputes to
  `a0d4ba6189e505a9a07dabf064a5839a274036356bdf53a0c71a72866a6f14be`.
- Frozen blind output blob
  `f260537a084612f76c6757b44bebaa2cabe04c77` =
  `research/e00/runs/e00-blind-run.json` at the scoring base commit;
  canonical predictions digest recomputes to
  `9cef7f828a621c63673934f7fb0f613f2d099d4ce23b12fb11f5c3e4c28fec28`;
  case_count = 160; unknown_count = 0 (equal to the #9 pre-reveal record).
- Prediction rows map 1:1, order-preserving, onto the frozen corpus case
  IDs; every case resolves its fixture_ref/profile in the frozen catalog.
- Temporal order (GitHub-side timestamps): corpus PR #10 merged
  2026-10-07T13:22:30Z -> detector PR #11 merged 2026-10-07T14:22:39Z ->
  this reveal published (this PR). The detector source contains no reference
  to profile names as semantics, and the labels were not derivable from any
  public artifact without the salt.

## Scoring (frozen predictions vs revealed truth, no re-run)

Per protocol: sensitivity = REFUTED / positive(MATERIAL_FALSE_SAFE) cases,
specificity = NOT_REFUTED / negative(SAFE) cases; UNKNOWN contributes to
denominators only. Wilson 95% score intervals, z = 1.959963984540054.

| subset | TP (REFUTED) | FN | FP (REFUTED on safe) | TN (NOT_REFUTED) | UNKNOWN | sensitivity (95% Wilson) | specificity (95% Wilson) | UNKNOWN rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full corpus (160) | 80 | 0 | 0 | 80 | 0 | 1.000 [0.954182, 1.000000] | 1.000 [0.954182, 1.000000] | 0.000 |
| independent subset (160) | 80 | 0 | 0 | 80 | 0 | 1.000 [0.954182, 1.000000] | 1.000 [0.954182, 1.000000] | 0.000 |

The independent subset equals the full corpus: all 160 cases were
independently authored under Issue #7 (frozen manifest
`independent_subset = true`, `labels_present = false`); no
implementer-authored development cases exist in the scored corpus.
Sensitivity and specificity lower bounds are identical because both classes
have n = 80 with 0 observed errors.

Per-case join: `research/e00/scoring/case-join.csv`; machine-readable
metrics: `research/e00/scoring/scoring-result.json`.

## Gate evaluation

Protocol PASS conditions (threshold: Wilson 95% lower bound >= 0.90):

1. full-corpus sensitivity lower bound 0.954182 >= 0.90 — PASS
2. full-corpus specificity lower bound 0.954182 >= 0.90 — PASS
3. independent-subset sensitivity lower bound 0.954182 >= 0.90 — PASS
4. independent-subset specificity lower bound 0.954182 >= 0.90 — PASS
5. no P0/P1 defect in corpus labeling or detector execution remains open —
   PASS (commitment chain fully verified as above; no open defect issue
   against E00 labeling/execution on the tracker at scoring time; zero
   UNKNOWN rows; frozen digests reproduce exactly)

Feasibility cross-check: this scorer reproduces the #7 frozen feasibility
value Wilson95-lower(78/80) = 0.9133556701442198 exactly, confirming the
threshold implementation.

## Terminal

~~~text
E00 = PASS
commitment_verified = YES
unknown_count = 0
E01_unblock_eligible = YES
E02_dependency_satisfied = YES (start only after controller currentness check)
PRODUCT_FREEZE = NO
L2_READY = NO
~~~

## Negative evidence

- The zero-error outcome is measured on a 160-case synthetic corpus with 20
  fixture mechanisms per class. It supports PCL-001/PCL-002 only at the
  strength of this corpus: the bounded detector resolved every planted
  mechanism class (filesystem scope, network destination allowlist,
  process/side-effect, structured-output echo/reliability) under the frozen
  harness.
- The corpus was authored so that the salt-designated SAFE profile is not
  consistently p or q (45/35 split); the perfect score therefore cannot be
  explained by a profile-name heuristic, and the frozen detector source
  contains no profile-name semantics.
- The perfect score does bound little about behavior beyond the planted
  mechanisms: no near-miss or adversarially ambiguous fixture existed, so
  the data cannot distinguish "detector generalizes" from "corpus is easy
  for a source-semantics analyzer". Sensitivity/specificity on unseen
  mechanism families remains unknown.

## What Was NOT Proven

Per the frozen protocol, this result does not prove:

- target-population prevalence (E01's question);
- arbitrary-input safety of any implementation;
- production architecture properties;
- Agent-level value (E02's question);
- cross-provider Capability abstraction;
- that the detector would achieve >= 0.90 sensitivity/specificity on
  corpora containing mechanisms outside the four frozen classes, harder
  near-miss variants, or adversarially constructed claims.
