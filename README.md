# app8

**app8** explores **Executable Capability Evidence**: a governance layer that turns software behavior claims into bounded, replayable evidence for admission/currentness decisions.

## Current stage

```text
PRODUCT_DIRECTION = CONDITIONAL_GO
L1_AUTHORITY = DECOMPOSED_DRAFT
PRODUCT_FREEZE = NO
L2_READY = NO
```

## Pinned development standard

```text
repository=kaicreator-mm/ai-development-standard
version=4.9.0
revision=7929012f36a2202dcc2edc7a414b8163adc7afbd
```

Do not implicitly follow the latest standard main.

## Current authority graph

```text
docs/product/v0.1/PRD.md
  -> product claims / MVP boundary / invariants / kill criteria

docs/product/v0.1/L1_EVIDENCE_INDEX.md
  -> claim-to-evidence mapping and L1 gate aggregation

docs/product/v0.1/l1/*-protocol.md
  -> immutable preregistered study protocols

docs/product/v0.1/l1/*-result.md
  -> study terminals (currently NOT_RUN)

docs/product/v0.1/L2_QUESTION_REGISTER.md
  -> architecture/security UNKNOWNs transferred only through the L1→L2 test

docs/product/v0.1/PRODUCT_FREEZE.md
  -> exact package aggregation only
```

## Historical reviews

- `docs/reviews/prd-v0.1-r4-review.md` — durable r4 successor review
- `docs/reviews/prd-v0.1-r5-review.md` — durable context-fresh r5 review
- `docs/reviews/prd-v0.1-r5-author-response.md` — author response into the decomposed package
- `docs/reviews/prd-v0.1-r3-review.md` — restored historical text; provenance NOT VERIFIED and not Freeze authority

## Important boundary

The decomposed package intentionally does **not** claim that sandbox/kernel/refutation/attestation mechanics are already solved. Those questions are explicitly registered for L2.

Before Product Freeze, app8 must still complete E00–E03 and a final independent Product Review with:

```text
open P0 = 0
open P1 = 0
```

GitHub durable state is the project source of truth.
