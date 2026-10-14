# app8 v0.4 — Product Owner Decision: adversarial verification with minimal human review

**Decision ID:** V04-PO-MLA-001  
**Status:** OWNER_APPROVED_DESIGN; SUCCESSOR_PROTOCOL_NOT_YET_QUALIFIED  
**Decision date:** 2026-10-14  
**Applies to:** #147 core qualification; #149 semantic extraction; #150 falsification; #151 terminal.  
**Authority:** the owner's explicit selection of (1) multi-LLM adversarial review, (2) deterministic tool verification, (3) minimal human final adjudication.

## Accepted product constraints

1. **Model-separated adversarial generation.** The evaluated app8 model P may only see the frozen source and its public product prompt. Independent R (reference proposer) and X (challenge proposer) generate candidate semantic tasks, counterclaims and falsification plans in isolation; J is an **optional** bounded third independent model for unresolved contradictions. Model family, provider, prompt/version, source and run identities must be pinned. Model agreement alone is not an oracle.
2. **Deterministic evidence wins.** Git blob/source identity, exact execution target, source→target applicability, syntax/invariants, and actual sandboxed observation are checked by tools. No model, including J, may sign its own unsupported plan as observed fact, and no model confidence can promote unsupported Capability.
3. **Human final authority with minimal workload.** Require human cards only for product-critical unresolved conflict and a small precommitted stratified audit of otherwise eligible decisions. Start with **one audited case per asset (four cards)**, expand when disagreement warrants, **up to 12 total cards** as a default budget. No mandatory full-source manual reading or manual authoring of all semantic labels; no automatic approval if mandatory exceptional reviews exceed budget. Human may **CONFIRM, REJECT or DEFER** with an exact evidence bundle.
4. **Low ROI excluded.** No unlimited agent debate, mandatory separate reviewer per ordinary claim, newly built test infrastructure or repeated old Docker probing. Prefer reuse of existing Stage-A artifacts, Stage-B public commitment/schema validation, Stage-C calculations, and #157/#158 public workpacks. Escalate only when a decision could change support/readiness or reveal systematic error.
5. **Auditable isolation.** R/X candidate reference is `LLM_PROPOSED`, not independent-human Gold. V's observation is distinguishable from source assertion; hidden oracle/decisive fixtures remain invisible to P or evaluated LLM-B before predictions. Preserve source pack (76 files), target candidate provenance, git SHA, reproducible seeds/denominators, negative results, and public hash commitments.

## Protocol and release precedence

- This is the **approved Product-level design decision**, authorizing implementation of a *new* experiment contract, `V04-MLA-1`. The [earlier RFC](MULTI_LLM_ADVERSARIAL_EVALUATION_RFC.md) is retained as historical proposal/context, not the normative study definition.
- Original [SE10 protocol](../v0.1-successor/l1/SE10_PROTOCOL.md) at Git blob `08f9244a04275c780f778d50f638e332aa5807a2` and [SE11 amended protocol](../v0.1-successor/l1/SE11_PROTOCOL.md) at Git blob `1204c717eb590071a7b7f7e1cd3018b825ef1617` stay byte-identical. Old `SE10_PASS`/`SE11_PASS` and their independent-human accuracy estimates are **NOT MET/NOT_RUN**. Do not run their `commit_gold.py` with model-generated references marked `model_generated_gold=false`, or self-attest independent curation.
- New experimental study outcome is **`V04_MLA_PROVISIONAL`** until successor protocol, scorer, human sampling rule, fixed cohort/metrics/thresholds, reviewer calibration and evidence authority are frozen **before** evaluated outputs. Independently review those contracts; no retroactive thresholds/denominator changes or new model labels passed off as old Gold.
- App8 v0.4 is *core product qualification*, not broad GA. SE12–SE16 still UNPROVEN. Formal Product Release remains **NO** until separately adopted product release criteria actually pass.
- Historical [blocked terminal](../../release/v0.4/CORE_EMPIRICAL_TERMINAL.md) is retained. It is not silently superseded by Product approval or by new synthetic unit tests.

## Smallest implementation sequence

```text
Product decision (this file) -> V04-MLA-1 protocol + schema/metric freeze
-> bounded independent model roles & deterministic validator/reducer
-> 4-software pre-evaluation trial (4 assets; 6 candidate cases/asset initial)
-> 4–12 human decisions on fixed sample / unresolved impactful disputes
-> full frozen evaluation if eligibility/evidence allows
-> #149/#150 true terminal -> #151 honest Release decision
```

**First trial is not a replacement for the old 48 human Gold or 80 hidden-truth score.** Maintain exact source and execution identities; R/X automatically draft **candidate** cases. Where executable truth is absent, `UNVERIFIED` counts in coverage and **cannot** become `SUPPORTED`. Scope, reviewer-pinned sample seed and acceptance metrics must be fixed before trial outputs are visible.

```text
V04_PO_MLA_DECISION=APPROVED
MULTI_LLM_ADVERSARIAL_REVIEW=YES
DETERMINISTIC_EVIDENCE_VERIFICATION=REQUIRED
HUMAN_FINAL_EXCEPTION_REVIEW=MINIMIZED_MAX_12_CARDS_DEFAULT
LLM_AGREEMENT_AS_GROUND_TRUTH=NO
OLD_SE10_SE11_EXACT_BLOBS_PRESERVED=YES
NEW_STUDY_PROTOCOL=REQUIRED_BEFORE_EVALUATED_RUN
MODEL_GENERATED_HUMAN_GOLD_ATTESTATION=FORBIDDEN
FORMAL_PRODUCT_RELEASE_QUALIFIED=NO
```
