# E03 interview instrument

Protocol binding:

```text
protocol_path = docs/product/v0.1/l1/E03-adoption-protocol.md
protocol_blob = 7ceefde5973544554da485665d40a165a120ed25
issue = #13
cohort = research/e03/cohort/manifest.md
```

Use the same instrument for P01..P08. Do not add leading questions for a particular participant after seeing earlier answers.

## Opening and consent

1. Confirm that the interviewee is the frozen Pxx target and that their current role still matches the frozen stakeholder class.
2. Explain that the study is about current software/tool behavior verification, admission, and upgrade/currentness problems; it is not a sales call and general enthusiasm does not count as evidence.
3. Ask permission to take notes and to publish only a normalized, de-identified summary under Pxx. If raw notes must remain private, explain that only a cryptographic digest and reviewer attestation will be durable on GitHub.
4. Do not request credentials, private customer data, NDA material, private-company secrets, or unnecessary personal information.

## Current workflow and recurring problem

5. In your current work, what software/AI tools, agents, providers, plugins/MCP servers, or model-backed capabilities do you have to admit, approve, verify, monitor, or upgrade?
6. Describe the most recent concrete case in which you had to decide whether such a tool/capability was safe or trustworthy enough to use. What happened, and when?
7. Which part of that problem recurs today: tool admission, behavior verification, or upgrade/currentness? How often has it happened in the last 90 days?
8. What evidence do you currently rely on (tests, traces, signatures, policy checks, manual review, vendor claims, sandbox observations, evals, change logs, other)?
9. Where does the current process fail or become expensive? Ask for one concrete consequence: time, engineer/security review load, blocked deployment, rollback, incident risk, false confidence, or inability to establish currentness.
10. When the tool/provider/model version changes, how do you know whether prior evidence remains valid? Give the most recent example.

## Existing alternatives and switching threshold

11. What current tool/process is closest to solving this? What is still missing?
12. What would an executable evidence layer have to prove or expose before you would trust it in an admission/currentness decision?
13. What would make you reject such a layer even if the demo looked useful?

## Concrete pilot commitment

14. Would you commit **one concrete resource** to evaluate this hypothesis? Record only an actual commitment, not interest. Qualifying forms are:
   - a named pilot plus a scheduled evaluation window;
   - a representative Provider/tool dataset;
   - access to a representative test environment;
   - committed engineering/security review time.
15. If yes, capture exactly which qualifying resource is committed, its owner/context, and any timing or access conditions. If no, record NO without persuasion.
16. If the participant says only "interested", "keep me posted", "I would try it", "send me a demo", or equivalent, explicitly confirm that this is **not** a pilot commitment.

## Close

17. Ask whether the normalized Pxx summary accurately reflects what was said.
18. Ask permission for a follow-up solely to verify evidence or schedule a qualifying pilot resource. Do not turn follow-up permission into a positive classification.

## Frozen success classification rubric

Copied from the frozen E03 protocol:

A participant counts as positive only if **both** are present:

1. a concrete recurring current problem in:
   - tool admission;
   - behavior verification;
   - or upgrade/currentness;
2. a concrete pilot commitment.

Pilot commitment means at least one:

- named pilot and scheduled evaluation window;
- representative Provider/tool dataset;
- access to a representative test environment;
- committed engineering/security review time.

General interest, praise or hypothetical willingness does not count.

E03 PASS requires:

```text
>= 5 / 8 positive participants
```

and positives include at least two stakeholder classes.

E03 FAIL is fewer than 5/8 positives after the frozen cohort is complete. A new cohort cannot erase that result unless a successor Product Evidence version changes the target segment and receives Independent Review.

## Evidence capture / privacy procedure

For each Pxx, E03-B must durably record only the minimum normalized fields needed for audit:

```text
participant_id
stakeholder_class
interview_date
recurring_problem_present = YES|NO
recurring_problem_domain = admission|behavior_verification|upgrade_currentness|none
normalized_problem_summary
pilot_commitment_present = YES|NO
pilot_commitment_type = named_pilot_window|representative_dataset|test_environment_access|engineering_or_security_review_time|none
normalized_commitment_summary
raw_evidence_digest_sha256
raw_evidence_private = YES|NO
reviewer_attestation
```

Rules:

- Raw material containing personal identifiers, private emails, credentials, NDA content, customer secrets, or private-company information must not be committed to GitHub.
- If raw notes/recordings are private, hash the exact retained artifact with SHA-256 and publish the digest plus an independent reviewer attestation that the normalized record corresponds to real external evidence.
- Use P01..P08 in durable public evidence.
- Do not modify the frozen cohort after learning an outcome.
- Do not score the final E03 Gate in E03-B; scoring belongs to E03-C (#15).
