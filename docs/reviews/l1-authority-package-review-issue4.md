<!-- ai-dev:event:v2 -->
```yaml
schema: ai-dev/event-v2
event: REVIEW_RESULT
actor_role: reviewer
operator_kind: claude-code
operator_id: "claude-code:app8-l1-authority-review-issue4-01"
session_ref: "app8-issue4-successor-review-20261007-e7ddbf5a"
transport_actor: "github:kaicreator-mm"
task: "#4"
sha: "e03ad120596296d79d3b1a44dfaa7bd37ba0c2f9"
standard_revision: "7929012f36a2202dcc2edc7a414b8163adc7afbd"
review_policy: required
status: FAIL
next_state: changes-requested
```

# Remediated v0.1 L1 authority package: context-fresh successor review (Issue #4)

## Terminal

```text
L1_AUTHORITY_PACKAGE_SUCCESSOR_REVIEW = FAIL
REVIEWED_HEAD = e03ad120596296d79d3b1a44dfaa7bd37ba0c2f9
STANDARD = kaicreator-mm/ai-development-standard@7929012f36a2202dcc2edc7a414b8163adc7afbd (4.9.0)
BASELINE_RECHECK_BEFORE_PUBLISH = MATCH
ISSUE3_P1 = 3/3 FIXED
ISSUE3_P2 = 3/3 remediated (P2-1 and P2-2 remediations leave/introduce the reachability defects below)
P0 = 0
P1 = 2
P2 = 4
P3 = 4
PRODUCT_FREEZE = NO
L2_READY = NO
E00 = NOT_RUN
E01 = NOT_RUN
E02 = NOT_RUN
E03 = NOT_RUN
NEXT = revise E00/E02 protocols (+ successor result placeholders + manifest rebind) -> context-fresh successor review
```

This is **not** a Product Freeze review. FAIL means E00–E03 must not be executed as the authoritative pre-Freeze sequence under this exact package.

**Independence.** Context-fresh and self-attested. This reviewer did not author the Issue #3 remediation. It did not take part in app8 r1–r5 or Issue #1–#3 authoring or review. It uses a new `operator_kind/operator_id/session_ref` (claude-code, distinct from the Issue #3 chatgpt-web reviewer). It rebuilt every fact from GitHub durable state plus the pinned ADS, and used no local working-copy or chat-history content. READ_ONLY: the only writes are the ROLE_CLAIMED comment and this REVIEW_RESULT on Issue #4.

## 0. Exact-baseline / currentness check

Immediately before publishing:

| Item | Expected (Issue #4) | Observed | |
|---|---|---|---|
| `main` HEAD | `e03ad120…f9` | `e03ad120…f9` | MATCH |
| PRD | `e851a8d6…` | `e851a8d6…` | MATCH |
| L1 Evidence Index | `cc00ffab…` | `cc00ffab…` | MATCH |
| L2 Question Register | `5b3b79f0…` | `5b3b79f0…` | MATCH |
| PRODUCT_FREEZE | `ba47b96d…` | `ba47b96d…` | MATCH |
| E00 protocol | `1e79c61a…` | `1e79c61a…` | MATCH |
| E02 protocol | `e474a817…` | `e474a817…` | MATCH |
| Product Research Backlog | `5b2da6b6…` | `5b2da6b6…` | MATCH |
| `.dev-standard/VERSION` | ADS 4.9.0 @ `7929012f…` | same | MATCH |

Blob contents were fetched through the GitHub API and re-hashed locally with `git hash-object`. The remediation delta was read as `compare/a879ffc0…e03ad120` (8 commits).

## 1. Issue #3 P1 closure

| Issue #3 finding | Disposition | Basis |
|---|---|---|
| P1-1: product-level threat promise transferred to L2 | **FIXED** | PRD §4 "Product-level threat promise" now freezes four protected behaviors: undeclared egress, writes outside the granted scope, process escape from the configured containment, and silent output→control escalation. It requires fail-closed behavior, and explicitly puts runner/kernel/sandbox/trust-root compromise, kernel or sandbox escape vulnerabilities, and time-bomb/data-triggered semantic misbehavior OUT. Secrets are default-deny with explicit residual-risk authorization, and output is untrusted by default. Q-L2-001 now asks only which Linux composition *satisfies* the frozen promise, with "L2 MUST NOT weaken, broaden or redefine". The "sandbox-escape/kernel-exploit assumption" decision was removed from L2. (Residual specificity gaps: P2-3; stale migration row: P2-4.) |
| P1-2: PCL-003 operational-cost conjunct without L1 evidence | **FIXED** | "or operational cost" has been removed from PCL-003. Every remaining PCL-003 conjunct maps to E02: decision improvement → criteria 1/3; "without unacceptable false denial" → criteria 2/4. No PCL claims a latency or cost property, so a negative Q-L2-009 answer cannot falsify a PCL. |
| P1-3: E02 decision-procedure isolation | **FIXED** | E02 now has a §"Shared decision procedure". One exact procedure and digest are frozen before any arm output and used by both arms. S gets static declarations plus the fixed baseline; E gets the *same* inputs plus generated evidence. Any arm-specific logic, rule, model or threshold change invalidates the run. The arms therefore differ only in Provider-behavior evidence. (Residual operational ambiguities that do not reopen this P1: P2-1, P2-2.) |

No Issue #3 P0/P1 remains OPEN, and none was deferred.

## 2. Issue #3 P2 remediation

| Issue #3 P2 | Status | Note |
|---|---|---|
| P2-1: E02 CI/analysis authority frozen too late | **Remediated (timing)** | The paired-CI method, analysis script, decision-engine digest and thresholds are now frozen "before any experimental arm output is generated". However, **which** method is chosen still decides whether criterion 4 can be met at all at the protocol minimum. See new **P1-2**. |
| P2-2: E00 independent subset not Gate-bearing | **Remediated, but introduces new P1-1** | The independent subset now has its own ≥0.90/≥0.90 lower-bound Gate. Combined with the unchanged "≥50% of ≥60" minimum, PASS is arithmetically impossible at the minimum compliant corpus. |
| P2-3: hard-case adaptation misclassified as L2 | **Remediated** | Q-L2-010 was removed and moved to `PRODUCT_RESEARCH_BACKLOG.md` R-001 as non-blocking. The classification is correct: it does not touch PCL-001..005, and the backlog says that a future scalable-adaptation claim must promote it to Product Evidence. The accounting chain was not updated: see P2-4. |

## 3. New blocking findings

The Issue #4 target "PASS/FAIL/K2/K3 remain reachable" was checked numerically for every Gate. Wilson 95% bounds use z = 1.959964.

| Gate | Protocol minimum | PASS reachable at minimum? |
|---|---|---|
| E00 full corpus (≥0.90 / ≥0.90) | n = 60 per class | yes; ≤1 error per class |
| **E00 independent subset (≥0.90 / ≥0.90)** | **n = 30 per class (50% of 60)** | **NO.** At 30/30 the Wilson lower bound is 0.8865. A perfect score needs n ≥ 35. |
| E01 (lower bound ≥5%) | n = 80 → 160 | yes; PASS needs C ≥ 8 at n = 80, or C ≥ 14 at n = 160. FAIL is reachable (forced at n = 160). |
| E02 criterion 1 (sens ≥0.80) | n = 60 | yes; ≤5 misses |
| E02 criterion 2 (spec ≥0.90) | n = 60 | yes; ≤1 false denial |
| E02 criterion 3 (E−S ≥ +0.20) | n = 60 | yes |
| **E02 criterion 4 (E−S valid-allow ≥ −0.05)** | **n = 60** | **Depends on the unfrozen CI method.** With S allowing all valid cases and E making **zero** false denials, the Newcombe hybrid-score paired lower bound is **−0.060**, so the criterion is unmeetable. Under Wald the lower bound is 0.000 (zero-width interval at zero discordance), so it passes. |
| E03 (≥5/8) | 8 | yes |

### P1-1: E00 independent-subset Gate is unreachable at the protocol's own minimum corpus

**Location.** `l1/E00-detector-calibration-protocol.md` (blob `1e79c61a`), §Calibration corpus ("≥ 60 … ≥ 60 … ≥ 50% of each class … independent") together with §PASS bullets 3–4.

**Expected.** A preregistered Gate whose FAIL is consequential must have a PASS that is reachable under every configuration the preregistration permits. Otherwise FAIL measures the design, not the detector. Here E00 FAIL feeds PCL-001 (→ K1) and PCL-002 (→ K2) through `L1_EVIDENCE_INDEX.md` §2.

**Actual.** A corpus at the stated minimum is fully protocol-compliant: 60 + 60 cases with exactly 30 independent per class. On that corpus, independent-subset sensitivity and specificity cannot reach a Wilson lower bound ≥ 0.90 even with zero errors (30/30 → 0.8865). E00 would deterministically FAIL. Because "No post-result threshold editing or case deletion" applies and old negative results stay durable, the outcome would be a K1/K2 kill record produced by arithmetic. The defect was introduced by the Issue #3 P2-2 remediation: the new subset Gate was not reconciled with the old 50% minimum. Even at 40 independent cases per class the error budget is zero, which makes E00 extremely brittle to a single mislabel.

**Required change (successor E00 protocol + rebound NOT_RUN result + manifest).** Choose one of these approaches:

1. Set an explicit independent-subset minimum per class that leaves a stated error budget, for example ≥ 60 independent per class (allows 1 error) or ≥ 80 (allows 2).
2. Add a preregistered feasibility rule: before freezing, show that the frozen subset sizes admit PASS with at least k errors, and treat a corpus that fails this check as an invalid freeze rather than an E00 FAIL.

### P1-2: E02 criterion 4 reachability is decided by an unconstrained CI-method choice

**Location.** `l1/E02-evidence-value-protocol.md` (blob `e474a817`), §Hidden evaluation corpus ("≥ 60 valid"), §Primary PASS criteria 4, and the closing sentence of that section ("exact paired-CI method … frozen … before any experimental arm output").

**Expected.** The Gate must be reachable and non-arbitrary under the preregistered design. The analysis authority must not be able to decide PASS-reachability through a method choice. This is the residual of Issue #3 P2-1: freezing *when* the method is chosen does not constrain *what* is chosen.

**Actual.** Consider the realistic best case at the protocol minimum: S allows all 60 valid cases (they are valid declarations) and E has zero false denials, so there is zero discordance.
- With a standard score-type paired interval (Newcombe hybrid score), the lower bound is −0.060 < −0.05. Criterion 4 cannot pass, so E02 FAILs and K2/K3 trigger with perfect treatment behavior.
- With Wald, the interval collapses to zero width at zero discordance, so the criterion passes. Wald is a degenerate method in exactly this boundary region.

As a result, at n_valid = 60 the method choice made at script-freeze time determines whether E02 can PASS. The protocol does not exclude either outcome: a predetermined kill, or a pass that relies on a degenerate interval. Under Newcombe, criterion 4 becomes reachable with 0 false denials at n_valid ≈ 80 and with 2 false denials at n_valid ≈ 160.

**Required change (successor E02 protocol + rebound NOT_RUN result + manifest).** Name the paired-CI method family in the protocol itself and exclude methods that degenerate at zero discordance, such as Wald. Then either:
- set n_valid, and n_false-safe for criterion 3, to a preregistered minimum that admits PASS with a stated false-denial budget under that method; or
- restate criterion 4 so it is reachable at the chosen n.

Add a pre-freeze feasibility check like the one for E00.

## 4. Non-blocking findings

### P2-1: E02 criterion 1 does not say whether UNKNOWN → fail-closed denial counts as "detection"

E00 states "UNKNOWN is not treated as a successful detection". E02 reports an UNKNOWN rate, but criterion 1 ("treatment sensitivity") does not say whether it is measured on decisions (deny) or on evidence (REFUTED). INV-004 makes missing security evidence fail closed. A procedure that denies on evidence-generation failure or UNKNOWN therefore scores "detections" on false-safe cases that merely crash or time out under enforcement. That inflates criterion 1, and through it the PCL-002 support that E02 claims. This is not P1 for three reasons: the operationalization must be frozen before arm outputs; specificity and non-inferiority (criteria 2 and 4) penalize UNKNOWN-denials on valid cases; and E00 independently gates PCL-002 at evidence level with UNKNOWN ≠ success. **Fix:** define criterion 1 explicitly. Recommended: decision-level for PCL-003, plus an evidence-level REFUTED sensitivity with UNKNOWN ≠ detection, reported and gated for PCL-002 consistently with E00.

### P2-2: The shared decision procedure's S-arm absence semantics, determinism and inputs are unconstrained

(a) The procedure must handle "no Provider-behavior evidence" in S. If it applies INV-004 fail-closed there, S denies everything and the baseline is degenerate. The protocol should require that S apply declaration-based admission, not missing-evidence denial. (b) "model change" implies the procedure may be stochastic. The protocol should freeze seed and sampling settings, or require determinism. (c) The protocol should enumerate the per-case inputs to the evidence pipeline: the S inputs plus the Provider artifact. It should also state that any per-case fixture or spec is authored by someone blind to curator labels, so that labels cannot reach the pipeline in derived form. The absolute criteria 1–2 bound E independently of S, so none of these opens a false-PASS path. They are auditability hardening.

### P2-3: Threat promise does not define secret scope or host-filesystem read confinement

The promise covers egress and writes but is silent on **reads** outside the granted scope. "Secrets/credentials are denied by default" implies some read boundary, but leaves L2 free to define "secret" narrowly, for example environment variables only while host `~/.ssh` stays readable. Exfiltration through the Provider-output channel stays possible even with egress denied. This is not a P1: the default-deny plus residual-risk-authorization language is product-level and binds L2, and no PCL depends on it. **Fix:** state in PRD §4 whether host-filesystem read confinement to the granted readable scope is in the promise, and give the minimum class of credential material covered by default-deny.

### P2-4: Migration and manifest accounting chain not updated after the Issue #3 remediation

`MIGRATION_FROM_R5.md` (blob `cc037d88`, unchanged since Issue #3) still says:
- §2, r5 §15 row: "exact threat/enforcer boundary Q-L2-001/Q-L2-007". This now contradicts PRD §4 and Q-L2-001 ("L2 MUST NOT … redefine"). PRD and Q-L2-001 are the higher authority, so P1-1 stays FIXED, but the row is stale.
- §3: "Hard-case adaptation probe → Q-L2-010". Q-L2-010 no longer exists; the item lives in Backlog R-001.

`PRODUCT_FREEZE.md` also does not bind the `PRODUCT_RESEARCH_BACKLOG.md` blob, which is the only record of where R-001 went. PRD §11 says "Any contradiction among package members makes Freeze FAIL", so this must be fixed before Freeze. It does not make E00–E03 ambiguous. **Fix:** update both migration rows and bind the Backlog blob, or record why it is out of the package.

### P3 (informational)

- **P3-1:** Q-L2-001 assumes Linux, but the PRD does not freeze OS/platform scope. State it in the PRD, or state that the platform is an L2 choice that does not narrow target users.
- **P3-2:** Resource exhaustion and availability (CPU, memory, fork bombs) is listed neither IN nor OUT in §4. Silence reads as "not promised"; saying so explicitly would remove the ambiguity.
- **P3-3:** Q-L2-009 says a repositioning to CI/governance is "subject to Product Review". PRD §12 requires a successor PRD if a product claim changes. Cross-reference §12 so a repositioning that changes target users cannot happen through review alone.
- **P3-4:** E02 FAIL triggers both K2 and K3 even when only criterion 3 or 4 fails and criteria 1–2 pass. This is conservative and never causes a false PASS, but the result record should report per-criterion attribution. Criterion 3 is close to redundant with criterion 1, because a static-declaration baseline structurally admits almost all false-safe cases (S ≈ 0 except metadata-detectable staleness). It is not tautological, so this is informational only.

## 5. Threat-boundary / transfer integrity (Issue §3)

- **Minimum product-level threat promise frozen:** yes (PRD §4); residual gaps are P2-3 and P3-2.
- **Q-L2-001 selects an implementation rather than redefining the promise:** yes. Its "L2 must decide" list is now mechanism, privileges, telemetry and conformance demonstration; the threat-assumption decision was removed.
- **Would any remaining L2_REQUIRED question invalidate PCL-001..005 if answered negatively?** No:
  - Q-L2-002, -003, -004, -006 and -008 have known mechanism families: content addressing, cgroups/namespaces, attestation formats.
  - Q-L2-007 can always be satisfied conservatively by treating all output as untrusted.
  - Q-L2-009 touches no PCL now that PCL-003 is narrowed.

  Transfer Test criteria 1–4 hold for Q-L2-001..009.
- **Secrets/output residual-risk language product-level enough to constrain L2:** yes for default-deny, explicit authorization and untrusted-by-default output; the narrow-definition gap is P2-3.

## 6. E02 causal isolation (Issue §4)

| Attack | Result |
|---|---|
| One exact shared decision/admission procedure | Yes, frozen with digest before arm output (P1-3 FIXED) |
| Only Provider-behavior evidence differs | Yes by text. Residual hardening in P2-2 |
| Treatment receives no hidden labels | Yes: curator-held labels, no answer key, pipeline digest fixed at E00. Derived-label path hardening in P2-2(c) |
| Arm-specific logic invalidates the run | Yes, explicitly |
| PASS/FAIL/K2/K3 reachable and non-tautological | **FAIL / K2 / K3 reachable. PASS reachability of criterion 4 at minimum n depends on the unfrozen CI method → P1-2.** Not tautological (P3-4) |

## 7. Authority currentness (Issue §5)

- E00 result → protocol `1e79c61a` and E02 result → protocol `e474a817`, both successor blobs. E01 (`3fd824a7`) and E03 (`7ceefde5`) are unchanged and consistent. **MATCH.**
- `PRODUCT_FREEZE.md` binds the PRD, Evidence Index, L2 Register, Migration, all E00–E03 protocol/result blobs and the Issue #3 review/response blobs exactly as they are at HEAD. **MATCH**, except that the Backlog blob is not bound (P2-4).
- E00–E03 are all NOT_RUN; Final Independent Product Review is NOT_RUN; `PRODUCT_FREEZE = NO`.
- The manifest states that this review "only authorizes proceeding with E00–E03" and is not a Freeze PASS. This terminal is FAIL in any case.

## Gate consequence

```text
PASS requires: open valid P0 = 0 AND open valid P1 = 0
               AND no protocol defect making E00–E03 ambiguous/non-auditable
Observed:      open valid P0 = 0
               open valid P1 = 2  (E00 independent-subset unreachable at minimum;
                                   E02 criterion-4 reachability set by unconstrained CI method)
=> L1_AUTHORITY_PACKAGE_SUCCESSOR_REVIEW = FAIL
```

**Routing.** Do not execute E00–E03 under this exact package.
1. Issue successor E00 and E02 protocols that fix P1-1 and P1-2, preferably also P2-1 and P2-2.
2. Rebind the E00/E02 NOT_RUN result placeholders to the new protocols.
3. Update `MIGRATION_FROM_R5.md` and the manifest (P2-4).
4. Open a new context-fresh successor review on the new exact baseline.

The Issue #3 P1 dispositions above (3/3 FIXED) carry forward unless the successor changes PRD §4, PCL-003, Q-L2-001 or the E02 shared-procedure section.
