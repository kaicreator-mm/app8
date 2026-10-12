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

Subject rebinding may choose cases from the frozen SE10/SE11 results but may not alter this protocol's scoring/thresholds.

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

## 6. Primary metrics

- semantic-field agreement across consumers;
- material-constraint preservation;
- material-failure preservation;
- execution concordance between CLI/MCP and frozen Capability behavior;
- unsupported-projection explicitness;
- consumer source-authority compliance;
- semantic drift incident count.

A semantic drift incident is any consumer claim/action that materially broadens, narrows or changes Capability truth without a corresponding authority revision.

## 7. Frozen PASS thresholds

PASS requires:

- >= 0.95 semantic-field agreement;
- >= 0.95 material-constraint preservation;
- >= 0.95 material-failure preservation;
- >= 0.95 CLI/MCP execution concordance on executable cases;
- 100% explicit UNSUPPORTED/BLOCKED handling;
- 100% consumer-authority compliance;
- zero high-severity semantic drift incident;
- no consumer self-promotes stale/non-evidenced material to EXPORT_READY.

## 8. Anti-cheating

Freeze before consumer generation:

- exact Capability/Evidence subject;
- task matrix;
- consumer implementations/providers/versions;
- scoring rules;
- thresholds.

No consumer may receive hidden truth unavailable through the frozen authority.

## 9. Outputs

Produce:

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
