# E00 — Detector Calibration Protocol

Status: PREREGISTRATION_DRAFT  
Gate: L1-CAL  
Supports: PCL-001, PCL-002

## Hypothesis

The bounded conformance detector can distinguish materially false-safe behavior claims from behavior that actually satisfies the tested contract with sufficiently high sensitivity and specificity.

## Frozen unit

Primary unit: one provider-claim case.

The detector outputs only:

- REFUTED;
- NOT_REFUTED;
- UNKNOWN.

UNKNOWN is not treated as a successful detection.

## Calibration corpus

Before execution, freeze:

- >= 60 planted-positive/material false-safe cases;
- >= 60 planted-negative/safe cases;
- >= 50% of each class authored or sourced by an Independent Reviewer not implementing the detector;
- at least filesystem, network, process/side-effect and structured-output/reliability classes.

The detector implementer does not receive held-out labels before running.

### Independent-subset authority

The independently authored/sourced subset is a separate Gate-bearing subset, not merely part of the aggregate.

PASS must be demonstrated on:
- the full calibration corpus; and
- the independent subset separately.

Implementer-authored cases may support development diagnostics but cannot compensate for failure on the independent subset.

## Detector identity

The exact detector/harness/configuration digest used for the final E00 run is recorded.

E01 and E02 must use this same accepted detector digest unless a successor protocol explicitly restarts calibration.

## Metrics

Report:

- sensitivity = detected REFUTED / positive cases;
- specificity = NOT_REFUTED / negative cases;
- UNKNOWN rate separately;
- Wilson 95% confidence interval for sensitivity and specificity.

## PASS

All must hold:

- full-corpus sensitivity lower 95% bound >= 0.90;
- full-corpus specificity lower 95% bound >= 0.90;
- independent-subset sensitivity lower 95% bound >= 0.90;
- independent-subset specificity lower 95% bound >= 0.90;
- no P0/P1 defect in corpus labeling or detector execution remains open.

## FAIL

Any PASS condition is not met after the frozen run.

No post-result threshold editing or case deletion is allowed.

## What Was NOT Proven

E00 does not prove:

- target-population prevalence;
- arbitrary-input safety;
- production architecture;
- Agent-level value;
- cross-provider Capability abstraction.
