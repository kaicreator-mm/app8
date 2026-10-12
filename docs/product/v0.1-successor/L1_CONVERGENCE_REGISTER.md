# L1 Convergence Register — app8 v0.1 Successor

Status: ACTIVE  
Controller: Issue #72  
Rule: shortest trustworthy path to study terminals; no optional-tooling recursion.

## Current blockers

| Study | Current state | Exact remaining blocker | Owner class | Minimum next step | Deferred now |
|---|---|---|---|---|---|
| SE10 | tooling merged; 17/17 regression PASS | #58 real independent human Gold | independent humans | execute #58 → SE10 evaluation | extra tooling robustness |
| SE11 | tooling/selection merged; target R5 static PASS | #69 real host target, then #55 hidden truth | Windows host + independent human curator | execute #69 → #55 → SE11 evaluation | non-validity hardening |
| SE12 | HOLD | needs frozen SE10/SE11 Capability/Evidence subject | Web/local | execute protocol once upstream terminal | architecture design |
| SE13 | HOLD | needs SE12 projections | real benchmark | run frozen paired benchmark | production Agent design |
| SE14 | runner merged; 16/16 regression PASS; labels active | independent labels; real paired index waits on SE10+SE11 evidence-backed Capability subject | independent adjudicators | adjudicate labels → after SE10/11 freeze paired index → bind receipt → run once | ranking feature work / synthetic capability metadata |
| SE15 | sample not frozen | two real independent curators + final LO target | 2 humans + real host | top-25 freeze → binding run | more Notepad research/UIA early inspection |
| SE16 | instrument merged / reviewed | freeze private recruitment state + real 8-person cohort | real external users | execute frozen recruitment → terminal | instrument feature expansion |

## No-more-tooling rule

From this register forward, a new change to SE10/SE11/SE14 experimental tooling must state:

```text
FINDING_CLASS=A_OR_B
WHY_STUDY_RESULT_WOULD_BE_INVALID_OR_UNEXECUTABLE=<specific counterexample>
```

Without both fields, defer it.

## Parallel execution lanes

```text
LANE_A_FRESH:
COMPLETE — #53/#61/#66/#68/#71 PASS and closed

LANE_B_WINDOWS:
#69 same Windows candidate host — REAL_HOST execution active

LANE_C_HUMAN:
#58 real independent human Gold — ACTIVE
#55 independent hidden truth — HOLD only on #69
#59 two independent human curators — ACTIVE
#51 real external users — ACTIVE

LANE_D_RESULTS:
SE14 labels may start after Stage-A freeze
SE10/SE11 terminals
→ freeze real SE14 paired index + bind reviewed label receipt
→ SE14 evaluated ranking
→ SE12
→ SE13
```

## Transfer trigger

Do not create the formal Implementation Task DAG merely because L1 work is extensive.

Trigger only after:

```text
SE10=PASS
SE11=PASS
SE12=PASS
SE13=PASS
SE14=PASS
SE15=PASS
SE16=PASS
FINAL_PRODUCT_REVIEW=PASS
PRODUCT_FREEZE=YES
L1_TO_L2_TRANSFER=PASS
L2_ARCHITECTURE_EVIDENCE=COMPLETE
```

Then:

```text
NEXT=IMPLEMENTATION_TASK_DAG
```
