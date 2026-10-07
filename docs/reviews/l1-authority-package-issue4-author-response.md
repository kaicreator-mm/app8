# Issue #4 Review — Author Response

Source review: `docs/reviews/l1-authority-package-review-issue4.md`

This file records author-side remediation only. It does **not** close findings. Successor review must determine whether each P1 is FIXED or remains OPEN.

## P1 responses

| Finding | Author response |
|---|---|
| P1-1 E00 independent-subset Gate unreachable at minimum | E00 successor protocol now requires >=80 independent positive and >=80 independent negative cases. It adds an arithmetic-feasibility precheck: the frozen independent subset must be able to PASS with at least two errors per class under Wilson 95% bounds. An infeasible corpus remains NOT_RUN/BLOCKED and cannot be executed into a detector FAIL. |
| P1-2 E02 criterion 4 reachability depended on CI-method choice | E02 successor protocol fixes Newcombe paired-proportions hybrid-score/Wilson 95% intervals, prohibits degenerate Wald intervals, raises hidden corpus minimums to >=160 false-safe and >=160 valid cases, and adds a preregistered arithmetic-feasibility check. At n_valid=160, criterion 4 remains reachable with at least two E-only false denials when S allows those cases. |

## P2 responses

| Finding | Author response |
|---|---|
| P2-1 UNKNOWN could inflate E02 detection | E02 criterion 1 is now explicitly evidence-level: only REFUTED counts as detection; UNKNOWN/evidence failure do not. Criterion 2 similarly requires NOT_REFUTED and treats UNKNOWN as not-success. Decision-level effects remain criteria 3/4. |
| P2-2 shared-decision S-arm absence semantics/determinism/inputs unconstrained | E02 now uses a deterministic shared procedure, freezes seed/settings if any model component exists, defines `ABSENT_BY_ARM_DESIGN` for S without invoking production fail-closed semantics, enumerates evidence-pipeline inputs, and forbids labels/derived label metadata. |
| P2-3 host read confinement / secret scope | PRD threat promise now includes filesystem reads outside granted readable scope and host-wide resource confinement. Secret minimum classes are explicitly named: tokens, passwords, private keys, session cookies, credential-store files, and secret-designated env/config values. |
| P2-4 migration/manifest accounting stale | MIGRATION_FROM_R5 now says the threat boundary is frozen in PRD §4 and hard-case adaptation moved to PRODUCT_RESEARCH_BACKLOG R-001. The successor Product Freeze manifest binds the Backlog blob. |

## P3 responses

- v0.1 reference platform is explicitly Linux x86_64.
- resource exhaustion beyond configured quotas is inside the confinement promise; SLA/availability within quota is explicitly out of scope.
- Q-L2-009 now requires successor PRD/Product Freeze if repositioning changes product authority.
- E02 failure attribution is per criterion: criteria 1–2 -> K2/PCL-002; criteria 3–4 -> K3/PCL-003.

## Currentness

E00 and E02 NOT_RUN result placeholders have been rebound to the successor protocol blobs. No E00–E03 data has been collected.

## Requested successor disposition

For each prior P1, use the pinned ADS finding semantics:

- FIXED;
- INVALIDATED_BY_EVIDENCE;
- or OPEN.

No P1 defer path exists.
