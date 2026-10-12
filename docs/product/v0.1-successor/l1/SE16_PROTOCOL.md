# SE16 Protocol — Target-User Pilot Pull

Status: DRAFT_FOR_FRESH_REVIEW
Execution: NOT_AUTHORIZED
Parent: Issue #25
Owning task: Issue #32
Product authority: main@908cee661f3747439bb0366b158903cb9b38b413

## 1. Falsifiable question

Does at least one real target-user segment have a recurring current need to compile existing software into reusable Agent-facing Capabilities, and will real participants commit non-trivial assets/time to a pilot?

General interest is not positive evidence.

## 2. Target segments

Recruit across at least two of:

- Agent/runtime/tool-platform engineers;
- teams integrating internal/third-party software into Agents;
- software/library/tool maintainers publishing Agent-facing interfaces;
- developers maintaining repeated glue around CLI/API/desktop software for Agents.

## 3. Sample

Minimum 8 valid independent participants, with:

- at least 3 participants from each of two distinct target segments;
- no more than 2 participants from the same employer/project;
- no participant who authored the app8 PRD or this protocol;
- participant identity may be private, but an auditable pseudonymous record and eligibility evidence must exist.

Recruitment list and eligibility rules are frozen before interviews begin.

## 4. Instrument

Use the same structured interview/pilot instrument for all participants.

Required questions gather:

- concrete software they currently need Agents to use;
- current workflow and workaround;
- frequency/recurrence;
- failure/cost of current approach;
- whether CLI/MCP/Skill tooling already solves the job;
- value, if any, of evidence-backed semantic Capability authority;
- currentness/version pain;
- willingness to supply a real asset/task/environment;
- concrete engineering/maintainer time commitment.

Avoid pitching features before current workflow/pain is captured.

## 5. Positive participant definition

A participant is POSITIVE only if BOTH hold:

1. recurring current problem is evidenced by a concrete workflow occurring at least monthly or tied to an active project with repeated software-capability adaptation; and
2. participant makes a concrete pilot commitment, such as:
   - real software asset;
   - representative task set;
   - runnable environment/access;
   - >= 2 hours engineering/maintainer review;
   - equivalent non-trivial contribution.

"Interesting", "would use", mailing-list signup, or hypothetical willingness is not enough.

## 6. Negative/counter evidence

Explicitly record:

- existing tool already sufficient;
- problem too rare;
- evidence layer seen as unnecessary overhead;
- unwillingness to provide pilot asset/time;
- security/legal constraints prevent use;
- preference for direct native interfaces;
- no willingness to maintain/revalidate generated capabilities.

## 7. Frozen PASS thresholds

PASS requires:

- >= 8 valid participants;
- >= 4 POSITIVE participants;
- positives >= 50% of valid participants;
- positives span at least 2 target segments;
- >= 3 positive participants provide a concrete software asset/task set suitable for a later pilot;
- at least 2 positives explicitly identify semantic consistency/evidence/currentness as a material problem not already solved by their current CLI/MCP/Skill workflow.

If recruitment cannot reach 8 valid participants, verdict is BLOCKED, not PASS.

## 8. Scoring discipline

Before interviews:

- freeze participant eligibility;
- freeze interview instrument;
- freeze POSITIVE rule;
- freeze thresholds.

Interview notes are scored independently from the interviewer where practical. Preserve verbatim or faithful structured evidence sufficient for audit, subject to participant privacy/consent.

## 9. Outputs

Produce:

- recruitment/eligibility manifest;
- frozen instrument;
- pseudonymous interview/pilot records;
- scoring ledger;
- positive and negative evidence;
- committed pilot-asset manifest;
- aggregate metrics;
- terminal;
- What Was NOT Proven.

## 10. Privacy / consent

Do not publish secrets, proprietary software details, credentials, personal identifiers or private company information without explicit permission. Durable GitHub evidence may use redacted/pseudonymous summaries with a private evidence pointer when required.

## 11. What this study cannot prove

SE16 cannot prove market size, willingness to pay, broad product-market fit or technical feasibility. It tests recurring real pull and non-trivial pilot commitment in the frozen sample.

## 12. Protocol terminal

~~~text
SE16_PROTOCOL = READY_FOR_FRESH_REVIEW
SE16_EXECUTION = NOT_AUTHORIZED
PRODUCT_FREEZE = NO
L2_READY = NO
~~~
