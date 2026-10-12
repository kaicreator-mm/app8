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

## 3. Task construction and leakage control

Task authors work from the frozen Capability/Evidence authority and ordinary user-facing software goals, not from generated CLI/MCP/Skill examples.

The 24 tasks must be frozen before Agent-run outputs are visible and balanced across:

- assets/classes;
- read/inspect vs mutate/produce behavior where applicable;
- simple vs multi-step tasks;
- tasks exercising material constraints/variants;
- at least 6 tasks containing a plausible unsupported or boundary-sensitive choice.

No task may copy a generated projection example verbatim. No task scorer or hidden fixture may be available to either Agent arm.

If a projection was created using a task later selected for SE13, that task is excluded before any benchmark run and replaced using the same predeclared selection rule.

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

## 8. Frozen PASS thresholds

PASS requires:

- APP8 aggregate success rate >= BASELINE + 0.15 absolute;
- paired bootstrap 95% CI for success-rate delta has lower bound > 0;
- APP8 does not increase invalid/unsupported action rate by > 0.05 absolute;
- no asset class shows an APP8 success deficit > 0.10 absolute;
- at least one of retries, glue-code creation, or tool-selection errors improves by >= 20% relative without a material success tradeoff.

Token/time cost are secondary and reported, not hidden. A success gain achieved only by an unbounded budget increase is invalid; both arms obey the frozen budget.

## 9. Anti-cheating

Freeze benchmark manifest, task-construction rule, tasks, scorers, model/harness identities and thresholds before first run.

Preserve all failed runs. No selective rerun except a predeclared infrastructure-failure policy applied symmetrically to both arms.

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
