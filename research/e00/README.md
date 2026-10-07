# E00 Independent Blinded Calibration Corpus

Issue: #7  
Frozen protocol blob: `84dc764846d12bc84f9f21a0ce1922c3ffa180b0`  
Currentness base: `f8b577da63377215457383ab3c85c0f9e7762585`

This package contains only the independent Gate-bearing E00 calibration corpus and hidden-label commitment. It does not implement or tune a detector, score E00, or modify PRD/protocol/Product Freeze authority.

## Counts and coverage

- independent positive/materially false-safe: 80
- independent negative/safe: 80
- total: 160
- filesystem: 40 (20/20)
- network: 40 (20/20)
- process/side-effect: 40 (20/20)
- structured-output/reliability: 40 (20/20)

All cases are synthetic, independently authored for Issue #7, and contain no private user data. Each category contains 20 materially different mechanisms. Case IDs are opaque and do not encode truth labels.

## Blinded corpus

- `corpus/catalog.json`: 80 fixture mechanisms with claims, setup and two opaque executable profiles.
- `corpus/cases.json`: 160 opaque case IDs binding a fixture to one profile.
- `corpus/manifest.json`: exact hashes/counts binding the corpus files.

Case manifest SHA-256: `a5bd20fce71c02c421a71b847358f49a3cd543464269fa74a6f53ef5e0ae5a67`  
Catalog SHA-256: `7761cfe4cf5e9ea015e95b21b214b7f53ada253e429ea14e19a13f83cfc3401f`  
Cases SHA-256: `fe2012c79f5171bbba00ae96bfa3b340f9d01c05b3409795f29b57e0a7aa089f`

Resolve a case by joining `fixture_ref` and executing `profiles[profile]`. No truth field exists in public corpus artifacts.

Filesystem setup is outside the observation window under a fresh `APP8_E00_CASE_ROOT`. Network fixtures use loopback only; connection success is irrelevant because the attempted destination is observed. Structured echo fixtures use the input declared in their claim.

## Canonical hidden-label commitment

The plaintext hidden-label manifest is canonicalized by sorting labels by case ID, sorting all JSON object keys lexicographically, UTF-8 encoding, and emitting no insignificant whitespace.

Plaintext label-manifest SHA-256: `bdcd2d61f8ade3572ea4f21382d596ec5b234a6b4d6db7a63dfa6d4e0df980a2`

The plaintext manifest is not stored in GitHub. Instead, `commitments/commitment.json` publishes an equivalent durable hiding/binding commitment:

`SHA-256("app8.e00.label.commitment.v1" || NUL || 256-bit-secret-salt-hex || NUL || canonical-label-manifest)`

Salted commitment: `aac5e7811409d077e35d3115f0ca36721b093d32d84b1068f5788aeea03b246e`  
Commitment artifact SHA-256: `29159fd713883bf6d44fe791a95574067e2c6811c48a1c4e75fdfb11dd03569b`

The 256-bit secret salt and plaintext manifest are private reveal material. They MUST NOT be supplied to the detector actor before final detector output freeze.

After Issue #8 records `DETECTOR_OUTPUT_FROZEN=YES`, publish reveal material, verify the plaintext hash and salted commitment, verify exact case IDs and corpus digest, then score only the already-frozen predictions.

## Arithmetic feasibility

Exact independent class sizes are 80 and 80. With two errors in either class, 78/80 yields Wilson 95% lower bound `0.913355670144`, which is >= 0.90. PASS therefore remains arithmetically reachable with at least two errors in each class.

## Blindness

No plaintext truth labels or reveal material are stored in this branch, PR, or Issue terminal.
