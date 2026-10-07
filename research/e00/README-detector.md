# E00 detector / blind runner

Frozen against `f12844d8d6783910bd2b95db23197d880be7117c` and protocol blob `84dc764846d12bc84f9f21a0ce1922c3ffa180b0`.

This detector is a deterministic, bounded source/contract analyzer for the four classes present in the #7 blinded calibration corpus. It consumes only the public `manifest.json`, `catalog.json`, and `cases.json` artifacts. The case `profile` value is used only to select the public source snippet according to the manifest join rule; the detector does not assign semantic meaning to `p` or `q`.

## Frozen identity

- detector/harness/config bundle SHA-256: `a0d4ba6189e505a9a07dabf064a5839a274036356bdf53a0c71a72866a6f14be`
- canonical prediction output SHA-256: `9cef7f828a621c63673934f7fb0f613f2d099d4ce23b12fb11f5c3e4c28fec28`
- case count: 160
- UNKNOWN count: 0
- deterministic seed: none
- final blind evaluator runtime: OpenAI Code Mode V8 isolate, pure ECMAScript
- replay harness: Node.js >=20 standard library only

Bundle digest rule is SHA-256 over the exact UTF-8 concatenation:

`path + NUL + content + NUL + path + NUL + content + NUL + path + NUL + content`

for `detector.cjs`, `run.cjs`, then `config.json`, using the repository-relative paths in that order.

Canonical output digest rule is recorded in `research/e00/runs/e00-blind-run.json`.

## Replay

```bash
APP8_E00_BUNDLE_SHA256=a0d4ba6189e505a9a07dabf064a5839a274036356bdf53a0c71a72866a6f14be node research/e00/detector/run.cjs
```

The harness re-hashes the three public corpus files using the #7 canonicalization rule (single trailing newline excluded) and refuses to run on drift.

## Blindness

No plaintext truth labels, reveal secret, scoring material, or contents of `research/e00/commitments/**` were accessed while implementing or executing this run. No truth-dependent metric is computed here. The frozen output must not be modified before #9 scoring.
