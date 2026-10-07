# app8

Working project for **Executable Capability Evidence**.

## Current stage

```text
PRODUCT_DIRECTION = CONDITIONAL_GO
PRD = v0.1-r5 (draft for context-fresh successor adversarial review)
PRODUCT_FREEZE = NO
L2_READY = NO
```

The current thesis is deliberately narrow:

> executable evidence should add value beyond a typed interface **after the same deterministic enforcement runtime already exists**.

The security path requires enforced guarantees plus evidence that the enforcer works for the bound Provider/invocation class. Upstream observation alone is never treated as arbitrary-input safety.

## Development standard

This repository is pinned through `.dev-standard/VERSION` to:

```text
kaicreator-mm/ai-development-standard
version 4.9.0
revision 7929012f36a2202dcc2edc7a414b8163adc7afbd
```

Do not implicitly follow the latest standard `main`.

## Durable product documents

- `docs/product/prd-v0.1-r5.md` — current PRD candidate
- `docs/reviews/prd-v0.1-r4-review.md` — predecessor successor-review FAIL terminal
- `docs/reviews/prd-v0.1-r4-disposition.md` — author response mapping into r5
- `docs/reviews/prd-v0.1-r3-review.md` — restored r3 review evidence
- `docs/reviews/prd-v0.1-r3-disposition.md` — r3 author-response mapping

GitHub durable state is the project source of truth.

No L2 or production implementation is authorized until Product Freeze under the pinned standard.
