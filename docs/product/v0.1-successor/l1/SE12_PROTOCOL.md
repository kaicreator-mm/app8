# SE12 Protocol — One Capability Authority, Many Consumers

Status: DRAFT_FOR_FRESH_REVIEW
Execution: HOLD_FOR_SE10_SE11_AND_FROZEN_CAPABILITY_SUBJECT
Parent: Issue #25
Owning task: Issue #28
Product authority: main@908cee661f3747439bb0366b158903cb9b38b413

## 1. Falsifiable question

Can one frozen Evidence-backed Capability authority drive CLI, MCP, Skill, Agent documentation and searchable metadata while preserving the same semantics, constraints, variants, failures and real-software behavior?

## 2. Deferred exact execution subject

Protocol logic is frozen now, but execution is forbidden until SE10 and SE11 yield a frozen Capability/Evidence subject.

Before execution, an independently reviewed subject manifest must bind:

- 12 Evidence-backed Capabilities;
- at least 3 software classes/assets;
- at least 3 Capabilities with meaningful variants;
- at least 3 with material negative/unsupported boundaries;
- exact Capability/Evidence blobs;
- exact bindings and environments.

### 2.1 Deterministic exact-12 selection (replaces discretionary strata)

**Frozen eligibility:** A candidate must have a stable ID, an EVIDENCED behavioral verdict, exact Evidence source refs, non-stale version/binding scope, and an executable binding. The eligible-pool manifest is frozen before any projection is generated.

**Selection algorithm:** Commit the UTF-8 seed `app8-SE12-v0.1-selection` and eligible-pool blob. Partition eligible candidates by source asset and its distinct software class. Retain only assets with at least 4 eligible candidates. Select the first 3 **distinct software classes**, ascending by canonical class ID; within each class select the first asset ascending by canonical repository/asset ID. If fewer than 3 such classes exist, verdict = BLOCKED (no fallback).

Within each selected asset, rank its candidates ascending by SHA-256(seed + "|" + canonical Capability ID); break exact hash collisions by ascending canonical Capability ID. Take the first 4 from each asset: exactly 12. No discretionary quotas, swaps, oversampling, post-hoc substitutions, or replacement after looking at projector outputs.

Before running a projector verify that the selected 12 contain >=3 material variants, >=3 material negative/unsupported boundaries and representation of all 3 distinct classes. If not, verdict = BLOCKED (do not cherry-pick a better set). Freeze the selected 12 IDs and their exact blobs.

Any evidence-stale/invalid subject discovered afterward is reported as a study limitation and scored according to the predeclared denominator; no favorable replacement or subject reallocation is allowed.

## 3. Required consumers

For every selected Capability, generate or materialize, where supported:

1. Agent-friendly CLI;
2. MCP tool/server surface;
3. Skill package/instructions;
4. Agent documentation;
5. searchable Capability Metadata.

A consumer may be explicitly UNSUPPORTED/BLOCKED. Silent substitution is forbidden.

## 4. Authority rule

Each consumer receives the same frozen Capability/Evidence authority.

A consumer may add representation-specific syntax, but may not independently read original target-software docs/source to mutate semantic truth.

The execution harness must record all consumer inputs so this can be audited.

## 5. Test matrix

For each Capability:

- semantic name/purpose consistency;
- input/output correspondence;
- variant preservation;
- constraint/precondition preservation;
- negative/unsupported-boundary preservation;
- failure/recovery semantics;
- binding identity;
- provenance/currentness exposure where representation supports it;
- CLI real execution;
- MCP real execution;
- Skill/docs instruction consistency;
- search metadata readiness/constraint consistency.

At least two positive and one negative/boundary task per Capability are required.

## 6. Primary metrics and denominator discipline

Primary subject denominator = **all 12 selected Capabilities**; representation-level field consistency has a denominator of 12 × required fields per required consumer, with unsupported/missing fields recorded as missing rather than silently excluded.

Track per consumer:

- CLI: real executable binding, assessed over **12**;
- MCP: real executable binding, assessed over **12**;
- Skill: assessable instructions, assessed over **12**;
- Agent Docs: assessable documentation, assessed over **12**;
- Search Metadata: assessable entry, assessed over **12**.

A generated consumer that fails compilation, execution, or contract validation is **FAIL**, not UNSUPPORTED or BLOCKED. UNSUPPORTED is allowed only when the frozen Capability authority itself documents a hard representation limitation with matching Evidence; BLOCKED is only a documented external environmental restriction, independently adjudicated before generator outcome visibility. Both count as non-covered in the primary denominator.

Also score semantic-field agreement, material-constraint/failure preservation, CLI/MCP execution concordance, explicit unsupported handling, source-authority compliance and semantic drift.

## 7. Frozen PASS thresholds

PASS requires all of:

- CLI executable coverage **>=9/12** and MCP executable coverage **>=9/12**; at least **9/12 common subjects** executable via both CLI and MCP;
- Skill assessable coverage **12/12**, Agent Docs **12/12**, Search Metadata **12/12**;
- >=0.95 semantic-field agreement over all required/assessable consumer fields, missing/unsupported representation recorded as miss where material;
- >=0.95 material-constraint preservation and material-failure preservation;
- >=0.95 CLI/MCP execution concordance across at least the 9 common executable subjects, with >=2 positive and >=1 negative task per subject;
- 100% explicit UNSUPPORTED/BLOCKED handling, including proof of representation/environment eligibility;
- 100% consumer-authority compliance;
- zero high-severity semantic drift incident;
- no stale/non-evidenced capability promoted to EXPORT_READY.

If 9 shared executable cases cannot be assessed, this study **FAILS** the multi-consumer feasibility claim; it cannot PASS on the smaller subset. No target-level cherry-picking is permitted.

## 8. Anti-cheating

Freeze before consumer generation:

- exact Capability/Evidence subject;
- deterministic selection seed and selected IDs;
- task matrix;
- consumer implementations/providers/versions;
- scoring rules;
- thresholds.

No consumer may receive hidden truth unavailable through the frozen authority.

## 9. Outputs

Produce:

- eligible-pool and subject-selection manifest;
- subject manifest;
- all consumer artifacts;
- authority-input ledger;
- real CLI/MCP execution logs;
- cross-consumer semantic matrix;
- drift findings;
- terminal;
- What Was NOT Proven.

## 10. What this study cannot prove

SE12 does not prove Agent utility, search advantage, broad non-pixel coverage or user demand. It proves only whether one factual Capability authority can constrain several representations/consumers consistently on the frozen subject.

## 11. Protocol terminal

~~~text
SE12_PROTOCOL = READY_FOR_FRESH_REVIEW
SE12_EXECUTION = HOLD_FOR_SE10_SE11_AND_FROZEN_CAPABILITY_SUBJECT
PRODUCT_FREEZE = NO
L2_READY = NO
~~~
