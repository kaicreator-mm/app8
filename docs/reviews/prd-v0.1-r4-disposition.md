# PRD v0.1-r4 findings disposition

Status: AUTHOR_RESPONSE_RECORDED  
Successor acceptance: PENDING r5 context-fresh review  
Source: `docs/reviews/prd-v0.1-r4-review.md`  
Response target: `docs/product/prd-v0.1-r5.md`

This document records the author-side response. It does not declare any finding independently closed.

## P0

| Finding | r5 response |
|---|---|
| P0-1 Evidence value and enforcement semantics conflict | r5 §§1–2 explicitly choose the strict ENFORCED security model; §24 runs C and D under the same enforcing runtime; §1 splits Evidence value into pre-execution refutation, enforcer-fit and functional reliability; §18 makes prevalence L1 problem evidence rather than C-vs-D effect size |

## P1

| Finding | r5 response |
|---|---|
| P1-1 r3 review evidence broken / disposition missing | Full r3 review restored at `docs/reviews/prd-v0.1-r3-review.md`; `docs/reviews/prd-v0.1-r3-disposition.md` added |
| P1-2 prevalence kill/pass math and calibration | r5 §§17–18 add planted-positive calibration; n>=80 initial; PASS/FAIL/BLOCKED rules; false-safe only; per-claim/per-tool reporting; one expansion to n=160 |
| P1-3 REFUTED dominance bypass/permanent poisoning | r5 §11 removes time ordering, adds deterministic overlap, lineage counterexample ratchet, retirement and pending external refutation replay |
| P1-4 non-atomic TOCTOU / parser differential | r5 §§9,13 use content-addressed immutable input/artifact/adapter, input/dependency digests, forced guard interpretation and bounded DecisionRecord claim |
| P1-5 environment template vs instance ambiguity | r5 §8 splits EnvironmentTemplate from InstanceBindings |
| P1-6 missing threat model | r5 §15 defines adversaries, mechanisms and explicit MVP out-of-scope trust-root/insider cases |
| P1-7 Gate closure / non-standard statuses / preregistration | r5 §§34–36 require GitHub preregistration, prevent negative-result erasure, define independent reviewer and map all Gate outcomes to ADS standard states |
| P1-8 lifecycle deadlock | r5 §§16–22 move L1 calibration/prevalence/adoption/review before Freeze and T1–T6 Technical MVP gates after Freeze → L2 → implementation |

## P2

| Finding | r5 response |
|---|---|
| P2-1 short interactive performance budget missing | r5 §30 includes hashing/copy-in/guard/admission/setup overhead and <=1s task budget |
| P2-2 heterogeneous replay could be pinned away | r5 §27 requires different realized members inside the same declared compatibility class |
| P2-3 prevalence reweighting/budget could be infeasible | r5 §18 caps L1 study expansion; r5 §24 does not use prevalence-mixed case composition as the conditional effect gate |
| P2-4 C/D shell bypass undefined | r5 §24 removes raw Provider/shell bypass from C/D measured path and counts bypass attempts |
| P2-5 untrusted REFUTED ignored | r5 §11 creates `UNKNOWN: REFUTATION_PENDING_REPLAY` until first-party replay/disposition |
| P2-6 standard not pinned | `.dev-standard/VERSION` pins ADS 4.9.0 at exact SHA `7929012f36a2202dcc2edc7a414b8163adc7afbd` |
| P2-7 Admission cases teach-to-test | r5 §23 requires at least half of frozen T1 cases from an Independent Reviewer |

## P3

| Finding | r5 response |
|---|---|
| I3 undefined / decision naming inconsistent | r5 removes undefined I3 and consistently uses DecisionRecord for the bound execution decision object |

## Review rule

All dispositions above remain AUTHOR_RESPONSE until independently reviewed against exact r5 SHA/blob.
