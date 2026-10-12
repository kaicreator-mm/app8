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

## 3. Human / external eligibility and minimum sample

**Only genuine consenting human target users external to the app8 study team/project count.** Artificial/model-generated personas, synthetic interviews, LLM-agent responses, researcher proxies, paid impersonators or claims written by an app8 team member on behalf of a participant are categorically ineligible.

Minimum 8 independently eligible human participants:

- >=3 from each of two distinct target segments;
- <=2 from the same employer/project;
- no app8 PRD author, protocol author, developer/maintainer, study interviewer or member of the evaluation team;
- no participant whose role is solely to grade/promote the idea rather than use software in actual work.

Before recruitment, freeze eligibility questionnaire and audit method. Capture pseudonymous unique participant ID, independently verifiable role/organization or professional project affiliation (kept private/redacted publicly), real user workflow/activity evidence, consent timestamp, interview modality and interviewer identity. Prevent duplicate enrolment by private deduplication controls.

Participants must supply their own non-hypothetical workflow examples; researcher suggestions are not valid eligibility proof. An unverified person or unverifiable workflow remains INELIGIBLE and cannot enter the numerator/denominator of valid participants; all exclusions and reasons must be counted in recruitment flow.

No personal credentials, private email, proprietary artifacts or recordings may be posted publicly without explicit consent.

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

## 8. Independent scoring / adjudication discipline

Before interviews freeze:

- eligibility rules and proof schema;
- neutral interview script;
- POSITIVE criteria and thresholds;
- double-scoring and dispute procedure.

Every **valid** participant record must receive two independent scorers, neither of whom conducted that interview or authored its transcript. Scorers independently mark CURRENT_RECURRING_PAIN and CONCRETE_PILOT_COMMITMENT with evidence excerpts/references, then assign POSITIVE only when both are present.

Any disagreement goes to a third independent adjudicator whose tie-breaking decision and reasons are durable. If independent double-scoring cannot be arranged, participant remains UNSCORED and aggregate verdict is BLOCKED; there is no discretionary "where practical" exception for the primary gate.

A commitment is counted only when backed by a concrete asset/task/environment or verified >=2-hour engineering/maintainer review allocation, not by a hypothetical intent or a polite verbal endorsement.

Publish pseudonymous score matrix, exclusions, inter-rater agreement and negative evidence; protect private eligibility proofs in an access-controlled store with durable opaque refs.

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
