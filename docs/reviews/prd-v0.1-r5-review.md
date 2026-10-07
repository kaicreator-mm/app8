<!-- ai-dev:event:v2 -->
```yaml
schema: ai-dev/event-v2
event: REVIEW_RESULT
actor_role: reviewer
operator_kind: claude-code
operator_id: "claude-code:windows-01-fresh-subagent"
session_ref: "app8-prd-r5-fresh-review-20261007"
transport_actor: "github:kaicreator-mm"
dispatched_by: "claude-code:windows-01"   # NOT context-fresh; dispatch only, no review conclusions supplied (see §0)
task: "#2"
sha: "1f9c2ab79ee4000dc4481142a7535ae8db9a5b33"
tree_sha: "51a8c8056f21c00e436443948e563d3a0fd6c841"
subject: "docs/product/prd-v0.1-r5.md @ blob 5d8ff030ec3aa0694f01f61ee4372fd01f013433"
standard_revision: "7929012f36a2202dcc2edc7a414b8163adc7afbd"   # ADS 4.9.0, per .dev-standard/VERSION
review_kind: context-fresh-successor-adversarial-product-review
review_policy: required        # Issue #2 Freeze terminal / PRD §20 L1-REVIEW
gate: L1-REVIEW
mode: READ_ONLY
status: FAIL
findings:
  p0: 1
  p1: 5
  p2: 6
  p3: 2
independence: context-fresh (self-attested; see §0)
baseline_recheck: MATCH        # main HEAD == reviewed sha; PRD blob == reviewed blob, re-read immediately before publishing
product_freeze: NO
l2_ready: NO
local_validation_required: false
next_state: changes-requested
```

# PRD v0.1-r5 context-fresh successor adversarial review — FAIL (P0=1 / P1=5 / P2=6 / P3=2)

## 0. 身份、独立性、事实源与派发披露

**Reviewer**：`operator_kind=claude-code`，`operator_id=claude-code:windows-01-fresh-subagent`，`session_ref=app8-prd-r5-fresh-review-20261007`，`transport_actor=github:kaicreator-mm`。

**独立性（Issue #2 "Reviewer independence"，PRD §20/§35）**

- 本 operator 是本次新建的子 agent 会话，启动时没有任何 app8 对话历史。它没有撰写 r1–r5，也没有参与过任何更早的 app8 PRD 审核。
- `operator_id`/`session_ref` 与 r4 reviewer（`claude-code:windows-01` / `app8-prd-r4-successor-review-20261007`）不同。PRD/README/review 文件的作者在 GitHub 上仅表现为 transport `kaicreator-mm`，没有记录逻辑 author operator，因此无法在 GitHub 上逐一核对 author context。上述判断依据的是本会话从零开始这一事实，属于**自我声明**，不是第三方证明。
- **派发披露**：本任务由 `claude-code:windows-01` 派发。按 Issue #1 中 r4 REVIEW_RESULT 的自述，该 operator 不满足 context-fresh。派发方只给出了身份字段和流程纪律，**没有提供任何审核结论、finding 或倾向**。全部结论都是本会话在阅读 GitHub durable state 后独立得出的。派发提示词按要求逐字附在文末（附录 A），供审计。
- 为了满足 Issue #2 的审核目标 9（前序可审计性），本会话读取了 Issue #1 中的 r4 审核正文和 `docs/reviews/*`。这些是前序证据，不是本轮结论来源。凡与前序意见一致之处，均已在 r5 文本上独立复核。

**事实源**：只使用 GitHub durable state。

- `kaicreator-mm/app8@1f9c2ab79ee4000dc4481142a7535ae8db9a5b33`（tree `51a8c80…`）。全部 8 个文件按 exact SHA 读取，并用 `git hash-object` 逐一核对 blob：PRD r5 = `5d8ff03…` ✔，r4 = `f083439…`，r3-review = `7341936…`，r3-disposition = `95e29d2…`，r4-review = `0ad3c98…`，r4-disposition = `85a72cc…`，README = `64f3e23…`，`.dev-standard/VERSION` = `7a0c7dc…`。
- 提交历史 `47349c3 … 1f9c2ab`，以及 `322e0ed` 时期的 r3 占位文件。
- Issue #1 body 与 3 条评论；Issue #2 body（body 未被编辑过，`userContentEdits=[]`）。
- `kaicreator-mm/ai-development-standard@7929012`：`AGENTS.md`、`prompts/independent-review-bootstrap.md`、`templates/agent-event-comment.md`、`schemas/agent-event-v2.schema.json`、`schemas/review-finding-v1.schema.json`、`schemas/review-aggregation-v1.schema.json`、`standards/DEVELOPMENT_WORKFLOW.md`、`prompts/L1_PRODUCT_EVIDENCE.md`、`docs/implementation/4.0.0/ADVERSARIAL_REVIEW.md`（severity 语义）、`docs/implementation/4.9.0/PRODUCT_FREEZE.md` 与 `PRODUCT_REVIEW_FINDING_DISPOSITION.md`（作为 Freeze 先例）、`standard-manifest.json`。
- 没有读取任何本机 app8 工作副本。

**Baseline 复核**：发布前重新读取，`main` HEAD = `1f9c2ab…`，PRD blob = `5d8ff03…`，与 Issue #2 baseline 一致，**无 drift**。

**READ_ONLY**：没有修改任何仓库文件、Issue body、label 或 state。只写了 ROLE_CLAIMED（#issuecomment-6032524776）和本条事件。

**方法限制**：纯静态审核，没有执行任何代码或实验。下文的统计数值是本会话按 Wilson score（z=1.96）独立计算的结果，标为 computed。

---

## 1. 总判

r5 是一次实质性的修订。r4 的 P0-1 在**论题层面**已经解决：§1/§2 选定了严格的 ENFORCED 安全模型，C/D 两臂共用同一个 enforcing runtime，prevalence 被降级为 L1 问题证据。生命周期死锁（r4 P1-8）也已解开。L1-PREV 的 PASS/FAIL/BLOCKED 在数学上都可以达到。REFUTED 不再按时间判定支配关系。

剩下的 P0 位于**论题的证伪工具**上，形式与 r3 P0-1 相同：在 r5 中，唯一检验产品论题的 T2，其 C 臂的 Admission 规则与 §12 冲突；REFUTED 层的主指标按构造必然成立；T2 没有 PASS 判据；T2 FAIL 也没有后果（r4 的 Kill criteria 被无声删除）。如果按现状冻结，产品论题将不可证伪。

P1 主要集中在以下几处：

- Freeze 规则中 "P1 可 defer" 的分支与 pinned ADS 冲突；
- L1-PREV 在 PASS 方向上仍存在假阳性通道；
- REFUTED 棘轮的兼容性谓词和 lineage 归属都未定义；
- 环境 class 的实际成员（尤其是 kernel）没有绑定，而 enforcer 是否有效恰恰取决于它；
- threat model 对恶意 Provider 的隔离强度假设留白。

---

## 2. P0

### P0-1 — T2 无法证伪 r5 的价值论题：C 臂与 §12 冲突，REFUTED 层按构造必过，PASS 规则与 FAIL 后果缺失

**Location**：PRD r5 §1（value channels 1–3），§11，§12，§22，§24，§38；对比 r4 §35 K2（r5 中已删除）；先例：`docs/reviews/prd-v0.1-r3-review.md` P0-1。

**Expected**：唯一检验 "executable evidence adds material value after typed interface + same enforcing runtime" 的 gate，必须同时满足以下条件：
(a) 两臂 Admission 规则都有定义，并且在 PRD 内自洽；
(b) 主指标在两种结果下都可能出现，不是按构造必然成立；
(c) 有冻结的 PASS/FAIL 判据；
(d) FAIL 有明确的产品后果。

**Actual**：

1. **C 臂在 §12 下无定义。** §12 规定，security-required 属性的 ALLOW 需要 "ENFORCED guarantees **and trusted enforcer-validity Evidence**"，而 enforcer-validity Evidence 是 executable evidence（§1："executable evidence that the enforcer works for the bound Provider/invocation class"）。C 臂（"static/publisher declarations"）按定义没有这类证据。于是只剩两种读法：
   - C 臂遵守 §12 → 所有 security-required 调用都是 DENY/UNKNOWN → benign availability 在 C 臂恒为 0，D 臂在 "benign availability / false denial" 指标上按构造获胜；
   - C 臂不遵守 §12 → 这与 §24 的 "share the same … **policy**" 矛盾，而且 PRD 没有写出 C 臂用的是什么规则。
   
   另一种读法是：enforcer-validity Evidence 由两臂共享。那么 C 与 D 的差别就只剩 upstream VERIFIED/REFUTED 观察，又回到第 2、3 点。
2. **REFUTED/stale 层按构造必然成立。** 该层的定义是 "cases with **externally established** refutation/currentness failure"。如果这些 refutation 预先存在于 D 的 trusted store 中，D 的 "pre-execution detection rate" 就恒为 100%，C 恒为 0%。"contained-violation attempts that reached the enforcer" 同样如此。这正是 r3 P0-1 中 "E0a 按构造必过" 的形态，并且与 T1（Admission 单元测试）重复。PRD 没有要求 D 的 evidence 由 D 自己的 conformance runner 在不知道分层真相的情况下生成。
3. **Channel 1 没有落成规则。** §11 只规定 REFUTED 支配 "**VERIFIED assertion**"。但在严格模型下，ALLOW 的依据是 ENFORCED + enforcer-validity evidence，而不是对 upstream 行为的 VERIFIED 断言。对 "provider 会尝试联网，但网络已被 enforcer 拒绝" 这种情况，§11/§12 中没有任何一条规则会产生 DENY。所以 §1 Channel 1（"already REFUTED … is denied before the enforcing runtime is asked to execute it"）在规范层没有对应规则。同时，"invocation class" 和 enforcer-validity Evidence 的生成方法也没有定义。
4. **T2 没有 PASS 判据。** §24 列出了 4 个主指标和 3 个分层，但没有写哪些指标需要达到什么阈值、方向如何、如何组合才算 PASS。文中只规定了扩样后 "insufficient evidence → FAIL"。
5. **T2 FAIL 没有产品后果。** r4 §35 的 K1–K7（包括 K2 "Evidence adds no incremental value → stop platform expansion"）在 r5 中被整体删除，`prd-v0.1-r4-disposition.md` 也没有记录这次删除。§22 只规定了 T3/T4/T6 FAIL 时的处置。
6. **Agent 层面的价值通道无法观测。** 四臂 "share the same Provider"，而 §38 说 Agent 回答的是 "Which admissible Provider should be selected?"。只有一个 Provider 时，D 的 DENY 不可能提高 functional task success（没有替代 Provider 可选）。Channel 2（"prevent over-broad allowlists"）在 "same enforcement policy is active in both arms" 的条件下同样无法观测。没有任何 gate 测量 Channel 2。

**Required change**：

- 明确写出 C 臂的 Admission 规则。建议：C 可以凭 *declared* ENFORCED + 同一个 enforcer ALLOW，但没有 provider-bound executable evidence；"缺少声明" 与 "缺少 evidence" 采用相同的 fail-closed 默认。同时说明 enforcer-validity evidence 是否在两臂之间共享。
- 规定 D 臂的 Evidence 必须由 D 的 conformance runner 在实验中自行生成，并且对分层真相 blind（不得预载 ground-truth refutation）。这样 "pre-execution detection" 测到的是 suite + Admission 的真实能力，而不是查表。
- 在 §11/§12 中写出 Channel 1 规则：trusted REFUTED 对 overlapping 的 upstream 行为断言 → DENY，即使存在 ENFORCED。同时写明这对 availability 的代价。另外定义 "invocation class" 和 enforcer-validity evidence 的生成协议（例如对 enforcer 做 planted-violation probe）。
- 为 T2 冻结 PASS 规则：每个主指标的 CI 方向与阈值（例如 detection 下界 ≥ X；benign availability 采用非劣效界；functional reliability 下界 > MME），以及多个指标的组合规则（AND 或预注册的 primary）。
- 恢复 T2 FAIL 的产品后果（相当于 K2，例如 stop platform expansion / 需要 successor PRD）。如果删除 r4 §35 是有意为之，就在 disposition 中逐条记录。
- 引入可选的替代 Provider/版本，让 Agent 选择通道可以被观测；或者明确声明 T2 不测 Agent 选择价值，并删除 §1/§38 中对应的价值主张。为 Channel 2 设计可测量的对照（evidence 导出的最小 allowlist vs declaration 导出的 allowlist），或者把 Channel 2 降级为非主张。

> 定级理由：按 ADS 4.0.0 §6，P0 指 authority-breaking 的缺陷。冻结一个主检验按构造可通过、FAIL 无后果的 PRD，等于让产品论题失去证伪能力。本仓库 r3 P0-1 对同类缺陷的定级是 P0，本条与其一致。这一条不否定产品方向，只要求把 T2 写成可以失败的实验。

---

## 3. P1

### P1-1 — "every P1 has explicit independently accepted defer disposition" 与 pinned ADS 的 P0/P1 语义冲突

**Location**：Issue #2 "Freeze terminal"，PRD r5 §20（L1-REVIEW PASS），§21；ADS@7929012 `schemas/review-finding-v1.schema.json`，`docs/implementation/4.0.0/ADVERSARIAL_REVIEW.md` §6–§7；app8 中不存在 `.dev-standard/PROJECT_OVERRIDES.md`。

**Expected**：pinned ADS 有以下规定：

- review-finding-v1 中，P0/P1 处于 `status=DISPOSITIONED` 时，`resolution_code` 只能是 `FIXED | INVALIDATED_BY_EVIDENCE`；`DEFERRED`/`ACCEPTED` 只适用于 P2/P3；
- 聚合不变式 2："any unresolved valid P0/P1 blocks PASS"；
- §6："MUST NOT redefine P0/P1 as non-blocking merely to obtain PASS"。

**Actual**：PRD §20 规定，在 "P1 被 defer" 的情况下 L1-REVIEW 可以 = PASS，也就是在存在未解决有效 P1 时给出 Review Gate PASS。尚未 Frozen 的 PRD 和 Issue 都不是高于 standard 的已生效权威，项目也没有 PROJECT_OVERRIDES。

**Required change**：L1-REVIEW PASS 只能在 open P0 = 0 且 open P1 = 0 时成立。如果某个 P1 需要降级，必须通过有证据的 severity 重判（ADS 4.0.0 §7 "Severity disagreement"：先解决影响事实，再由授权方处置），并留下 finding 记录。不能用 "defer" 绕过。要么同步修改 Issue 的 Freeze terminal 措辞，要么通过 PROJECT_OVERRIDES 显式说明，并经独立审核确认这不违反 ADS 硬约束。
（本轮结论不受此条影响：存在 P0，terminal 在任何读法下都是 FAIL。）

### P1-2 — L1-CAL/L1-PREV：FAIL 方向已闭合，PASS 方向仍有假阳性通道，跨版本重跑语义不明

**Location**：PRD r5 §17，§18，§34。

**已核实（computed, Wilson, z=1.96）**：

- n=80、0 事件时上界 = 4.58% < 5% ✔；
- n=80 时 PASS 需要 k ≥ 8（下界 5.15%），1–7 事件 → BLOCKED；
- n=160 时 FAIL 需要 k ≤ 2（上界 4.44%），PASS 需要 k ≥ 14（下界 5.28%）；
- L1-CAL 在 40/40 时下界 = 91.2%，39/40 时 = 87.1%，即 PASS 实际上要求 100% 检出。

这些规则在**未加权、按工具计数**的口径下都可以达到，并且 fail-closed。

**Actual（残余缺口）**：

1. **只校准了灵敏度，没有校准特异度。** L1-CAL 只用 planted-positive。一个过度报警的 detector（例如把任何联网尝试都判为 false-safe）能轻松通过 L1-CAL，然后在 L1-PREV 中把流行率推过 5%，造成**错误 PASS**。这是推动产品前进的方向，需要最严格的防护。
2. **gate 使用的估计量与单位未冻结。** "Primary statistic counts … declarations"（按 claim），而 n ≥ 80 的单位是 tools。按 claim 计数时 claim 在工具内聚类；如果采用 usage-weighted 估计，有效样本量会小于 n。§18 中 "n ≥ 80 permits zero-event upper bound < 5%" 只在未加权按工具计数时成立。
3. **UNKNOWN 在 gate 中的处理未定义。** 文中要求同时报告 best-case 和 worst-case 两个界，但 PASS/FAIL 按哪个界判定没有写。如果按 worst-case（UNKNOWN 计为 false-safe）判 PASS，就是向上偏差。
4. **detector 的身份没有在 CAL 与 PREV 之间冻结。** 没有要求 L1-PREV 使用与 L1-CAL 相同 digest 的 detector。
5. **跨版本语义自相矛盾。** §18/§34 规定负面结果 "cannot be erased/superseded"，同时又允许 "rerun after negative result with independent review approval"。如果 successor study PASS，L1-PREV 是否变为 PASS 没有说明。如果会变，就是不带 alpha 校正的跨版本 optional stopping；如果不会变，重跑就没有意义。
6. **materiality 的判定者未设盲。** 谁来判定 "material false-safe"、判定时是否知道假设方向，都没有规定。

**Required change**：

- L1-CAL 增加 planted-negative（真实安全的声明）集合，并为特异度设 Wilson 下界门槛。
- 冻结 gate 使用的单位（primary = per-tool 未加权，其余口径仅作报告），或者给出加权估计的有效 n 与相应的最小 n。
- 规定 PASS 按 UNKNOWN 计为非 false-safe 的保守界判定，FAIL 按 UNKNOWN 计为 false-safe 的界判定。
- L1-PREV 必须使用 L1-CAL 时的 detector digest。
- 规定跨版本组合规则：一旦 FAIL，L1-PREV 保持 FAIL，除非新版本引入的新信息经独立审核认定为改变了被测总体，并且采用预注册的 alpha 分配；所有版本合并报告。
- materiality 由对假设方向设盲的独立判定者给出。

### P1-3 — REFUTED 棘轮仍可被绕过：兼容性谓词未定义、guard 可过拟合、lineage 归属不可判定、退役可以自批

**Location**：PRD r5 §5.1，§11（overlap、ratchet、retirement、untrusted external refutation）。

**Actual**：

1. `environment_compatible(r, s)` 和 `invocation_compatible(r, s)` 都**没有定义**。如果实现为 "template digest 相等"，那么对 EnvironmentTemplate 做任意无关改动（template 绑定了 15 项，任何一项变化都会改变 digest），或对 invocation template 做微调，就会让 overlap 为假，旧 REFUTED 失效。这就是 r4 P1-3 的 "身份微调绕过" 在环境/调用维度上重新出现。
2. **guard 过拟合。** overlap 只检查 `guard_s.accepts(r.counterexample_fixture)` 这一个具体 fixture。一个恰好拒绝该 fixture 字节（或其细微特征）的新 guard 就能 "legitimately exclude"，而同一类缺陷仍在域内。"legitimately" 没有可操作的定义。
3. **lineage 归属不可判定。** §5.1 只规定 "starting a new lineage requires reviewed disposition"，但没有规定如何判定一个 Provider 属于哪个已有 lineage。fork、更名、重新打包后以新的 "source family" 出现时，系统不会知道需要 disposition。adapter 语义 lineage 被纳入 lineage 的组成部分，因此通过 "reviewed" 重开 adapter lineage，会让同一个上游缺陷的反例不再被继承。
4. **退役与外部 refutation 拒绝都可以自批。** `REFUTATION_RETIRED` 只需要 "trusted first-party review"；外部 refutation 可以 "explicitly reject … through an audited disposition"，不必 replay。两者都没有独立性要求，而 threat model 把 careless publisher 列为 IN SCOPE。
5. 对没有 input-domain guard 的属性（例如与输入无关的网络行为），`guard_s` 未定义，overlap 不可计算。

**Required change**：

- 定义两个兼容性谓词：按 counterexample 所依赖的 template/invocation 维度判定，未知维度视为 compatible（fail-closed）。
- refutation 记录缺陷类别（例如 "playlist indirection" "protocol=http"），并附带一个可复现的 counterexample 邻域/变异族。新 scope 必须以**域级规则**（格式、协议、参数类）排除整个类别，而不是排除单个 fixture，并且需要独立审核。
- 用确定性规则把 lineage 归属到上游 source family（例如上游仓库/包身份加内容相似度阈值），未知时归入已有 lineage（fail-closed）。上游缺陷的反例在 source-family 层棘轮，不随 adapter lineage 重置。
- 退役、以及不 replay 就拒绝外部 refutation，都需要独立 reviewer（与 §35 相同的定义）。
- 无 guard 时把 `guard_s` 定义为 accept-all。

### P1-4 — EnvironmentTemplate 只绑定 "class"，没有绑定实际成员；enforcer 有效性依赖的 kernel 特性因此没有被匹配

**Location**：PRD r5 §8.1（"CPU feature/microarchitecture class"，"kernel/runtime class"），§8.2，§10，§12，§27。

**Actual**：template digest 绑定的是**策略和类别**。实际 CPU/kernel 的取值既不在 template digest 中，也不在 InstanceBindings 中（§8.2 的例子只有 /in、/out、secrets、clock、resource limits）。因此：

1. Admission 无法校验生产 host 是否属于该 class。生产 host 只要匹配 template digest，就会被视为匹配。
2. §27 T5 要求第二台 runner "differ in actual member values"，说明成员确实会变化，但 Evidence 记录（§10）不包含证据产生时的实际成员。
3. 更严重的是，**enforcer 的有效性依赖 kernel 的具体特性**（seccomp filter 能力、Landlock ABI 版本是否支持网络规则、cgroup v1/v2、user namespace 是否可用）。在同一个 "kernel class" 中，Kernel A 上得到的 enforcer-validity Evidence 不能外推到 Kernel B。严格模型的全部安全性都建立在 enforcer 上，所以这里是一个安全缺口，不只是可复现性问题。
4. VERIFIED_IN_SCOPE 的含义是 "EnvironmentTemplate + valid InstanceBindings"，等于把观察过的少数实例外推到 schema 允许的全部实例（例如任意大小的 /in，以及 bounds 内的任意 resource limits），而外推规则没有写明。

**Required change**：

- 增加 `HostRealization`：实际 CPU 特性集、kernel 版本，以及 enforcer 相关能力（seccomp/Landlock ABI/cgroup/userns）的探测结果。在 InstanceBindings 中记录它，并要求 Admission 校验其类别成员资格。
- enforcer-validity Evidence 必须绑定 enforcement 相关能力的实际值，或者把这些能力冻结为 template 的**精确**要求。
- Evidence 记录产生时的 HostRealization。
- 写明 instance-schema 的覆盖规则：哪些维度在 schema 内可以外推、哪些必须在边界值上采样。

### P1-5 — threat model 对恶意 Provider 只写了 "PARTIALLY IN SCOPE"，没有说明安全边界依赖的隔离强度与残余通道

**Location**：PRD r5 §2.3，§8.2（"declared secrets/credentials handles"），§15，§29。

**Actual**：严格模型把安全性完全交给 enforcer，但 §15 对 "Malicious or compromised Provider" 和 "Test-aware Provider" 只写了 "PARTIALLY IN SCOPE"，没有列出哪些在范围内、哪些不在：

- **隔离强度假设没有说明**：namespace/container、gVisor 还是 microVM？kernel 0-day / 沙箱逃逸是否在范围外？对恶意代码来说，这一项决定了 "ENFORCEABLE_SECURITY" 是否成立。
- **授权通道内的外泄**：Provider 拿到 "declared secrets/credentials handles" 和输入内容后，可以把它们编码进 `/out`，再经过 Agent 或允许的 egress 外流。这属于 §2.3 的 non-enforceable 类，但 threat model 没有点名，也没有说明默认处置（禁止向不受信 Provider 授予 secret，还是 ACCEPTED_RESIDUAL_RISK）。
- **时间触发 / 输入触发的恶意行为**（time-bomb、只对真实数据特征触发）：对 reliability 断言不可防御，应明确声明。
- held-out/per-run 生成 fixture 的**规模和更新频率**没有下限；生成器分布本身可以被指纹识别。
- r4 §26 Output trust（不提升 UNTRUSTED_EXTERNAL，这是 r3 P2-3 的关闭依据）在 r5 中被删除，threat model 的 "Prompt-injected Agent" 一行因此缺少对 Provider 输出的处理。

**Required change**：把 "PARTIALLY" 拆成明确的 IN/OUT 条目：

- 写明 reference enforcer 的隔离等级，以及 "sandbox escape / kernel exploit = OUT OF SCOPE" 之类的假设；
- 写明 secret/输入经输出通道外泄的默认处置（建议：security-required 调用默认不向 Provider 授予 secret，例外走 ACCEPTED_RESIDUAL_RISK）；
- 写明 time-bomb / data-triggered 行为对 OBSERVATIONAL_RELIABILITY 不设防；
- 为私有 held-out 部分设定最小比例和轮换规则；
- 恢复或显式替代 r4 §26 的 output-trust 边界。

---

## 4. P2

### P2-1 — §12 把 ALLOW/DENY/UNKNOWN 映射为 PASS/FAIL/BLOCKED，与 §36 自相矛盾

**Location**：§12（signature `-> PASS | FAIL | BLOCKED` 与映射），§36 最后一句。
**Expected**：§36 规定 "Business-domain outcomes such as ALLOW/DENY/UNKNOWN … are fields … not Gate states"。
**Actual**：§12 又把它们映射成 Gate 状态。一次正确的 DENY 被记为 FAIL；UNKNOWN 被记为 BLOCKED，而 §36 中 BLOCKED 的定义要求 "an authorized bounded next attempt remains"，对 `INPUT_DOMAIN_UNDECIDABLE` 并不成立。
**Required change**：把 Admission 的返回类型改为 DecisionRecord（`decision = ALLOW|DENY|UNKNOWN`），删除映射。只有 T1 等 gate 使用 PASS/FAIL 来表示 "expected decision 是否命中"。

### P2-2 — bounded TOCTOU 主张对被绑定对象成立，但有两处边界规则缺失

**Location**：§9 第 5 步（"where the tool permits it"），§13。
**判定**：对 DecisionRecord 绑定的 content-addressed 对象，"closes check/use substitution" 的有界主张成立（copy-in + input/dependency-closure digest + 从不可变对象执行 + mismatch → DENY）。
**Actual**：

1. 当工具**不允许**强制解释、也不暴露实际采用的解释时，PRD 没有给出回退规则。T3 写的是 "forced or mismatch blocks"，但 mismatch 无法观测时怎么处理没有写。
2. DecisionRecord 没有**时效或单次使用**规则。在 Admission 之后、执行之前（或重复使用该 DecisionRecord 时），新到达的 trusted REFUTED 或吊销不会生效。这是 policy/evidence 状态上的 check/use 窗口，Channel 1 的价值因此可以被绕开。
3. content-addressed store 在宿主上的目录是否只读或不可变，没有要求。runner 属于 trusted，但同宿主上的其它进程不在 trusted 假设内。

**Required change**：

- 不可强制且不可观测时，该 guard 不算 ENFORCED（降为 UPSTREAM_OBSERVED → 不能用于安全 ALLOW）。
- DecisionRecord 单次使用，或者在执行前校验 refutation-index/revocation 版本仍然是当前版本。
- 执行前对挂载对象再次计算 digest，或者使用不可变快照。

### P2-3 — r3 审核证据：正文已恢复，但来源、主体和撰写者均不可审计；r3 disposition 的 "successor" 列由作者填写

**Location**：`docs/reviews/prd-v0.1-r3-review.md`（blob `7341936`，commit `77b5b31` "restore full …"），`docs/reviews/prd-v0.1-r3-disposition.md`；先前的占位 blob（`322e0ed` 时为工具错误文本）。
**Actual**：

1. 恢复后的 r3 审核没有 reviewer operator_id/session_ref，没有 reviewed SHA/blob，也没有对应的 GitHub 事件。它审核的 `prd-0.1-r3.md` 以及它引用的 `prd-0.1-r1-review.md`/`prd-0.1-r2-review.md` 在本仓库任何提交中都不存在（仓库从 r4 开始）。因此 r3 findings 的 Location 无法对照原文核查。
2. 恢复提交没有说明来源，也没有给出原件 hash。Issue #1 的 r4 审核披露 r1/r3 审核文本出自本机、非 GitHub 的 `claude-code:windows-01` 会话，所以正文的真实性只能是 **NOT VERIFIED**。
3. r3-disposition 的 "Successor disposition" 列（例如 "NOT VERIFIED; r4 review reopened …"）是作者对 r4 审核的转述。r4 审核本身只给出了总体结论 `R3_CLOSURE = NOT_VERIFIED`，没有逐条裁决。
4. 两份 disposition 文件使用的是自定义状态词（AUTHOR_RESPONSE_RECORDED / AUTHOR_RESPONSE PRESENT / NOT VERIFIED），不是 ADS review-finding-v1 的 `status`/`resolution_code`。

**判定**：r3 findings 的**内容**现在已经在 GitHub 上，可以对照 r4/r5 追溯，r4 的 P1-1 因此在内容层面关闭。**来源与完整性**无法审计。好在 r4 审核（Issue #1，与 `docs/reviews/prd-v0.1-r4-review.md` 逐字一致，本轮已用 diff 核对）是 durable 的，并且已经覆盖 r4 全文，所以这一点不阻断 Freeze 逻辑。
**Required change**：在 r3-review 文件头部补充 provenance（来源会话/operator、原始文件 hash 或 "provenance unrecoverable" 声明、被审对象不可得的声明）。把 "Successor disposition" 列改名为 "Author's reading of r4 review"。disposition 改用 ADS 的 `status`/`resolution_code` 词汇。本轮对 r3 中 "AUTHOR_RESPONSE PRESENT" 三项的独立裁决见 §6.2。

### P2-4 — r4→r5 存在未披露的实质删除

**Location**：r4 §26 Output trust，§33 Hard-case probe，§35 Kill criteria K1–K7，§36 Anti-metrics → r5 中均不存在；`prd-v0.1-r4-disposition.md` 没有提及。
**Expected**：successor review 需要在 GitHub 上看到完整的语义 delta（参照 ADS 4.9.0 PRODUCT_FREEZE 中 "UNEXPLAINED_MATERIAL_DELTA=0" 的做法）。
**Actual**：上述删除中，K2 的删除影响 P0-1，Output trust 的删除撤销了 r3 P2-3 的关闭依据（见 P1-5），anti-metrics 的删除去掉了防止 vanity metric 的约束。没有任何记录说明这些删除是有意的。
**Required change**：在 r4-disposition（或新的 r5 delta 记录）中列出全部删除与合并，逐项说明理由。需要保留的内容恢复到 r6。

### P2-5 — T5 没有 PASS 判据；Freeze 的记录权威与顺序未定义；L1-ADOPT 的参与者独立性未定义

**Location**：§27，§16/§20/§21，§19。
**Actual**：

1. T5 只规定了第二台 runner 必须异构，没有写 PASS 条件（verdict 一致？可以容忍哪些差异？）。
2. 谁、以什么事件、在哪里宣告 Product Freeze，没有写。L1-REVIEW 的 PASS 绑定 exact PRD blob，而 L1-CAL/PREV/ADOPT 在 L1-REVIEW 之后执行；如果它们的结果需要修改 PRD，是否需要 delta re-review 没有规定。
3. L1-ADOPT 的 5 名参与者是否必须来自项目/作者组织之外、由谁招募，没有规定。按现状，内部或友好人士即可满足 3/5。

**Required change**：

- T5 PASS 规定为 "各 fixture 的 verdict 一致，任何不一致按 REFUTED 或 UNKNOWN 处理"。
- 规定 Freeze 记录（例如在 PRD 仓库提交 `PRODUCT_FREEZE.md`，绑定 exact blob 并列出各 L1 gate 的证据引用），并规定 L1 结果导致 PRD 变化时必须做 delta re-review。
- L1-ADOPT 参与者须为外部人员，并预注册招募渠道。

### P2-6 — L1 可执行研究与 ADS 生命周期的衔接只靠 PRD 自定义

**Location**：§16；ADS `standards/DEVELOPMENT_WORKFLOW.md` Stage 1/2.2，`prompts/L1_PRODUCT_EVIDENCE.md`。
**Actual**：生命周期顺序（L1 → Freeze → L2 → 实现 → T gates）与 ADS 一致，r4 P1-8 的死锁已解除。但 ADS 中的可执行 Research Demo 是 **L2** 概念（Stage 2.2，带 E1–E3 证据强度、exact SHA、What was NOT proven 等硬规则）。L1-CAL/PREV 需要的可执行 detector 在 ADS 中没有对应的 L1 载体，§16 自定义了一套字段，但缺少 ADS Research Demo 的几项硬规则：被测边界必须真实、negative evidence、exact SHA 绑定、Evidence Strength。
**Required change**：在 §16 中声明 L1 研究 Issue 沿用 ADS Research Demo 的硬规则（引用 `standards/ARCHITECTURE_RESEARCH_DEMO_STANDARD.md` 对应条款），或者通过 PROJECT_OVERRIDES 正式登记该扩展。

---

## 5. P3

- **P3-1 — 交互性能只给出 warm-path 预算（§30）。** ≤1 s 任务 "added warm-path p95 ≤ 250 ms"，但 §8.2 每次调用都需要 "fresh writable output directory"，并且需要 environment preparation。对交互式 Agent，cold/first-call 路径的占比未知，也没有预算或报告要求（r4 §27 至少写了 "Cold-start results are reported"，r5 连报告要求也删了）。建议恢复 cold-path 报告，并说明 warm-path 的前提（池化或复用）是否与 "fresh" 实例绑定兼容。
- **P3-2 — "Branching gate"（§30、§31）不在 §36 的映射表里。** 性能 branch 失败时 Gate 状态是什么（FAIL？NOT_APPLICABLE for interactive positioning？）没有说明。建议在 §36 增加一行。

---

## 6. 审核目标逐项结论

### 6.1 Issue #2 的九个审核目标

| # | 目标 | 结论 | Finding |
|---|---|---|---|
| 1 | 同一 enforcing runtime 下 Evidence 价值命题是否自洽 | **论题层自洽，证伪层不自洽**：C 臂与 §12 冲突；REFUTED 层按构造必过；Channel 1 无规则；T2 无 PASS 判据，FAIL 无后果；Channel 2 不可测 | P0-1 |
| 2 | L1-PREV 是否数学可达、fail-closed、检测已校准、无 optional stopping | **数学可达且 FAIL 方向 fail-closed**（computed，见 P1-2）；**校准只覆盖灵敏度**；单位/估计量/UNKNOWN 处理未冻结；跨版本重跑规则自相矛盾 | P1-2 |
| 3 | REFUTED 棘轮能否被身份变更、scope 收窄、lineage 重置、退役绕过 | **能**：兼容性谓词未定义（template/invocation 微调可绕过）；guard 可以对单个 fixture 过拟合；lineage 归属不可判定，adapter lineage 重置会丢失反例；退役和拒绝外部 refutation 都可以自批。identity 变更本身已被 ratchet 覆盖 ✔ | P1-3 |
| 4 | content-addressed copy-in + 依赖闭包 + 强制解释能否使有界 TOCTOU 主张成立 | **对被绑定对象成立** ✔；缺不可强制时的回退规则、DecisionRecord 时效、store 不可变性 | P2-2 |
| 5 | Template + InstanceBindings 是否消除生产与证据的匹配歧义 | **部分消除**：clock、/in、/out 已清楚 ✔；CPU/kernel 的实际成员未绑定，enforcer 有效性因此无法匹配 | P1-4 |
| 6 | threat model 是否足够明确（恶意/测试感知 Provider、trusted runner） | **trusted runner/insider 明确 OUT** ✔；恶意 Provider "PARTIALLY" 未拆分：隔离强度、输出通道外泄、time-bomb、held-out 规模都没有写 | P1-5 |
| 7 | 生命周期是否有效 | **顺序有效，与 ADS Stage 1→2 一致** ✔（r4 P1-8 关闭）；缺 Freeze 记录权威与 re-review 规则，L1 可执行研究的载体是 PRD 自定义的 | P2-5, P2-6 |
| 8 | Gate 状态与 disposition 是否符合 pinned ADS 枚举 | **Gate 状态基本符合**（§36 表、T 系列 ✔）；§12 与 §36 矛盾；"P1 defer" 与 ADS P0/P1 语义冲突；disposition 文件使用的是非 ADS 词汇 | P1-1, P2-1, P2-3, P3-2 |
| 9 | r3/r4 findings 与 author disposition 在 GitHub 上是否完全可审计 | **r4：可审计** ✔（Issue #1 评论与 review 文件逐字一致）；**r3：内容已在 GitHub，来源与审核对象不可审计**；r4→r5 存在未披露删除 | P2-3, P2-4 |

### 6.2 前序 findings 在 r5 中的独立裁决

r4（Issue #1 REVIEW_RESULT，P0=1/P1=8/P2=7/P3=1）：

| r4 finding | r5 位置 | 本轮裁决 |
|---|---|---|
| P0-1 价值与 enforcement 语义冲突 | §1, §2, §18, §24 | **论题层 CLOSED；残余缺陷由新的 R5 P0-1 承接**（证伪工具） |
| P1-1 r3 证据损坏 / 缺 disposition | r3-review, r3-disposition | 内容层 CLOSED；来源不可审计 → R5 P2-3 |
| P1-2 B0 数学与校准 | §17, §18 | 部分 CLOSED（可达性、false-safe only、三值规则、扩样上限 ✔）；残余 → R5 P1-2 |
| P1-3 REFUTED 绕过 / 永久误伤 | §11 | 部分 CLOSED（去除时间序、可判定 overlap 骨架、棘轮、退役、pending replay ✔）；残余 → R5 P1-3 |
| P1-4 TOCTOU / parser differential | §9, §13 | CLOSED（有界主张成立）；残余 → R5 P2-2 |
| P1-5 环境模板/实例 | §8 | 部分 CLOSED；残余 → R5 P1-4 |
| P1-6 缺 threat model | §15 | 部分 CLOSED；残余 → R5 P1-5 |
| P1-7 Gate closure / 状态 / 预注册 | §22, §34, §36 | 大部分 CLOSED；残余 → R5 P0-1(T2 判据/后果)、P1-1、P1-2(5)、P2-1、P2-5(1) |
| P1-8 生命周期死锁 | §16, §21, §22 | **CLOSED**；P2 级残余 → R5 P2-5(2)、P2-6 |
| P2-1 短调用性能 | §30 | CLOSED（≤1 s / 250 ms）；cold-path → R5 P3-1 |
| P2-2 异构重放可被规避 | §27 | CLOSED；PASS 判据缺失 → R5 P2-5(1) |
| P2-3 重加权 / 预算 | §18, §24 | CLOSED |
| P2-4 C/D shell 绕过 | §24 | CLOSED |
| P2-5 非 trusted REFUTED 被忽略 | §11 | CLOSED；自批拒绝 → R5 P1-3(4) |
| P2-6 标准未 pin | `.dev-standard/VERSION` | **CLOSED**（已核实 repo/version/revision） |
| P2-7 B1 teach-to-test | §23 | CLOSED |
| P3-1 I3 / 命名 | 全文 | CLOSED（r5 中无 I3，DecisionRecord 命名一致） |

r3 中 disposition 标为 "AUTHOR_RESPONSE PRESENT"、但尚无 successor 裁决的三项：

| r3 finding | 本轮裁决 |
|---|---|
| P1-2 UNVERIFIED_ESCAPE 授权与计量 | CLOSED（r5 §14） |
| P1-5 blind mutation | CLOSED（r5 §26：独立性、commit-reveal、≥50% 真实回归、报告 CI） |
| P1-7 第三方信任 | CLOSED（r5 §28：FIRST_PARTY / consumer-replayed，publisher 签名不能授权） |

r3 的 P2-3（output trust）：r4 曾关闭，**r5 删除了相关条款，因此重新打开** → R5 P1-5 / P2-4。

---

## 7. Terminal

```text
SUCCESSOR_ADVERSARIAL_REVIEW_r5 (context-fresh) = FAIL
L1-REVIEW = FAIL
REVIEWED = kaicreator-mm/app8@1f9c2ab79ee4000dc4481142a7535ae8db9a5b33
           docs/product/prd-v0.1-r5.md blob 5d8ff030ec3aa0694f01f61ee4372fd01f013433
STANDARD = kaicreator-mm/ai-development-standard@7929012f36a2202dcc2edc7a414b8163adc7afbd (4.9.0)
BASELINE_RECHECK_BEFORE_PUBLISH = MATCH (no drift)
P0 = 1   P1 = 5   P2 = 6   P3 = 2
FREEZE_TERMINAL (Issue #2: P0=0 AND (P1=0 OR all P1 independently accepted-deferred)) = NOT MET
  - P0 = 1 → not met under any reading
  - no P1 carries an independently accepted defer disposition; additionally, per P1-1, a defer path for P1 is not ADS-compliant
R4_CLOSURE = mostly CLOSED/PARTIAL (see §6.2); residuals carried as R5 findings
R3_CLOSURE = content auditable; provenance NOT VERIFIED
PRODUCT_DIRECTION = CONDITIONAL_GO (not reassessed as a kill; no finding falsifies the direction)
PRODUCT_FREEZE = NO
L2_READY = NO
NEXT = PRD v0.1-r6 (+ delta record of all r4→r5→r6 removals) → context-fresh successor review
```

**Remaining risk**：如果 r6 只为 T2 补一张 PASS 阈值表，却不规定 D 臂 evidence 必须盲生成、也不写出 C 臂规则，T2 仍会在 REFUTED 层按构造通过，而 benign 层的结论取决于对 §12 的读法。这样，产品论题的检验在冻结后会继续失真。

**Recommended next workflow state**：`changes-requested`。本 Issue 只授权审核；本结果不授权实现、L2 或 technical MVP。

---

## 附录 A — 派发提示词（逐字）

派发方 `claude-code:windows-01`（非 context-fresh）。以下为本会话收到的完整派发提示词，逐字照录：

````text
你是 kaicreator-mm/app8 的 context-fresh、READ-ONLY Independent Reviewer。

任务：执行 GitHub Issue kaicreator-mm/app8#2，按 Issue 中的固定要求完成审核，并把 terminal 回写到该 Issue。

Issue 是唯一的 work contract。先用 `gh issue view 2 --repo kaicreator-mm/app8` 读取当前 Issue；scope、baseline SHA/blob、review targets、独立性要求、freeze terminal 规则，都以 Issue 当前内容为准。本提示词不重复、也不补充这些内容。

身份（写入你发布的每一个 ai-dev:event:v2 事件）：
- actor_role: reviewer
- operator_kind: claude-code
- operator_id: "claude-code:windows-01-fresh-subagent"
- session_ref: "app8-prd-r5-fresh-review-20261007"
- transport_actor: "github:kaicreator-mm"
- dispatched_by: "claude-code:windows-01"。该 operator 不满足 context-fresh。它只负责派发本任务，没有向你提供任何审核结论；请在 REVIEW_RESULT 中原样披露这一事实，并逐字附上本派发提示词，供审计。

事实源与纪律：
- 只把 GitHub durable state 当作事实源，用 `gh` / `gh api` 读取：app8 仓库在 Issue 指定的 exact SHA/blob 上的内容、Issue #1/#2、以及 app8 `.dev-standard/VERSION` 所 pin 的 kaicreator-mm/ai-development-standard exact revision（先读它的 AGENTS.md、prompts/independent-review-bootstrap.md、templates/agent-event-comment.md，再读审核所需的其它规范）。
- 不要读取本机 C:\xDev\kAiCreator\app8 下的任何文件，也不要读取本机其它 app8 相关文件。那些不是 GitHub durable state，可能出自非独立 operator。
- READ_ONLY：不修改任何仓库文件，不 push，不建分支或 PR，不改 Issue body/labels/state。唯一允许的写操作是在 Issue #2 上发评论：先发 ROLE_CLAIMED，审核完成后发 REVIEW_RESULT。
- 发布 REVIEW_RESULT 前，重新确认 main 上的 HEAD SHA 和 PRD blob 与 Issue 的 baseline 一致。如果不一致，按规范处理（记录 drift，不要把结论挪到别的 SHA 上）。
- 如果你判断自己不满足 Issue 的独立性要求，或者无法完成审核，按 Issue 规定回写 BLOCKED 并说明原因。
- Gate 状态只用规范允许的枚举。Finding 使用 P0–P3，每条给出 Location / Expected / Actual / Required change。无法确定的事实标为 UNKNOWN / NOT VERIFIED，不要猜测。
- 临时文件放在 C:\Users\15549\AppData\Local\Temp\claude\C--xDev-kAiCreator-app8\2ff8023a-0284-4f5d-8f40-15d3db6955a2\scratchpad\fresh-r5\ 下。用 Bash 工具执行命令（Git Bash）；gh 已登录。评论正文先写入文件，再用 `gh issue comment 2 --repo kaicreator-mm/app8 --body-file <file>` 发布。单条评论不超过 60000 字符，超出时拆成编号的多条。

完成后，回复我：两条评论的 URL、terminal 摘要（P0/P1/P2/P3 计数、status、freeze 判定），以及最关键的 3–5 条 finding 的一句话概要。
````
