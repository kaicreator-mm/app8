# PRD v0.1-r3 findings disposition

Historical document type: AUTHOR_RESPONSE (not a review-finding terminal)  
Independent successor acceptance: NOT VERIFIED by r4 review  
Source review: `docs/reviews/prd-v0.1-r3-review.md`  
Response target: `docs/product/prd-v0.1-r4.md`

This file does not retroactively claim r3 findings were independently closed. It records how r4 attempted to address each r3 finding so a successor reviewer can audit the lineage.

## P0 disposition

| Finding | Author response in r4 | Author's reading of r4 review |
|---|---|---|
| P0-1 E0 effect size could be manufactured by benchmark composition | Added E0-prevalence, four-arm design, preregistered statistics and prevalence-linked benchmark/reweighting in r4 §§14–18 | NOT VERIFIED; r4 review reopened the value model as a new P0 because enforcement and evidence were still confounded at the product-thesis level |
| P0-2 Admission was not bound to actual input/execution context | Added Provider identity, CLOSED_SCOPE, ExecutionContext, DecisionRecord and pre-exec digest re-check in r4 §§3–10 | NOT VERIFIED; r4 review found remaining TOCTOU, input-content and environment-template/instance gaps |

## P1 disposition

| Finding | Author response in r4 | Author's reading of r4 review |
|---|---|---|
| P1-1 evidence shopping | r4 §7 added trusted REFUTED dominance, suite-lineage minimum and local refutation/revocation index | NOT VERIFIED; r4 review found dominance needed scope/lineage semantics |
| P1-2 UNVERIFIED_ESCAPE authorization/metrics | r4 §12 restricted escape to policy/human authorization and counted unsafe escape executions | author response present |
| P1-3 statistical false PASS | r4 §§16–18 added prevalence-informed design, clustered analysis plan, power analysis, CI rules and one expansion | NOT VERIFIED; r4 review found gate math/status issues remained |
| P1-4 CLOSED_SCOPE omitted observable environment state | r4 §§5–6 and heterogeneous replay added clock/CPU/kernel/resource/runtime identity constraints | NOT VERIFIED; r4 review required template/instance split and threat-model clarification |
| P1-5 blind mutation evidence weak | r4 §23 required blind held-out cases, commit-reveal and historical regressions | author response present; still subject to future technical validation |
| P1-6 gate closure ambiguous | r4 §§29–32 added numbered gate taxonomy and dispositions | NOT VERIFIED; r4 review found lifecycle and standard-status conflicts |
| P1-7 third-party attestation trust | r4 §§13,25 narrowed MVP to FIRST_PARTY / consumer-replayed evidence | author response present |

## P2 disposition

| Finding | r4 response |
|---|---|
| P2-1 semantic retention could degrade fidelity | r4 §22 added frozen per-dimension fidelity requirements |
| P2-2 intermittent violations lacked repetitions | r4 §6 added `runs_per_fixture` / repetition policy |
| P2-3 output trust was only advisory | r4 §26 explicitly bounded the product claim to preserving trust labels and not upgrading UNTRUSTED_EXTERNAL |
| P2-4 verified-path production cost absent | r4 §27 introduced a reference operational budget |
| P2-5 contract/evidence category confusion | r4 §22 explicitly excluded network/side-effects from semantic output-retention dimensions |

## Closure rule

No row above is considered independently CLOSED merely because this disposition exists. Successor review controls closure.
