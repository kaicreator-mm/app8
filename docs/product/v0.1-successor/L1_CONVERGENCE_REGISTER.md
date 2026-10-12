# L1 Convergence Register — app8 v0.1 Successor

Status: ACTIVE  
Controller: Issue #72  
Rule: shortest trustworthy path to study terminals; no optional-tooling recursion.

## Current blockers

| Study | Current state | Exact remaining blocker | Owner class | Minimum next step | Deferred now |
|---|---|---|---|---|---|
| SE10 | tooling R1 | #61 Fresh PASS on PR #60, then real Gold | Fresh reviewer + independent humans | merge #60 → execute #58 | extra tooling robustness |
| SE11 | tooling/target R1/R3 | #66 PASS; #68 R3 PASS; #69 target; #55 truth | Fresh reviewer + Windows host + independent curator | close reviews → merge → target/truth → execute | non-validity hardening |
| SE12 | HOLD | needs frozen SE10/SE11 Capability/Evidence subject | Web/local | execute protocol once upstream terminal | architecture design |
| SE13 | HOLD | needs SE12 projections | real benchmark | run frozen paired benchmark | production Agent design |
| SE14 | tooling R1 | #71 PASS, independent labels | Fresh reviewer + independent labeler | merge #70 → freeze labels → run once | ranking feature work |
| SE15 | sample not frozen | two real independent curators + final LO target | 2 humans + real host | top-25 freeze → binding run | more Notepad research/UIA early inspection |
| SE16 | instrument R1 | #53 PASS, then real 8-person cohort | Fresh reviewer + real users | merge #52 → freeze private recruitment state → execute | instrument feature expansion |

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
#53
#61
#66
#71

LANE_B_WINDOWS:
#68 R3
→ #67 merge
→ #69

LANE_C_HUMAN:
after #60 merge -> #58
after #62/#69 -> #55
#59 two human curators when frozen source set is accepted
after #52 merge -> #51 real users

LANE_D_RESULTS:
SE14 immediately after #70 + labels
SE10/SE11 terminals
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
