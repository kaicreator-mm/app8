# E01 — False-safe / Stale Declaration Prevalence Protocol

Status: PREREGISTRATION_DRAFT  
Gate: L1-PREV  
Supports: PCL-001  
Depends on: E00 PASS

## Hypothesis

At least 5% of tools in the frozen target population contain at least one materially false-safe or stale declared behavior claim that can affect admission/governance.

## Target population

The preregistration must freeze:

- public catalog/registry snapshot(s);
- eligibility rules;
- target-user relevance rule;
- sampling frame;
- exclusions and reasons.

Primary sampling is uniform over eligible tools in the frozen target population.

Usage/popularity-weighted estimates are secondary reports only unless a successor protocol preregisters a different primary population.

## Primary unit

Primary Gate unit: **per tool, unweighted**.

A tool is positive if at least one eligible declared behavior claim is independently adjudicated as materially false-safe/stale and detected/refuted with the E00-approved detector.

Secondary reports:

- per claim;
- category;
- popularity/usage weighted where valid data exists.

## Directionality

Only false-safe claims count toward the primary positive rate.

False-unsafe / overly conservative claims are reported separately.

## Materiality adjudication

Materiality is adjudicated by an Independent Reviewer blinded to the desired PASS/FAIL direction.

The taxonomy is frozen before claim outcomes are inspected.

## Detector identity

The E00-approved detector digest is mandatory.

A detector/configuration change invalidates this protocol's run and requires successor E00/E01 preregistration.

## Sample plan

Initial sample:

~~~text
n = 80 eligible tools
~~~

One and only one preregistered expansion is allowed:

~~~text
maximum n = 160 eligible tools
~~~

No optional stopping between those points.

## UNKNOWN handling

Let:

- C = confirmed positive tools;
- U = UNKNOWN/unverifiable tools;
- N = total sampled tools.

For PASS, use the conservative lower-prevalence view:

~~~text
p_pass = C / N
~~~

UNKNOWN counts as non-positive.

For FAIL, use the conservative anti-kill view:

~~~text
p_fail = (C + U) / N
~~~

UNKNOWN counts as potentially positive.

Compute Wilson 95% intervals.

## Gate rule

Threshold T = 5%.

- PASS: lower 95% bound of p_pass >= 5%.
- FAIL: upper 95% bound of p_fail < 5%.
- otherwise BLOCKED after n=80.

If BLOCKED at n=80, execute the single preregistered expansion to n=160.

At n=160:

- PASS if PASS criterion holds;
- FAIL if FAIL criterion holds;
- otherwise FAIL with reason `PROBLEM_PREVALENCE_NOT_DEMONSTRATED_WITHIN_BUDGET`.

## Successor studies

A FAIL under this frozen target-population definition remains FAIL.

A later study may become relevant only if an Independent Reviewer accepts evidence that the target population materially changed. That is a new product-evidence version, not a rerun that erases E01.

All versions remain durable and are reported together.

## What Was NOT Proven

E01 does not prove:

- the detector is valuable to users;
- evidence improves decisions;
- production security;
- architecture viability;
- market willingness to pay.
