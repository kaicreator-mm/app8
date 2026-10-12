# SE16 Pre-Recruitment Instrument — Target-User Pilot Pull

Status: CANDIDATE_FOR_FRESH_REVIEW
Execution: PRE_RECRUITMENT_ONLY
Owning issue: #51
Protocol: docs/product/v0.1-successor/l1/SE16_PROTOCOL.md
Protocol blob: 75d2282c35769c02274ef13878947727d879c658

## 1. Purpose

Freeze the eligibility, interview, consent, evidence, scoring, adjudication, and privacy instruments before any SE16 participant is recruited or interviewed.

This file does **not** contain participant evidence and does not authorize a PASS claim.

## 2. Eligibility questionnaire

A candidate is eligible only when all required answers are independently auditable.

Required fields:

1. Pseudonymous participant ID.
2. Real-human confirmation and consent to participate.
3. Current role and target segment:
   - Agent/runtime/tool-platform engineer;
   - team integrating internal/third-party software into Agents;
   - software/library/tool maintainer publishing Agent-facing interfaces;
   - developer maintaining repeated glue around CLI/API/desktop software for Agents.
4. Employer/project affiliation, stored privately when identifying.
5. Concrete non-hypothetical workflow where software is used by/for an Agent.
6. Recurrence: monthly-or-more often, or repeated adaptation inside an active project.
7. Exclusion check: not an app8 PRD/protocol author, app8 developer/maintainer, interviewer, scorer, adjudicator, or evaluation-team member.
8. Exclusion check: role is not solely to grade/promote app8.
9. Duplicate-enrolment check through a private deduplication key.
10. Evidence pointer for role/workflow verification.

Synthetic/model/persona/proxy users, researcher-written claims on behalf of a participant, and paid impersonation are ineligible.

## 3. Consent record

Before interview, record:

- pseudonymous participant ID;
- consent timestamp;
- interview modality;
- interviewer identity;
- permission level for public pseudonymous summary;
- permission status for quoting or sharing artifacts;
- private evidence pointer.

Never publish credentials, private email, proprietary artifacts, recordings, personal identifiers, or private company information without explicit permission.

## 4. Neutral interview script

Capture current workflow before describing proposed app8 features.

### A. Current work

1. What software do you currently need Agents or automated workflows to use?
2. Describe one concrete recent workflow from start to finish.
3. How often does this workflow recur?
4. What interface do you use today: API/SDK, CLI, MCP/tool, desktop UI, custom scripts, other?
5. What fails or costs time today?
6. What glue code, prompts, wrappers, or maintenance do you repeatedly recreate?
7. How do version changes/currentness affect the workflow?

### B. Existing alternatives

8. Does an existing CLI/MCP/Skill/tool registry already solve the job sufficiently?
9. What remains unsolved?
10. Would direct native interfaces be preferable to an intermediate capability layer? Why?
11. What security/legal/maintenance constraints would prevent use?

### C. Concept probe

Only after Sections A/B are complete, describe the neutral concept:

> A system analyzes software interfaces and documentation, tests capability hypotheses against real software, and exports evidence-backed reusable capability representations for Agent-facing consumers.

Then ask:

12. Which part, if any, addresses a material problem in the workflow already described?
13. Is semantic consistency, evidence, or currentness a problem not solved by the current approach?
14. What would make this unnecessary overhead?

### D. Pilot commitment

15. Would you contribute a real software asset?
16. Would you contribute representative tasks?
17. Could you provide a runnable environment or access path?
18. Would you allocate at least 2 hours of engineering/maintainer review?
19. What exact asset/task/environment/time commitment can be recorded now?

Generic interest or hypothetical willingness is not a pilot commitment.

## 5. Evidence record schema

For each valid participant, preserve:

- participant ID;
- segment;
- recurrence evidence ref;
- concrete-workflow evidence ref;
- current-alternative evidence ref;
- semantic/evidence/currentness pain evidence ref;
- negative/counter-evidence refs;
- concrete pilot commitment type and evidence ref;
- eligibility reviewer identity;
- interviewer identity;
- scorer A / scorer B / adjudicator identities;
- privacy classification for every evidence item.

Public artifacts use only pseudonymous summaries and opaque private evidence refs where needed.

## 6. Primary scoring rubric

Each valid participant is independently scored by two scorers who did not conduct the interview and did not author the transcript.

Each scorer assigns:

### CURRENT_RECURRING_PAIN

PASS only if evidence shows:
- a concrete current workflow; and
- recurrence at least monthly, or repeated capability adaptation in an active project.

Otherwise FAIL.

### CONCRETE_PILOT_COMMITMENT

PASS only if evidence shows at least one non-trivial commitment:
- real software asset;
- representative task set;
- runnable environment/access;
- >=2 hours engineering/maintainer review;
- independently justified equivalent contribution.

“Interesting”, “would use”, signup, or hypothetical intent = FAIL.

### POSITIVE

POSITIVE only when both CURRENT_RECURRING_PAIN=PASS and CONCRETE_PILOT_COMMITMENT=PASS.

Disagreement between scorer A and B must go to a third independent adjudicator. No majority-by-discussion before the two initial scores are committed.

If independent double scoring cannot be completed, participant status = UNSCORED and aggregate verdict = BLOCKED.

## 7. Aggregate frozen gate

PASS requires all:

- >=8 valid participants;
- >=4 POSITIVE;
- POSITIVE / valid participants >=0.50;
- positives span >=2 target segments;
- >=3 positives provide a concrete software asset/task set suitable for later pilot;
- >=2 positives explicitly identify semantic consistency/evidence/currentness as a material problem not already solved by current CLI/MCP/Skill workflow.

Recruitment failure to reach 8 valid participants = BLOCKED, not PASS.

## 8. Recruitment balance

- recruit from >=2 target segments;
- target >=3 valid participants from each of two segments;
- <=2 valid participants from the same employer/project;
- retain all exclusions and reasons in recruitment flow;
- do not replace negative participants with favorable participants after interviews begin to improve the positive rate.

## 9. Pre-recruitment freeze checklist

Before first participant contact:

- [ ] this instrument is independently reviewed and merged;
- [ ] eligibility questionnaire frozen;
- [ ] consent fields frozen;
- [ ] interview script frozen;
- [ ] proof/evidence schema frozen;
- [ ] double-scoring/adjudication procedure frozen;
- [ ] aggregate thresholds frozen;
- [ ] private evidence storage location/access policy frozen;
- [ ] participant-ID and deduplication method frozen;
- [ ] no participant outcomes visible.

## 10. Stage status

```text
SE16_INSTRUMENT = CANDIDATE_FOR_FRESH_REVIEW
PARTICIPANTS_RECRUITED = 0
INTERVIEWS_RUN = 0
OUTCOMES_VISIBLE = NO
SE16_GATE_PASS = NO
PRODUCT_FREEZE = NO
L2_READY = NO
```

## 11. What Was NOT Proven

This pre-recruitment instrument proves no user demand, market size, willingness to pay, PMF, technical feasibility, Agent utility, Product Freeze, or L2 readiness.
