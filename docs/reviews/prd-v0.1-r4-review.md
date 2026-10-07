<!-- ai-dev:event:v2 -->
```yaml
schema: ai-dev/event-v2
event: REVIEW_RESULT
actor_role: reviewer
operator_kind: claude-code
operator_id: "claude-code:windows-01"
session_ref: "app8-prd-r4-successor-review-20261007"
transport_actor: "github:kaicreator-mm"
task: "#1"
sha: "322e0ed5a34cc6369e01c461a7ba3dc8258f2199"
tree: "444d348a21fa35c642df2ff11df26b6a8ef8068d"
subject: "docs/product/prd-v0.1-r4.md @ blob f0834396694f2e366116786aafeb1bd46702a4bc"
review_kind: successor-adversarial-product-review
review_policy: required        # Issue #1: Freeze/L2 gated on this terminal
mode: READ_ONLY
status: FAIL
findings:
  p0: 1
  p1: 8
  p2: 7
  p3: 1
product_direction: CONDITIONAL_GO   # unchanged; not a kill
product_freeze: NO
l2_ready: NO
local_validation_required: false
next_state: changes-requested
```

# PRD v0.1-r4 Successor Adversarial Review — FAIL (P0=1 / P1=8 / P2=7 / P3=1)

## 0. 审核身份、事实源与独立性声明

- **事实源**：仅 GitHub live state —— `kaicreator-mm/app8@322e0ed`（tree `444d348`）、Issue #1 body、`docs/product/prd-v0.1-r4.md`（blob `f083439`）、`README.md`；流程依据 `kaicreator-mm/ai-development-standard@7929012`（AGENTS.md、`prompts/independent-review-bootstrap.md`、`templates/agent-event-comment.md`、4.0.0 severity semantics）。本地文件、聊天记录不作为事实。
- **独立性**：本 Reviewer 未参与 r4 的撰写。**需如实披露**：同一 `claude-code:windows-01` operator 此前在本地（未进入 GitHub）产出过 r1/r3 审核文本，因此本会话**不是 fresh context**。本轮结论只依据上述 GitHub 内容，但若项目把 "全新" 解释为 context-fresh，需要另起一个无历史的 Reviewer 做确认审核。
- **只读**：未修改 PRD、README 或 docs；只向本 Issue 写入事件。

## 1. 总判

r4 的工程化程度显著提升：ExecutionContext、DecisionRecord、REFUTED dominance、FIRST_PARTY trust、E0-prevalence、聚类统计、一次扩样规则、Gate 编号，均已成文。
但本轮发现 **1 个 P0**，它不是"漏写"，而是 r4 两处修复**互相抵消**：

> §9 规定安全 ALLOW 必须依赖 ENFORCED guarantee（修复 r3 的 scope 问题）；
> §14/§16 又用"第三方声明错误的流行率"来度量 Evidence 相对 static policy 的安全增量（修复 r3 的效应量问题）。
> 在 §9 之下，声明真假已不影响安全 ALLOW，于是 C vs D 的安全差异要么趋近于 0，要么只能靠"C 不加 enforcer"制造出来——后者又把 enforcement 混进了被测变量。

此外有 8 个 P1，主要集中在：kill rule 数学上不可触发、REFUTED dominance 按时间而非覆盖范围判定、TOCTOU 修复非原子、环境身份不区分模板与实例、缺 threat model、Gate 状态不符合标准枚举，以及 "Technical MVP 先于 Product Freeze" 造成的生命周期死锁。

---

## 2. P0

### P0-1 — §9 的 "arbitrary runtime inputs" 构成两难，两种读法都会破坏一项核心主张

**Location**：§9（"UPSTREAM_OBSERVED alone is insufficient for security-required ALLOW on arbitrary runtime inputs"；条件 7、8），§1，§6，§14，§16，§18，§35 K2

**Actual**：限定词 "on arbitrary runtime inputs" 没有定义。经过 deterministic input-domain guard 的输入，算不算 "arbitrary"？

- **读法 A：经过 guard 的输入不算 arbitrary**，因此 UPSTREAM_OBSERVED 可以单独支撑 ALLOW。
  但 guard 定义的 domain（例如"合法 mp4"）仍是无限集，而 §6 明确说 VERIFIED_IN_SCOPE "never a universal statement about arbitrary future input"。用有限 fixture 的观察去担保无限 domain，正是前序版本要关闭的 scope 漏洞（polyglot、parser differential、条件触发行为）。§1 的 "falsifiable, closed-scope" 主张在读法 A 下失效。
- **读法 B：任何未来输入都算 arbitrary**，因此安全 ALLOW 永远需要 ENFORCED + enforcer evidence。
  这时 provider 的声明是真是假，对 D 臂的安全 ALLOW 不再起作用（D 不信声明，只信 enforcer）。对每个属性：
  - **runtime 可强制的属性**（网络、挂载外写入、进程逃逸）：只要 C 臂运行在同一 enforcing runtime 里，C 放行的"虚假声明 provider"在执行时同样被拦下 → **unsafe execution 差异≈0**，K2 将被"正确地"触发，即使 Evidence 有真实价值；
    如果让 C 臂不带 enforcer，C vs D 就重新混入 "enforcement 有没有" 这个变量 —— r2 时代的多变量混杂问题回来了。
  - **runtime 不可强制的属性**（在允许写入的目录内的破坏性操作、经允许通道的数据外泄、输出语义正确性）：按读法 B 永远无法 ALLOW。于是 Evidence 最可能独占价值的那类属性，被 §9 直接排除在安全 ALLOW 之外。
  - Evidence 在 D 中剩下的安全作用，只有条件 6（dominating REFUTED → DENY）。它把 "被 runtime 拦截的违规尝试" 变成 "执行前 DENY"。这是真实价值（早发现、供应商问责、避免功能性失败），**但不是 §16/§17 主指标所度量的 risk reduction**。

**Expected**：PRD 的安全模型（§9）、价值命题（§1）与 E0 主指标（§16–§18）三者必须一致。被测变量必须是 "executable evidence"，而不是 "enforcement 的有无"。

**Required change**（最小修订，不扩大范围）：

1. **明确选定一种读法。** 建议选读法 B：security-required 属性只能经由 first-party ENFORCED + 本 provider/invocation 类的 enforcer-validity evidence 来 ALLOW。
   对 runtime 不可强制的属性，要么明确排除在 MVP 安全范围之外，要么定义一个显式的残余风险路径（例如 `UPSTREAM_OBSERVED_ACCEPTED_RISK`）：与 UNVERIFIED_ESCAPE 同级授权，绝不静默，并计入 E0 违规统计。
2. **重写 §1 的价值通道，并据此确定 E0 主指标**。Evidence 在读法 B 下的增量价值应拆为：
   (a) REFUTED → 执行前 DENY / 供应商问责；
   (b) enforcer-fit：provider 在 enforcer 下能正常工作，不被误拒，allowlist 最小化；
   (c) 非安全可靠性：输出契约、错误语义、取消。
   E0 的主指标相应改为：contained-violation attempts、pre-execution detection rate、benign availability / false denial、functional reliability。
3. **§16 写明 C 臂与 D 臂运行在同一 enforcing runtime 中**，唯一差异是 Admission 读的是声明还是 executable evidence。
4. **E0-prevalence 重新定位为 L1 problem evidence**：它说明 "现状（信任声明）有多糟"，但不再作为 enforced 属性上 C vs D 效应量的来源。

> 本 P0 不否定产品方向。它要求 r5 把 "Evidence 在 enforcement 已存在时还能增加什么" 写成可证伪的命题。当前文本把这个问题隐藏在一个未定义的限定词里。

---

## 3. P1

### P1-1 — 前序审核证据在 GitHub 上不可用，r3 的处置无法审计

**Location**：`docs/reviews/prd-v0.1-r3-review.md`（commit `322e0ed`，blob `3fff99e`，155 bytes）；README "Documents"；PRD §38；Issue #1 "Predecessor review"

**Actual**：该文件全部内容是一段工具错误文本（"The requested file reference is not currently visible. Use files.search …"），不是审核正文。commit 信息却写着 "preserve PRD r3 adversarial review evidence"。PRD §38 声称 `P0_r3 = ADDRESSED_IN_r4 / P1_r3 = ADDRESSED_IN_r4`，但没有逐条处置表。

**Expected**：按标准，GitHub durable state 是唯一事实源；Freeze gate（§32）要求 "every P1 either closed or carrying an explicit accepted defer disposition"。这只有在前序 findings 与处置都在 GitHub 上时才可审计。

**Required change**：用 r3 审核的真实正文替换占位文件（或标记为 `EVIDENCE_LOST` 并说明来源）；新增 `docs/reviews/prd-v0.1-r3-disposition.md`，逐条记录 finding → disposition → r4 §ref。
**本轮对 r3 closure 的判定：`NOT VERIFIED`**。

### P1-2 — B0 的判定规则：kill 在最小样本下不可触发，并且"因无知而 PASS"

**Location**：§14，§29 B0，§35 K1

**Actual**：

1. **数学上不可触发。** 规则是 "95% CI 上界 < 5% → PREVALENCE_TOO_LOW"，最小样本为 "at least 30"。即使 30 个样本中观察到 0 个，Wilson 上界也是 3.84/(30+3.84) ≈ **11.3%**。要让 0 事件时上界 < 5%，需要 **n ≥ 73**。在声明的最小样本下，K1 永远不会触发 —— r3 指出的 "E0 无法失败" 在 B0 上重现。
2. **B0 PASS 没有定义。** 文本只定义了 kill。CI 跨过阈值时（例如 1/30，CI 约 0.6%–17%），B0 等于 "未被证明太低"，在实际操作中会被当作 PASS 继续推进 —— 不确定时放行，与全文 fail-closed 的立场相反。
3. **分析单位与 materiality 未冻结。** 不清楚统计的是 per-tool 还是 per-claim，也没有定义什么算 "materially false"，这给结果出来后的事后分类留了空间。
4. **方向未区分（向上偏差）。** 与安全准入相关的是 **false-safe** 声明（声称只读/无副作用，实际不是）。false-unsafe（过度保守，例如 MCP `destructiveHint` 默认为 true）只会造成误拒，不会造成不安全的放行。混在一起统计会抬高流行率。
5. **测量工具未校准（向下偏差）。** B0 用 conformance check 测量 REFUTED，而 suite sensitivity（B4）排在 B0 之后才验证。用灵敏度未知的工具得到 "流行率很低"，可能是工具弱，而不是世界干净，最终造成**错误 kill**。
6. **抽样框架。** 对 catalog 均匀抽样会被长尾业余项目主导，与目标用户真正会准入的工具总体不同。"where technically feasible" 会系统性排除需要凭证的远端 SaaS 型 server。

**Required change**：

- 把 B0 写成三值规则：上界 < T → KILL；下界 ≥ T_min → PASS；否则 INCONCLUSIVE，并允许一次预注册扩样。
- 用 T 反推最小 n（若 T = 5%,0 事件时 n ≥ 73）。
- 统计单位冻结为 per-claim 和 per-tool 两者都报告，只计 false-safe。
- 在 B0 之前做 planted-positive 校准（已知违规的 provider），报告检出灵敏度；只有灵敏度 ≥ 预注册值时 kill 才有效。
- 冻结抽样权重（uniform 与 usage-weighted 两者都报告），UNKNOWN 按最好/最坏两端分别给出界。

### P1-3 — REFUTED dominance 按 "时间" 而不是 "覆盖" 定义，可以被绕过，也可能永久误伤

**Location**：§7，§9 条件 5/6，§34

**Actual**：

1. **只写了 "dominates older VERIFIED"。** 用不包含反例 fixture 的更窄 corpus 重新跑一次，产生一份更新的 VERIFIED，就能盖过旧的 REFUTED → evidence shopping 依然成立。
2. **身份微调绕过。** dominance 只在 "a given Provider identity" 之内生效。对 adapter 做任意无关改动 → identity 改变 → 旧 REFUTED 不再适用；再用不含反例 fixture 的旧 lineage 重跑 → VERIFIED。§7 没有要求反例 fixture 自动进入最低 lineage。
3. **"overlapping assertion/scope" 未定义。** scope 是多维的（input domain × environment × invocation）。没有 domain 代数，overlap 无法判定：判 fail-closed 就会永久误伤（Issue 问题 3 担心的情况），判 fail-open 就允许挑选证据。
4. **没有撤销或申诉路径**：harness 缺陷、非法 fixture（不在 domain 内）导致的 REFUTED 怎么退役，没有规定。

**Required change**：

- 去掉 "older"：任何 trusted REFUTED 支配所有 overlapping 的 VERIFIED，与时间先后无关。
- **棘轮规则**：每个 trusted REFUTED 的反例 fixture 自动加入该 provider 谱系（同一 source/adapter lineage，跨 identity）的 policy 最低 lineage。新 identity 必须对它重新测试。
- **可判定的 overlap**：`overlap(REFUTED r, scope s) := guard_s.accepts(r.fixture) ∧ env/invocation 兼容`。用新 scope 自己的确定性 guard 去分类反例 fixture —— 收窄 input domain 以排除反例，是合法的恢复路径，不会被永久误伤。
- 定义 `REFUTATION_RETIRED`：只能由 trusted 流程以 "harness defect" 或 "fixture out of domain" 为理由执行，并留下记录。

### P1-4 — "closes admit/exec TOCTOU" 是过度声明：重检与执行不是原子的，guard 与 provider 存在 parser differential

**Location**：§8，§10，§19 条件 4/5

**Actual**：

1. "re-check these digests immediately before execution" 是 check-then-use。如果 artifact、adapter 或输入是从可变路径读取的，校验与 exec 之间仍有窗口。
2. DecisionRecord 绑定的是 `input descriptor`（分类结果），**不是输入内容的 digest**。分类之后替换文件，或者输入间接引用其它文件（播放列表、include、sidecar），都不在绑定范围内。
3. **Parser differential。** guard 按自己的解析得出 "mp4"，provider 按自己的格式探测逻辑可能识别为别的格式（polyglot）。除非 invocation **强制使用 guard 的解释**（例如固定 demuxer 和协议白名单），否则 guard 的分类并不约束 provider 的实际行为。
4. guard 本身是不是 "enforcer"、是否必须接受 B4 的 mutation 测试，文中没有说明。

**Required change**：

- 执行时只使用按内容寻址的不可变副本（输入 copy-in 并以只读方式挂载；artifact/adapter 从 content-addressed store 执行），实现 check-and-use 同一对象。
- DecisionRecord 增加 `input_content_digest`；间接引用在 sandbox 内被禁止或被一并 copy-in。
- guard 的分类结果必须编码进 invocation（强制解释）。
- guard 归类为 ADAPTER_ENFORCED，纳入 E3 的 dev/blind mutation（包括 polyglot 案例）。
- 把措辞改为 "closes TOCTOU for content-addressed inputs within the reference path"。

### P1-5 — 环境身份不区分 "模板" 与 "实例"，§9 条件 2 要么永远不满足，要么没有定义

**Location**：§5，§6，§9 条件 2，§10，§20

**Actual**：CLOSED_SCOPE 要绑定 "explicit mount manifest"、"clock policy" 等。生产调用的输入挂载、输出目录、时钟值每次都不同。如果 environment_digest 包含这些，生产调用永远无法匹配 evidence 环境 → 全部 UNKNOWN；如果不包含，那么哪些部分可以变、怎么变，文中没有定义 —— 实现者会各自决定。时钟同样如此：冻结时钟在生产中不可行，真实时钟则让 evidence 无法覆盖未来的时间点。

**Required change**：定义 `environment_template_digest`（不可变部分）+ `instance_bindings`（每次调用允许变化的维度及其类型约束，例如 "仅一个只读输入挂载，位于 /in"、"一个可写输出目录"、"时钟 = 实时，偏移量记录"）。Admission 匹配 template，并校验 instance_bindings 落在 schema 之内。依赖时间的行为明确写为 VERIFIED_IN_SCOPE 不覆盖，属于安全的部分交给 enforcer。

### P1-6 — 缺少 threat model，安全机制无法对齐到攻击者

**Location**：全文（§5、§7、§9、§13、§19、§23 各自隐含不同的攻击者）

**Actual**：E0-prevalence 针对的是 "粗心的发布者"；E1 针对 "宿主状态泄漏"；FIRST_PARTY 针对 "伪造的第三方 evidence"；input guard 针对 "恶意输入作者"。但从未说明 MVP 防谁、不防谁。关键的未覆盖情形：**恶意或被攻破的 provider 具备测试感知能力** —— 公开的、按内容寻址的、偏合成的 fixture corpus（§28）可以被 provider 识别并特判，于是 UPSTREAM_OBSERVED 对这类对手完全失效。first-party insider 和被攻破的 runner 也没有说明是否在范围内。

**Required change**：新增 Threat Model 一节，按 adversary 列出：粗心发布者、恶意发布者 / 测试感知 provider、恶意输入、被 prompt 注入的 Agent、被攻破的 runner / insider。每一行写明对应的机制和 gate，以及 "not defended in MVP" 的条目。对安全相关的 evidence，要求使用私有 held-out fixture，或每次运行用随机种子生成并记录。

### P1-7 — Gate closure 仍不完整，并且与标准的 Gate 状态枚举冲突

**Location**：§14，§17，§18，§19，§23，§25，§29，§30，§31，§35；标准 AGENTS.md "Gate 只能使用 PASS / FAIL / BLOCKED / NOT_RUN / NOT_APPLICABLE"

| # | 问题 |
|---|---|
| a | `PREVALENCE_TOO_LOW`、`NOT_DEMONSTRATED`、`INCONCLUSIVE`、`REJECTED/CONTINUES` 都不是标准的 Gate 状态，也没有映射规则 |
| b | §17 中扩样后仍 INCONCLUSIVE → `E0 = NOT_DEMONSTRATED`;§35 K2 只在 "B2 **fails**" 时触发。NOT_DEMONSTRATED 算不算 FAIL?是 kill,还是无限期悬置? |
| c | §17 的 B2 PASS "CI ... exclude the preregistered minimum meaningful effect threshold" 没有写方向。应写成：下界 > MME → PASS;上界 < MME → FAIL;其余 → INCONCLUSIVE |
| d | §23 说 B4 "Blocking **for security admission**",§25 说 B6 "Blocking **for the security-admission claim**",§29/§30 又把两者都列为 Technical MVP 的必过项。B4 或 B6 失败时，是 Technical MVP FAIL,还是只撤回安全主张? |
| e | §19 E1 删掉了 r3 的最低扰动数量（现在只有 "at least half ... by independent reviewer",总数没有下限）;E1 reviewer 的独立性条件也没有定义（E3 有定义） |
| f | **借重新版本化实现 optional stopping**:§14 "threshold may only change in a new preregistered study version",§31 "cohort protocol changes → new discovery version"。负面结果出来后开一个新版本重来，没有任何限制 |
| g | "preregistered" 没有可审计的载体：预注册必须是数据采集前的 GitHub commit 或 Issue(带时间戳和 hash),并由独立 reviewer 确认 |
| h | §30 "An independent reviewer records the terminal":没有定义独立性判据（标准要求 operator_id/session_ref 可审计地区分） |

**Required change**：增加一张 Gate 结果表：每个 B/R gate → 结果 → 映射到标准状态 → 处置 → 触发的 K。规定 NOT_DEMONSTRATED ≡ FAIL(用于 K2);规定 B4/B6 失败的处置;恢复 E1 的最低扰动数;任何新 study/cohort 版本都不能覆盖已有的负面结果，必须同时报告所有版本，并经独立审核批准;预注册必须落在 GitHub。

### P1-8 — 生命周期倒置:"Technical MVP PASS 先于 Product Freeze" 与当前授权形成死锁

**Location**：§30，§32，Issue #1 "Scope control"，标准 AGENTS.md(PRD Freeze → L2 → 实现;Research Demo 属于 L2 evidence)

**Actual**：§32 要求先 Technical MVP PASS(B0–B6:reference runner、PID namespace、attestation、四臂 Agent 实验……)才能 Product Freeze,而 L2 Architecture 在 Freeze 之后。Issue #1 又明确 "No implementation expansion ... is authorized"。结果是，满足 Freeze 所需的实现工作没有任何授权通道，也没有架构依据。即便本审核达到 P0 = 0,Freeze 仍然不可达。

**Expected**：产品层验证实验要么属于 L1 Product Evidence(Freeze 之前，以有边界的 research demo 形式授权),要么属于 Freeze 之后的 v0.1 release gates。

**Required change**：

- 把 B0(以及 adoption)归入 **L1 evidence**,作为 PRD Freeze 的前提;
- 把 B1–B6 改为 **v0.1 Technical MVP release gates**,在 Freeze → L2 → 实现之后执行;
- 如果坚持部分 B gate 在 Freeze 前执行，必须为其开设独立的 research-demo Issue,写明允许的范围与 "What was NOT proven"。

---

## 4. P2

- **P2-1 — 性能预算漏掉了最主要的交互场景（§27）。** 只有 "raw ≥ 5 s" 的任务有 overhead 预算;典型的交互式调用（如 probe,约百毫秒）没有预算，而 1 s 的 warm prep 对它们是 10 倍开销。输入 hashing / copy-in(P1-4 的修复)、guard 解析、在线吊销检查也都没有计入。50 ms 的 Admission p95 应写明使用离线吊销快照。
- **P2-2 — 异构重放可以通过 "约束" 规避（§20）。** 把 CPU、内核、时钟声明为精确值，第二台 runner 就与第一台完全相同。要求：若约束的是一个类别（例如 x86-64-v3),第二台 runner 必须在**类别内部**取不同成员。
- **P2-3 — 重加权的可迁移性与可行性（§16、§17）。** 在 catalog 工具总体上测得的流行率，不能直接迁移到 benchmark 中的 provider。流行率低时，重加权后的有效样本极小，按功效分析需要的 N 可能根本不可行。应预注册一个预算上限：超过上限时直接判定结果（视为 NOT_DEMONSTRATED,即 FAIL),而不是空转。
- **P2-4 — 各臂的工具可用性没有定义（§16）。** C/D 臂里 Agent 有没有 shell?如果有，直接调用 provider 就绕过了 Admission,这是否计入违规?§12 只覆盖了 escape。
- **P2-5 — 非 trusted 的 REFUTED 被完全忽略（§7、§13）。** 验证一个反例的成本很低（重放该 fixture)。外部报告的 REFUTED 至少应触发 `UNKNOWN: REFUTATION_PENDING_REPLAY` 并进行强制重放，而不是被无视。
- **P2-6 — 标准版本没有 pin。** 仓库没有 `.dev-standard/VERSION`;README 写的是 "follows the current ai-development-standard",这正是标准明确禁止的 "隐式读取最新 main"。
- **P2-7 — B1 的用例由实现团队自己冻结（§15）。** 在自己写的用例上达到 100% 是可以 teach-to-the-test 的。建议至少一半用例由独立 reviewer 编写。

## 5. P3

- **P3-1** — I3 "future provider-distribution sampling" 没有任何定义;§2 的 "Bound Execution Decision Record" 与 §10 的 "DecisionRecord" 命名不一致。

---

## 6. Issue #1 七个阻塞问题的结论

| # | 问题 | 结论 |
|---|---|---|
| 1 | E0-prevalence 是否测到真实世界的比率 | **部分**。已不由 benchmark 制造;但 kill 在 n=30 时不可触发，没有 PASS 规则，未区分 false-safe,测量工具未校准 → **P1-2**。按 P0-1,它也不再是 enforced 属性上 C vs D 效应量的正确来源 |
| 2 | Admission 绑定是否足以防止 scope mismatch / TOCTOU | **否**。重检与执行不是原子的;输入内容没有绑定;存在 guard 与 provider 的 parser differential;环境模板与实例不分 → **P1-4、P1-5** |
| 3 | REFUTED dominance 能否防 shopping 又不永久误伤 | **否**。按时间而不是覆盖判定;身份微调可以绕过;overlap 未定义;没有撤销路径 → **P1-3**(已给出可判定的 overlap 规则) |
| 4 | FIRST_PARTY / consumer replay 对 MVP 是否足够 | **对 "伪造的第三方 evidence" 足够;对测试感知的恶意 provider 和 insider 不足**,而且 threat model 缺失 → **P1-6** |
| 5 | 聚类统计、功效分析与一次扩样规则是否 closure-complete | **否**。B2 的 CI 方向未写;NOT_DEMONSTRATED 与 K2 不衔接;重新版本化可以实现 optional stopping;预注册没有载体;可行性没有上限 → **P1-7、P2-3** |
| 6 | CLOSED_SCOPE + 异构重放 + 环境身份能否支撑安全准入 | **在模板/实例拆分之前不能**;约束可以规避异构重放;并且按 P0-1,安全最终依赖的是 enforcer → **P1-5、P2-2、P0-1** |
| 7 | Blocking / Branching / Informational 是否无歧义 | **否**。状态不符合标准枚举;B4/B6 的作用范围冲突;E1 的最低扰动数被删;生命周期死锁 → **P1-7、P1-8** |

## 7. PRD §39 九个攻击目标的结论

| # | 目标 | 结论 / finding |
|---|---|---|
| 1 | prevalence 是真实比率吗 | 部分 → P1-2 |
| 2 | 抽样与 claim 选择会不会向上偏 | **会**:false-unsafe 混入统计、长尾 catalog 均匀抽样;同时有向下偏差（工具未校准）→ P1-2 |
| 3 | ExecutionContext + 绑定能否防止绕过 | 不能完全防止 → P1-4、P1-5 |
| 4 | dominance 会不会永久否决 | 当前定义下，既可能绕过，也可能永久误伤 → P1-3 |
| 5 | first-party 下还能否伪造或误导 | 可以：测试感知 provider、insider → P1-6 |
| 6 | 聚类统计能否阻止 optional stopping | 单个 study 内可以;跨 study 版本不能 → P1-7(f) |
| 7 | CLOSED_SCOPE 在 CPU / 内核 / 时间差异下是否有意义 | 时钟在模板/实例层面未定义;约束可规避异构 → P1-5、P2-2 |
| 8 | verified-path 开销与交互场景是否兼容 | 未证明;主要交互场景没有预算 → P2-1 |
| 9 | Gate 是否 closure-complete | 否 → P1-7、P1-8 |

## 8. r5 的最小修订路径

1. **先解决 P0-1**:选定 §9 的读法(建议读法 B),重写 §1 的价值通道和 E0 主指标，写明 C 与 D 运行在同一 enforcing runtime 中。
2. 修复 GitHub 上的 r3 证据，并补上逐条处置表(P1-1)。
3. B0 改为三值规则，给出 n 的推导、只计 false-safe、先做 planted-positive 校准(P1-2)。
4. REFUTED:去掉 "older"、加入棘轮规则、可判定的 overlap、撤销路径(P1-3)。
5. 执行时使用 content-addressed 不可变副本;强制 guard 的解释;guard 纳入 E3(P1-4)。
6. 环境拆为 template + instance bindings(P1-5)。
7. 新增 Threat Model 一节(P1-6)。
8. Gate 结果表映射到标准状态;禁止通过重新版本化覆盖负面结果;预注册落在 GitHub(P1-7)。
9. 生命周期：B0 与 adoption 归入 L1;B1–B6 作为 Freeze 之后的 release gates(P1-8)。

以上全部是规则层面的修订，不需要授权任何实现扩张，符合 Issue #1 的 scope control。

## 9. Terminal

```text
SUCCESSOR_ADVERSARIAL_REVIEW_r4 = FAIL
REVIEWED = kaicreator-mm/app8@322e0ed5a34cc6369e01c461a7ba3dc8258f2199
           docs/product/prd-v0.1-r4.md blob f0834396694f2e366116786aafeb1bd46702a4bc
P0 = 1   P1 = 8   P2 = 7   P3 = 1
R3_CLOSURE = NOT_VERIFIED (predecessor review evidence on GitHub is a 155-byte error placeholder)
PRODUCT_DIRECTION = CONDITIONAL_GO (unchanged)
PRODUCT_FREEZE = NO
L2_READY = NO
NEXT = PRD v0.1-r5 → successor adversarial review (context-fresh reviewer recommended)
```

Remaining risk：如果 r5 只为 §9 的限定词补上定义，却不重写 §1 的价值通道和 E0 主指标，P0-1 会以 "E0 FAIL 但原因是度量错位" 的形式在实验阶段重新出现。
