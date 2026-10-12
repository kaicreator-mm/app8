# SE13 Protocol — Agent Utility of app8 Capability Projections

Status: DRAFT_FOR_FRESH_REVIEW
Execution: HOLD_FOR_SE12_ARTIFACTS
Parent: Issue #25
Owning task: Issue #29
Product authority: main@908cee661f3747439bb0366b158903cb9b38b413

## 1. Falsifiable question

Do app8 projections materially improve an Agent's ability to complete representative software tasks compared with giving the same Agent the raw native interface/documentation under a comparable execution budget?

## 2. Deferred subject binding

Execution waits for SE12 to produce frozen representative projections.

Before any benchmark run, an independently reviewed benchmark manifest must pin:

- exact model/provider/version;
- exact Agent harness/version;
- exact raw-doc/native-interface baseline package;
- exact app8 Capability/projection package;
- 24 representative tasks spanning at least 3 software assets/classes;
- task success scorer;
- time/token/tool-call budgets;
- random seed/order.

## 3. Deterministic task population and leakage control

Task population = the **12 frozen SE12 subject Capabilities**, with exactly **two independently authored user-goal tasks per Capability** (24 tasks). No curator chooses only the easiest software/task pairs. Exact software versions, Capability IDs and evidence blobs come from the SE12 subject manifest.

Before examining Agent outputs or any final generated CLI/MCP/Skill instruction examples, an independent task author writes for each subject:

- T0 = one common positive task based on its user-facing intent;
- T1 = one variant/constraint/boundary-sensitive task using its source-supported variation; if no such variation exists, a second materially distinct ordinary user goal is selected from the frozen Capability description with the smallest lexical source-anchor ID.

At least 6 T1 tasks must require material constraint/variant/unsupported-boundary reasoning. If the 12 subjects cannot yield 6 such tasks, verdict is BLOCKED; **do not replace Capabilities**.

Commit the 24 task descriptions, objective scoring scripts/fixtures, exact source anchors and the complete candidate-task set before benchmark execution or final projection exposure. Task author cannot read generated projection examples during task authoring.

No post-hoc task replacement is permitted. If a selected task literal appears in a generated Skill/example, that task remains in the audit manifest and the study is BLOCKED until an independently reviewed pre-run remedy; it is not silently swapped for an easier task.

## 4. Study design

Paired two-arm evaluation:

- BASELINE: raw official docs/help/native interfaces only;
- APP8: same underlying software access plus frozen app8 projections/Capability-facing material.

The same model/harness, environment and budget are used in both arms.

Run each task three independent times per arm, yielding 72 runs per arm.

Counterbalance arm ordering and task ordering. Where feasible, scoring is blind to arm.

## 5. Primary outcome

Task success rate according to frozen task-specific objective scorers.

A task scorer must inspect actual outputs/state, not accept the Agent's self-report.

## 6. Secondary outcomes

Record:

- tool/interface selection errors;
- invalid command/call count;
- retry count;
- one-off glue-code creation;
- total tool calls;
- model tokens;
- wall-clock execution time where comparable;
- unsupported-action attempts;
- recovery success after failures.

## 7. Fairness rules

The APP8 arm may not receive hidden answer keys, decisive fixtures or task-specific scripts unavailable to baseline.

Both arms receive equivalent credentials and native software access.

If app8 projections encode a task's literal expected answer, that task is invalid and must be excluded before running either arm.

## 8. Frozen PASS thresholds and paired statistical unit

PASS requires:

- APP8 aggregate success rate >= BASELINE + 0.15 absolute;
- **task-cluster paired bootstrap** 95% two-sided percentile CI for success-rate delta has lower bound > 0;
- APP8 invalid/unsupported action rate does not increase by >0.05 absolute;
- no software class shows APP8 success deficit >0.10 absolute;
- at least one of retries, glue-code burden, or tool-selection errors improves by >=20% relative without material success tradeoff.

**Bootstrap exact algorithm:** For each of 24 tasks, compute mean success of its three APP8 runs and three BASELINE runs; task paired difference = APP8 mean - BASELINE mean. Draw 10,000 bootstrap samples of 24 **paired task IDs** with replacement using committed seed `app8-SE13-task-bootstrap-v1`; average paired differences in each resample, and take the 2.5th and 97.5th percentiles. Do **not** resample 144 runs or 72 per arm as independent; the unit is the paired task.

Token/time cost is reported. A success gain achieved by extra time/token/tool budget beyond the frozen common cap does not count.

## 9. Infrastructure failure policy / anti-cheating

Freeze task population, scoring, execution identities, all three trial seeds per arm, bootstrap implementation and thresholds before first run. Run all task × arm × trial combinations.

Classify genuine infrastructure failures only from objective host logs (e.g., unavailable provider, failed machine boot before Agent execution), **not** Agent command errors, timeout due to poor task behavior, or tool-use mistakes. Apply **one paired rerun** using the predeclared reserve seed to **both arms** for that task/trial when an external infrastructure failure affected either arm. Retain original and rerun logs. If >5% of paired task/trial cells remain externally blocked, verdict = BLOCKED; otherwise unresolved cells are counted as failures for the affected arm, with sensitivity analysis reported. No selective reruns after observing score.

## 10. Outputs

Produce:

- benchmark manifest;
- task-construction provenance;
- exact arm packages;
- all run traces;
- objective scorer results;
- paired aggregate statistics;
- secondary metrics;
- infrastructure exclusions;
- terminal;
- What Was NOT Proven.

## 11. What this study cannot prove

SE13 cannot prove user demand, business moat, universal model benefit, long-term maintenance cost or safety. It tests Agent utility only on the frozen tasks/models/environments.

## 12. Protocol terminal

~~~text
SE13_PROTOCOL = READY_FOR_FRESH_REVIEW
SE13_EXECUTION = HOLD_FOR_SE12_ARTIFACTS
PRODUCT_FREEZE = NO
L2_READY = NO
~~~
