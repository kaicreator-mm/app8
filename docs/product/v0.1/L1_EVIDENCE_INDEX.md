# L1 Evidence Index — app8 v0.1

Status: DRAFT_FOR_INDEPENDENT_REVIEW  
Authority: claim-to-evidence map for `PRD.md`

## 1. Purpose

This document answers:

> What must be proven before Product Freeze, and which exact study proves each product claim?

It does not define architecture.

## 2. Claim map

| Product claim | Required evidence | Gate effect |
|---|---|---|
| PCL-001 Declaration problem is material | E00 + E01 | FAIL => K1 |
| PCL-002 Executable evidence detects false-safe/stale behavior | E00 + E02 | FAIL => K2 |
| PCL-003 Evidence adds decision value beyond typed interface + fixed enforcement | E02 | FAIL => K3 |
| PCL-004 Provider-native MVP is sufficient | PRD boundary + L2 transfer review | universal alignment not required |
| PCL-005 Adoption pull exists | E03 | FAIL => K4 |

## 3. Required studies

### E00 — Detector Calibration

Protocol: `l1/E00-detector-calibration-protocol.md`  
Result: `l1/E00-detector-calibration-result.md`

Purpose:

- verify both sensitivity and specificity of the bounded conformance detector before prevalence is measured;
- freeze detector digest/configuration that E01 must reuse.

Gate:

- PASS only if protocol criteria are met;
- otherwise FAIL/BLOCKED per pinned ADS.

### E01 — False-safe / stale declaration prevalence

Protocol: `l1/E01-prevalence-protocol.md`  
Result: `l1/E01-prevalence-result.md`

Purpose:

- estimate whether the target population contains enough materially false-safe/stale declarations for the problem to matter.

Gate effect:

- supports/refutes PCL-001 only;
- does not determine E02 conditional effect size.

### E02 — Evidence decision value

Protocol: `l1/E02-evidence-value-protocol.md`  
Result: `l1/E02-evidence-value-result.md`

Purpose:

- test whether bounded executable evidence can detect material false-safe/stale behavior with useful precision and improve admission/currentness decisions when the typed invocation surface and enforcement baseline are held fixed.

Important:

- E02 is not an Agent shell-vs-wrapper benchmark;
- it does not preload ground-truth refutation labels into the treatment evidence store;
- it measures the evidence-generation + decision pipeline itself.

### E03 — Adoption evidence

Protocol: `l1/E03-adoption-protocol.md`  
Result: `l1/E03-adoption-result.md`

Purpose:

- determine whether target users have a recurring current problem and will commit pilot resources.

## 4. Evidence strength / research discipline

Any executable L1 study must inherit the hard discipline used by the pinned ADS Research Demo standard where applicable:

- falsifiable hypothesis;
- exact code/detector SHA or digest;
- real boundary for the tested claim;
- negative evidence retained;
- explicit `What Was NOT Proven`;
- durable raw/result references;
- no promotion of prototype mechanics into production architecture.

This is an L1 product-evidence use of the discipline, not a declaration that L1 research is L2 architecture evidence.

## 5. Gate states

Only:

~~~text
PASS / FAIL / BLOCKED / NOT_RUN / NOT_APPLICABLE
~~~

are Gate states.

Business outcomes, measured rates and product decisions are fields inside results.

## 6. Review finding rule

Product Freeze cannot pass while any valid P0/P1 remains OPEN.

P0/P1 resolution follows the pinned ADS finding schema:

- FIXED; or
- INVALIDATED_BY_EVIDENCE.

P1 is not deferrable through Product Freeze.

## 7. Protocol immutability

Every protocol is preregistered as a GitHub blob before data collection.

Once collection begins:

- the protocol blob is immutable for that study;
- thresholds/metrics cannot be edited in-place;
- protocol defect => current study FAIL/BLOCKED as specified;
- successor protocol receives a new version/file;
- old negative results remain visible.

## 8. Result authority

A result document must bind:

- protocol blob;
- dataset/catalog snapshot;
- detector/artifact digest;
- execution/reviewer identity;
- raw evidence refs;
- exact analysis script or formula version;
- Gate terminal;
- What Was NOT Proven.

A result cannot silently reinterpret the protocol.

## 9. Freeze aggregation

Product Freeze requires:

~~~text
E00 = PASS
E01 = PASS
E02 = PASS
E03 = PASS
Independent Product Review = PASS
open P0 = 0
open P1 = 0
~~~

If any required result is NOT_RUN or BLOCKED:

~~~text
PRODUCT_FREEZE = NO
~~~
