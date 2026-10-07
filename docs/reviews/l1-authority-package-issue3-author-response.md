# Issue #3 Review — Author Response

Source review: `docs/reviews/l1-authority-package-review-issue3.md`

This file records author-side remediation. It does **not** close findings. Successor review must determine whether each P1 is FIXED or remains OPEN.

## P1 responses

| Finding | Author response |
|---|---|
| P1-1 product-level security promise transferred to L2 | PRD §4 now freezes the minimum threat promise: malicious/test-aware Provider violations of configured network/filesystem/process boundaries are in scope; untrusted output cannot silently become control authority; trusted-runner/kernel/sandbox compromise is explicitly out of scope; secrets default denied unless residual-risk authorized. Q-L2-001 now selects an enforcement mechanism that must satisfy this already-frozen promise and may not redefine it. |
| P1-2 PCL-003 operational-cost conjunct untested | Removed `operational cost` from PCL-003. Performance remains a post-Freeze architecture/positioning question in Q-L2-009 and is no longer part of the L1 product claim. |
| P1-3 E02 did not freeze one shared decision procedure | E02 now freezes one exact admission/decision procedure + digest before any arm output. S and E use the identical procedure; E differs only by receiving generated Provider-behavior Evidence. Arm-specific decision logic invalidates the run. |

## P2 responses

| Finding | Author response |
|---|---|
| P2-1 E02 paired-CI authority frozen too late | E02 now freezes exact paired-CI method, analysis script, decision-engine digest and thresholds before any experimental arm output is generated. |
| P2-2 E00 independent calibration subset not Gate-bearing | E00 now requires independent-subset sensitivity and specificity lower bounds >= 0.90 in addition to full-corpus thresholds. Implementer-authored cases cannot compensate for independent-subset failure. |
| P2-3 hard-case adaptation distribution misclassified as L2 | Removed Q-L2-010 and moved the question to `PRODUCT_RESEARCH_BACKLOG.md` as non-blocking future Product Evidence. |

## Result/manifest currentness

Because E00 and E02 protocols changed, their NOT_RUN result placeholders were rebound to the successor protocol blobs. Product Freeze remains NO and all L1 studies remain NOT_RUN.

## Requested successor disposition

For each prior P1, use the pinned ADS finding semantics:

- FIXED;
- INVALIDATED_BY_EVIDENCE;
- or OPEN.

No P1 defer path exists.
