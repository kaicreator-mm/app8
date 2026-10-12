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

## 3A. Participant ID, deduplication and private evidence storage

These controls are frozen **before first participant contact**.

### Pseudonymous participant ID

- Generate an independent random UUIDv4.
- Public/study ID format: `P_<32 lowercase UUIDv4 hex>`.
- The ID contains no employer, role, geography, recruitment source, score, interview order or other semantic information.
- Sequential IDs and researcher-chosen semantic IDs are forbidden.

### Private duplicate-enrolment key

Duplicate detection uses a keyed digest, never a raw identifier in Git.

1. Privately collect **all verified stable identifiers already legitimately available** for recruitment/eligibility verification from this bounded type set: `EMAIL`, `PROFESSIONAL_PROFILE_URL`, `EMPLOYER_DIRECTORY_ID`, `PROJECT_ACCOUNT_ID`. Do not collect an identifier only for dedup if it is otherwise unnecessary/unlawful.
2. Canonicalize deterministically by identifier type: trim surrounding whitespace; lowercase the complete email address; for URLs lowercase scheme/host only and preserve path/query bytes; directory/account IDs are trimmed but otherwise byte-preserved. Do not infer aliases, strip plus-addressing, merge domains, or use fuzzy matching.
3. Compute one keyed digest **per available verified identifier**:
   `HMAC-SHA256(SE16_DEDUP_SECRET, "app8-se16-v1\n" + identifier_type + "\n" + canonical_identity)`.
4. The participant's private dedup identity is the **set of all such HMACs**, not a researcher-selected single identifier. If any HMAC intersects an existing participant's set, mark `POTENTIAL_DUPLICATE` and require private human linkage resolution before eligibility can become VALID.
5. `SE16_DEDUP_SECRET` is a fresh cryptographically random 256-bit study secret, stored separately from participant evidence and never committed, logged, pasted into issues, or shared with scorers.
6. Store only the typed HMAC set and linkage disposition in the private participant index. Public GitHub receives neither raw stable identifiers nor HMACs.
7. Linkage resolution is bounded: `CONFIRMED_SAME_HUMAN`, `CONFIRMED_DISTINCT_HUMANS`, or `UNRESOLVED`. `CONFIRMED_SAME_HUMAN` may contribute at most one valid participant; `UNRESOLVED` is ineligible for the primary cohort. No fuzzy similarity score can auto-merge or auto-clear a candidate.
8. If a new identifier is learned later, it must be HMAC-indexed and checked against the full private index before final primary-cohort freeze. A duplicate discovered after interview remains a recruitment-flow exclusion and cannot be replaced using outcome knowledge.

The HMAC is only a duplicate-enrolment control. It is not identity proof, consent proof, or evidence of a valid workflow.

### Private evidence store

All identifying/proprietary participant evidence is stored outside every Git worktree in an access-controlled private store. Before recruitment, freeze a **private store descriptor** containing:

- storage-system/host identity;
- absolute private root or opaque storage object identity;
- encryption-at-rest status;
- OS/service access-control identities permitted to read/write;
- backup/retention policy;
- evidence-file naming policy;
- dedup-secret storage location class (must be separate from the evidence root);
- deletion/withdrawal procedure;
- descriptor version and timestamp.

The descriptor itself may contain sensitive paths/accounts, so public GitHub records only its SHA-256 commitment plus the non-sensitive policy class. The independent pre-recruitment reviewer verifies the private descriptor without publishing its sensitive contents.

Required policy:

- minimum access: interviewer/eligibility custodian only as required; scorers receive pseudonymous evidence extracts/opaque refs and no unnecessary identity data;
- no credentials or authentication tokens in participant evidence;
- raw recordings only when explicitly consented, otherwise do not create them;
- public evidence must be redacted/pseudonymous and use opaque private refs;
- withdrawal before aggregate freeze removes future study use of private evidence where legally/operationally possible and records only a non-identifying withdrawal tombstone needed to prevent accidental re-enrolment;
- no deletion may be used after outcome visibility to improve the positive fraction; withdrawals/exclusions remain counted in recruitment-flow accounting according to the frozen protocol.

Before first contact, publicly commit:

```text
PARTICIPANT_ID_METHOD=UUIDV4_OPAQUE
DEDUP_METHOD=HMAC_SHA256_PRIVATE_SECRET
PRIVATE_STORE_DESCRIPTOR_SHA256=<64 lowercase hex>
DEDUP_SECRET_PUBLIC=NO
RAW_IDENTITY_PUBLIC=NO
PRIVATE_STORE_POLICY_REVIEWED=YES
```

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

## 8A. Primary cohort and stopping rule

The primary SE16 gate uses a **pre-registered fixed cohort**, not sequential recruitment until the desired outcome appears.

Before first outreach:

0. Freeze the **candidate queue and outcome-blind recruitment firewall**:
   - create a bounded candidate pool from the frozen outreach channels without using any SE16 interview/pilot outcome;
   - assign each candidate an opaque recruitment ID and freeze a cryptographically random permutation/queue plus channel-allocation quotas;
   - freeze outreach cadence/batch size and the rule for moving to the next queued candidate after non-response/ineligibility;
   - interviewer/scorer outcome data is not visible to the recruitment coordinator or eligibility queue operator until the eighth valid primary participant is irrevocably frozen;
   - recruitment/eligibility staff may see only data necessary for consent, eligibility and dedup, never POSITIVE/negative scoring, semantic-pain answers, pilot-commitment strength or aggregate positivity;
   - any emergency deviation from the queue for legal/safety/contact-invalidity reasons must be recorded before the substitute is contacted and may not use interview outcome information.
1. Select and freeze exactly two primary target segments from the four protocol-defined segments.
2. Freeze a target of **8 valid primary participants**:
   - at least 3 valid participants from each selected primary segment;
   - the remaining 2 may come from either selected segment or another protocol-defined segment;
   - never more than 2 valid participants from the same employer/project.
3. Freeze outreach sources/channels, per-channel allocation, candidate queue/randomization seed commitment, outreach cadence/batch rule and eligibility screening procedure before outcomes.
4. The **first 8 valid eligible participants encountered by the frozen queue/segment/employer procedure** form the primary cohort. Interview outcome cannot change queue order, channel allocation, contact cadence, eligibility disposition, or whether an otherwise valid candidate enters the cohort. Positive/negative interview results may not affect whether an otherwise valid participant enters that cohort.
5. Recruitment ends for the primary gate when the eighth valid participant is frozen. The PASS/FAIL calculation uses exactly those 8 valid participants.
6. If the sampling plan cannot produce 8 valid participants within the pre-registered recruitment window/outreach budget, primary verdict = `BLOCKED_RECRUITMENT`; do not extend the window/budget after observing positivity.
7. Additional participants after the primary cohort are explicitly `SECONDARY_EXPLORATORY`. They may inform product learning but **cannot rescue or replace** the primary SE16 gate result.

Before first outreach publicly commit the non-sensitive sampling plan:

```text
PRIMARY_VALID_COHORT_SIZE=8
PRIMARY_SEGMENTS=<two frozen protocol segment IDs>
PRIMARY_SEGMENT_MINIMUM=3_EACH
MAX_VALID_PER_EMPLOYER_PROJECT=2
RECRUITMENT_WINDOW_OR_BUDGET=<frozen value>
OUTREACH_CHANNEL_SET=<frozen non-sensitive identifiers>
OUTREACH_CHANNEL_ALLOCATION=<frozen quotas>
CANDIDATE_QUEUE_COMMITMENT_SHA256=<64 lowercase hex>
OUTREACH_CADENCE_BATCH_RULE=<frozen value>
RECRUITMENT_OUTCOME_FIREWALL=ENFORCED_UNTIL_PRIMARY_COHORT_FREEZE
OPTIONAL_STOPPING=FORBIDDEN
POST_PRIMARY_PARTICIPANTS=SECONDARY_EXPLORATORY_ONLY
```

If privacy-sensitive outreach details are required, store them in the private pre-recruitment descriptor and publicly commit its SHA-256.

## 9. Pre-recruitment freeze checklist

Before first participant contact:

- [ ] this instrument is independently reviewed and merged;
- [ ] eligibility questionnaire frozen;
- [ ] consent fields frozen;
- [ ] interview script frozen;
- [ ] proof/evidence schema frozen;
- [ ] double-scoring/adjudication procedure frozen;
- [ ] aggregate thresholds frozen;
- [ ] primary cohort size, two primary segments, outreach channel set and recruitment window/budget frozen;
- [ ] optional stopping prohibited; post-primary participants secondary-only;
- [ ] private evidence-store descriptor created outside Git, independently reviewed and its SHA-256 publicly committed;
- [ ] UUIDv4 participant-ID method frozen;
- [ ] HMAC-SHA256 typed multi-identifier deduplication method + separate secret-storage class frozen;
- [ ] candidate queue/randomization commitment, channel allocation and outreach cadence/batch rule frozen;
- [ ] recruitment/eligibility outcome firewall frozen until primary cohort lock;
- [ ] no raw identity or dedup HMAC appears in public GitHub;
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
