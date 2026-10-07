# PRD v0.1-r5 Review — Author Response into L1 Authority Decomposition

Source review: `docs/reviews/prd-v0.1-r5-review.md`  
Reviewed r5 blob: `5d8ff030ec3aa0694f01f61ee4372fd01f013433`

This is an **author response**, not a finding closure terminal. Only an Independent Reviewer may determine whether a finding is FIXED or INVALIDATED_BY_EVIDENCE.

## P0

| Finding | Author response |
|---|---|
| P0-1 T2 could not falsify the product thesis | Removed the r5 four-arm/T2 formulation from the PRD. Product claims are now explicit in `PRD.md`. L1 proof is factored into E01 prevalence and E02 conditional evidence-value. E02 holds typed interface + enforcement fixed, treatment Evidence is generated blind to ground-truth labels, has explicit sensitivity/specificity/incremental-detection/non-inferiority PASS rules, and FAIL triggers K2/K3 and blocks Freeze. No Agent-provider-selection claim remains. |

## P1

| Finding | Author response |
|---|---|
| P1-1 P1 defer contradicted pinned ADS | `PRD.md` INV-006 and `L1_EVIDENCE_INDEX.md` require open P0=0 and open P1=0. No P1 defer path exists. |
| P1-2 L1-CAL/PREV false-positive and estimator ambiguity | E00 now calibrates both sensitivity and specificity and freezes detector identity. E01 freezes primary unit as unweighted per-tool, counts false-safe only, defines conservative UNKNOWN handling, reuses exact E00 detector digest, and makes same-population FAIL durable rather than rerunnable until PASS. |
| P1-3 REFUTED ratchet underspecified | Exact refutation overlap/lineage algebra is removed from L1 product authority and registered as Q-L2-005. L1 retains only the product invariant that negative evidence is first-class and affects admission/currentness. Product Review must validate the transfer classification. |
| P1-4 environment template lacked concrete host realization | Host/kernel/enforcer capability binding is Q-L2-002; environment template/instance design is Q-L2-003. They are no longer represented as solved L1 product facts. |
| P1-5 malicious Provider threat boundary incomplete / output trust removed | Enforcement threat boundary is Q-L2-001. Output trust is restored as PRD INV-007 and Q-L2-007. The PRD does not claim the sandbox architecture is already solved. |

## P2/P3 material responses

- Admission business decisions are no longer mapped to development Gate states in the L1 PRD.
- Bounded TOCTOU/content-addressing moved to Q-L2-004.
- r3 evidence is retained as historical/non-authoritative evidence; provenance limitations are recorded separately.
- r4→r5 and r5→decomposition material deltas are recorded in `MIGRATION_FROM_R5.md`.
- replay/attestation technical PASS rules are L2/release concerns, not L1 Freeze preconditions.
- executable L1 studies inherit applicable ADS Research Demo hard disciplines via `L1_EVIDENCE_INDEX.md`.
- cold/warm performance architecture moved to Q-L2-009.
- undefined Branching-Gate vocabulary is removed from L1 Gate authority.

## Requested successor verdict

For each prior P0/P1, the Independent Reviewer should issue one of the ADS-compliant outcomes:

- FIXED;
- INVALIDATED_BY_EVIDENCE;
- or leave OPEN.

This document itself does not close findings.
