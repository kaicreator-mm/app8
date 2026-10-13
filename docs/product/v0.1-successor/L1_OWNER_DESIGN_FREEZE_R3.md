# app8 L1 r3 — Product-owner scope freeze and empirical-evidence deferral

Status: OWNER_APPROVED / ARCHITECTURE_START_WITH_WAIVER  
Decision authority: Issue #92 (2026-10-13), supersedes L1 scheduling gates in #72/#80; original protocol bytes preserved.  
Successor Product: Evidence-backed Software Capability Compiler.

## Product-owner decision

The Product owner explicitly removes the mandatory independent-human author/reviewer and independent Fresh Product review from the **L1-to-L2 scheduling gate**. App8 must not remain stalled on acquiring third-party Gold curators, hidden-truth curators, or paid human reviews before any architecture work.

This is an **authority/schedule amendment**, not experimental success. It does not retroactively validate a claim, erase prior counterexamples, change any frozen study score thresholds, or turn a model-authored design example into independent human Gold.

## New stage gates

| Gate | Status | Meaning |
|---|---|---|
| PRODUCT_SCOPE_FREEZE | YES_OWNER_APPROVED | Thesis, constraints, input/output and claim boundaries are defined enough to architect |
| L1_REAL_WORLD_EVIDENCE_QUALIFIED | NO | SE10/SE11 remain empirically UNPROVEN |
| ADS_INDEPENDENT_REVIEW_CONFORMANT | NO_OWNER_WAIVER | Explicit process exception; never label independent review PASS |
| L2_ARCHITECTURE_START | YES_WITH_OWNER_WAIVER | Can write design decisions/contracts and schedule implementation work after L2 |
| FORMAL_RELEASE_QUALIFICATION | NO | Real observations, currentness and quality gates required before release claims |
| EVIDENCE_BACKED_CAPABILITY_EXPORT_READY | NO_BY_DEFAULT | A Capability becomes ready only after appropriately scoped real evidence passes |

## L1-to-L2 authority handoff

- Claim SPCL-001 UNDERSTAND useful semantic capability extraction: **DESIGN_ACCEPTED / PERFORMANCE_UNPROVEN**; former SE10 remains an executable L3/Release acceptance target.
- Claim SPCL-002 FALSIFY / REAL_EXECUTION / EVIDENCE evidence correctness: **DESIGN_ACCEPTED / PERFORMANCE_UNPROVEN**; former SE11 remains an executable L3/Release acceptance target.
- Claims SPCL-003..SPCL-007: **UNPROVEN_DEFERRED** to their existing L2/L3/Release targets.
- The inherited E00 detector calibration is historical method evidence only; does not validate the successor.
- Previously frozen human Gold/hidden-truth tooling, Stage A, source pack, dual-curator instruments and scoring tests remain reusable **reference assets**. They may be used for controlled validation later, never falsely described as completed.
- #69 Real Host Phase 2 was reported completed by operator; its redacted terminal/manifest checksum was not visible in GitHub as of this decision. Do not reinstall, invent checksums, or claim its external smoke PASS without receipt.

## Model-authored design data policy

The product owner authorizes ChatGPT to produce:
- test case descriptions, source-scoped semantic Capability hypothesis examples;
- deterministic assertion templates, valid/invalid inputs, error and side-effect contracts;
- architecture alternatives, risks, contracts, interfaces and expected behavioral outcomes **as hypotheses**.

Every such artifact must declare:

```text
DATA_ORIGIN=MODEL_AUTHORED_DESIGN_SEED
INDEPENDENT_GOLD=NO
GROUND_TRUTH=NO
REAL_EXECUTION_OBSERVED=NO
EVIDENCE_AUTHORITY=NONE
STATUS=ILLUSTRATIVE_UNVERIFIED
```

LLM-A and LLM-B may share these **illustrative** cases as development examples; they cannot use them as an undisclosed blind benchmark. A release evaluation must bind real target identities, observations, provenance, fixtures and replay; labels cannot be inferred from model prose.

## Retained hard invariants

```text
PIXEL_DERIVED_AUTOMATION=FORBIDDEN
STRUCTURED_SEMANTIC_UI=ALLOWED
LLM_SELF_CERTIFIED_EVIDENCE=FORBIDDEN
DOCUMENTATION_ONLY_EXPORT_READY=FORBIDDEN
UNOBSERVED_CLAIM_PROMOTION=FORBIDDEN
REFUTED_OR_BLOCKED_EXPORT_READY=FORBIDDEN
SOURCE_EXECUTION_MAPPING_REQUIRED=YES
VERSION_ENVIRONMENT_SCOPE_REQUIRED=YES
NEGATIVE_EVIDENCE_PRESERVED=YES
REUSE_HARVEST_FIRST=YES
LICENSE_ERASURE_BY_LLM_REWRITE=FORBIDDEN
```

## Owner-waiver risk register

1. **Circular labels:** model-generated seeds cannot measure independent semantic accuracy; SE10 remains unknown.
2. **Truth leakage:** model-authored expected outcomes cannot qualify as hidden behavioral truth; SE11 remains unknown.
3. **Environment drift:** source snapshot and installed official release may diverge. Freeze mapping and target applicability before promotion.
4. **Product-claim gap:** L2 may discover that projection, search or non-pixel coverage is infeasible. Narrow unsupported claims instead of inventing PASS.
5. **ADS deviation:** independent Product review was previously expected. This owner-directed waiver is explicit; formal standards compliance cannot be claimed.

## Architecture entry decision

```text
PRODUCT_SCOPE_FREEZE=YES_OWNER_APPROVED
SE10_EMPIRICAL_PASS=NOT_CLAIMED
SE11_EMPIRICAL_PASS=NOT_CLAIMED
SE12_TO_SE16=UNPROVEN_DEFERRED
L2_START_AUTHORIZED=YES_WITH_OWNER_WAIVER
L2_ARCHITECTURE_EVIDENCE=NOT_YET_COMPLETE
FORMAL_IMPLEMENTATION_TASK_DAG=NOT_YET_AUTHORIZED
PRODUCT_RELEASE_READY=NO
```

Immediate next: L2 Q-L2-S01/S02/S04/S05 contracts → projection/search/binding interfaces → L2 decision review (tests/consistency, no mandatory independent human) → Implementation Task DAG.
