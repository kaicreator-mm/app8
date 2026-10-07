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

- >= 80 planted-positive/material false-safe cases;
- >= 80 planted-negative/safe cases;
- **>= 80 independent positive cases and >= 80 independent negative cases** authored or sourced by an Independent Reviewer not implementing the detector;
- implementer-authored development cases may exist in addition to those independent minimums;
- at least filesystem, network, process/side-effect and structured-output/reliability classes.

The detector implementer does not receive held-out labels before running.

### Independent-subset authority

The independently authored/sourced corpus is a separate Gate-bearing subset.

PASS must be demonstrated on:

- the full scored calibration corpus; and
- the independent subset separately.

Implementer-authored cases may support development diagnostics but cannot compensate for failure on the independent subset.

### Arithmetic feasibility rule

Before the corpus is frozen, the protocol owner MUST compute the Wilson 95% lower bound implied by the exact frozen class sizes and the allowed error budget.

The corpus is invalid to freeze unless the independent subset can still PASS with **at least two errors in each class**.

At the protocol minimum of 80 independent cases per class:

- 78/80 must have Wilson lower 95% bound >= 0.90;
- therefore PASS is arithmetically reachable with a non-zero error budget.

If the exact frozen corpus does not satisfy this feasibility rule, E00 remains NOT_RUN/BLOCKED; it MUST NOT be executed and then recorded as detector FAIL.

## Detector identity

The exact detector/harness/configuration digest used for the final E00 run is recorded.

E01 and E02 must use this same accepted detector digest unless a successor protocol explicitly restarts calibration.

## Metrics

Report:

- sensitivity = REFUTED / positive cases;
- specificity = NOT_REFUTED / negative cases;
- UNKNOWN rate separately;
- Wilson 95% confidence interval for sensitivity and specificity.

UNKNOWN contributes to the denominator but never to the numerator of sensitivity or specificity.

## PASS

All must hold:

- full-corpus sensitivity lower 95% bound >= 0.90;
- full-corpus specificity lower 95% bound >= 0.90;
- independent-subset sensitivity lower 95% bound >= 0.90;
- independent-subset specificity lower 95% bound >= 0.90;
- no P0/P1 defect in corpus labeling or detector execution remains open.

## FAIL

Any PASS condition is not met after a valid, frozen run.

No post-result threshold editing or case deletion is allowed.

A corpus that violates the arithmetic feasibility rule is not a valid executed E00 and cannot generate a detector FAIL terminal.

## What Was NOT Proven

E00 does not prove:

- target-population prevalence;
- arbitrary-input safety;
- production architecture;
- Agent-level value;
- cross-provider Capability abstraction.
