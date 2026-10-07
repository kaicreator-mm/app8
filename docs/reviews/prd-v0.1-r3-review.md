# 对抗审核 — PRD v0.1-r3 (Executable Capability Evidence)

**审核对象:** `prd-0.1-r3.md`(DRAFT_FOR_SUCCESSOR_ADVERSARIAL_REVIEW, 2026-10-07)
**前序:** `prd-0.1-r1-review.md`、`prd-0.1-r2-review.md`
**审核日期:** 2026-10-07
**审核立场:** r2 的 P0/P1 已逐条修复，本轮不重复。只攻击 r3 **新引入的结构**(四臂、CLOSED_SCOPE、fail-closed、统计规则、Gate taxonomy)本身是否成立。

---

## 0. 结论

```text
SUCCESSOR_ADVERSARIAL_REVIEW_r3 = FAIL
P0 = 2   P1 = 7   P2 = 5
PRODUCT_DIRECTION = STILL_VIABLE
PRODUCT_FREEZE = NO
L2_READY = NO
```

r3 是三版里质量最高的一版：MVP 已收敛到单一 surface,r2 要求的四臂、DISCOVERED/CLOSED 分级、fail-closed、Wilson CI、blind mutation 和 Gate 三分类都已到位，并且修得正确。

剩下的两个 P0 都不在"有没有写"的层面，而在**机制能不能自洽**的层面：

1. **E0 的效应量是实验设计参数，不是测量结果。** false declaration 的比例由团队自己决定写进 benchmark,所以 C vs D 的差距可以被造出来。E0a 更是按构造必然 PASS。
2. **Admission 看不到执行上下文。** 纯函数的输入里没有"这次调用的真实输入"和"这次执行所在的环境",所以 ALLOW 无法绑定到 Evidence 实际覆盖的 scope。r1 的 `.m3u8` 反例在 r3 下依然能拿到 ALLOW。

这两个都可以小范围修掉(见 §5),我认为 r4 能达到 `P0 = 0`。

---

## 1. 发现总表

| ID | 级别 | 位置 | 一句话 |
|---|---|---|---|
| P0-1 | P0 | §14–§24, §28 | false declaration 的流行率由实验者设定，E0 的效应量可以被构造;E0a 按构造必过 |
| P0-2 | P0 | §10, §11, §13 | Admission 不接收实际输入与执行环境，ALLOW 无法绑定到 Evidence scope |
| P1-1 | P1 | §10, §13, §54 | 调用方自选 evidence_bundle:可提交旧的 VERIFIED、隐瞒新的 REFUTED |
| P1-2 | P1 | §12, §22 | UNVERIFIED_ESCAPE 由谁授权、是否计入 E0 违规，都没定义 |
| P1-3 | P1 | §20–§23 | 统计规则忽略 episode 聚类;relative reduction 和 benign 退化只用点估计 |
| P1-4 | P1 | §8.2, §9, §26, §44 | CLOSED_SCOPE 只封住了文件/环境变量/网络，没封住时钟、CPU、内核、/proc 等环境态 |
| P1-5 | P1 | §38–§41 | blind mutation 的样本太小、来源是人造的，"独立"也没定义 |
| P1-6 | P1 | §42, §55, §59, §61, §57 | Gate closure 仍有 6 处歧义(含未分类的 gate 和未定义的 PASS) |
| P1-7 | P1 | §45–§47, §56 | 修 P0-1 必然引入第三方声明者;签名只能证明"谁签的",证明不了"跑过" |
| P2-1 | P2 | §36 | semantic retention 只算维度在不在，不算精度有没有被降级 |
| P2-2 | P2 | §7, §6 | 间歇性违规:一个 fixture 跑几次没有规定 |
| P2-3 | P2 | §48 | Output trust 标注只是给 harness 的建议，E0 也不测注入结果 |
| P2-4 | P2 | §11, §64 | verified path 必须在 hermetic 环境执行，生产路径的成本与延迟没有预算 |
| P2-5 | P2 | §35 | network / side-effect behavior 是 Evidence 断言，不是 contract 输出维度 |

---

## 2. P0

### P0-1 E0 的效应量由实验者设定，E0 无法失败

**机制**

C 与 D 唯一的差别，是 provider 的声明错误时 D 能识别出来。所以 C vs D 的效应量约等于:

```text
effect ≈ P(benchmark 中出现 false/stale declaration) × P(Evidence 能抓住它)
```

第一项完全由 benchmark 设计者决定:

- §16 **要求** benchmark 包含 "静态声明满足 policy、但 Evidence 已 REFUTE" 的案例;
- §17 直接规定 20 个 admission case 里 **8 个**是 false/stale declaration;
- §21 要求 C 臂 "≥5 unsafe/static-false-positive events",这只要放进 ≥5 个 false-declaration 任务就能满足;
- §28 的 false claim 也是 "构造" 出来的。

**后果**

- **E0a 按构造必过。** C 只读声明，必然 ALLOW 这 8 个;D 读到 REFUTED,必然 DENY。这是 Admission 函数的**单元测试**,不是价值证据。
- **E0b 的 70% relative reduction 可以通过调配比例获得。** 12 个 adversarial 任务里放多少个 false declaration,就决定了 C 臂有多少违规。
- **K1 / STOP_PLATFORM_EXPANSION 实际上不可能被触发。** 产品命题(§1)是 "Evidence 是否比 static policy 有**额外**价值",而额外价值完全取决于**真实世界中声明出错的频率**。r3 没有任何一步测量这个频率。

**更深一层 —— MVP 中的声明者就是验证者**

在 MVP 中，写 adapter、写 contract 声明、生成 Evidence 的是同一个团队。自己写的声明为什么会错?
现实中 false/stale declaration 的来源只有两类:

1. **第三方**声明者(MCP server 作者、工具发布者)—— 但 Registry 和 marketplace 都不在 MVP 内;
2. **上游版本漂移**导致声明过时 —— 这是 §42 的 Upgrade Validation,而它没有进入任何 Gate(见 P1-6)。

所以 E0 现在测量的，是一个 MVP 中并不自然存在的场景。

**修订要求**

- **新增 E0-prevalence(先于 E0a/E0b,作为最便宜的 kill 点):**
  按预注册的抽样流程(例如对某个公开 MCP registry 的快照做随机抽样)选取 ≥30 个第三方工具/MCP server,对其**已声明**的行为属性(MCP tool annotations `readOnlyHint` / `destructiveHint` / `openWorldHint`,或文档声明)跑 conformance,
  输出 `REFUTED rate + 95% CI`。若 CI 上界低于预注册阈值，直接触发 K1,不需要再做 Agent 实验。
- 同时测量 **stale** 来源:对 §42 的 major 升级，统计声明在升级后被 REFUTE 的比例。
- **E0b 中 false-declaration 任务的比例必须取自 E0-prevalence 的实测值**(或者按实测值对结果重新加权后报告),不能由团队自定。
- 把 E0a 重新定位为 **Admission correctness test**,移出 "价值证明"。
- 次要混杂:必须写明 C 臂对 "缺少声明" 采用与 D 臂对 "缺少 Evidence" **相同的 fail-closed 规则**,否则 D 可能只是凭更严格的默认值胜出，与 Evidence 内容无关。

---

### P0-2 Admission 看不到执行上下文，ALLOW 无法绑定到 scope

**证据**

§13 中的定义:

```text
Admission(provider, requested_contract, policy, evidence_bundle) → ALLOW | DENY | UNKNOWN
```

§10 的 ALLOW 条件包括 "Evidence matches required input domain"。§6 又规定 VERIFIED_IN_SCOPE 只在给定的 *input domain、fixture corpus、invocation、closed execution environment* 内成立。

但 Admission 的参数里**既没有本次调用的实际输入，也没有本次执行所在的环境**。

**攻击 a — 域外输入**

Evidence 的 scope 是 "mp4/mkv 合成 fixture",结果为 `network: VERIFIED_IN_SCOPE (UPSTREAM_OBSERVED)`,Admission 返回 ALLOW。
运行时，Agent(或攻击者控制的上游数据)传入一个本地 `.m3u8` 文件。Admission 不知道这个输入，不可能判断它在域外。
这正是 r1 P0-2 的原始反例，在 r3 下**依然拿得到 ALLOW**。

**攻击 b — 环境不一致**

Evidence 在 hermetic 镜像 X 中生成。§10 的条件检查的是 *provider identity*(§4 中没有 environment digest)以及 *freshness*,但 Admission 并不知道执行会发生在哪里。
如果 verified path 实际在宿主机、或在另一个镜像里执行，CLOSED_SCOPE 的全部努力就失效了。§11 的 "executable through verified path" 没有定义这条路径必须使用与 Evidence 相同的 environment digest。

**攻击 c — 决策与执行没有绑定(TOCTOU)**

Admission 只返回一个决策，没有说明 runner 在 exec 时是否**重新校验** artifact / adapter / config / environment 的 digest。
在 admit 与 run 之间替换二进制或配置，就绕过了全部检查。

**对产品命题的含义(r4 需要正面写出)**

对于输入不可枚举的调用(几乎所有真实调用都是如此),`UPSTREAM_OBSERVED` 永远覆盖不了运行时的实际输入。
因此 security-required 的 ALLOW 实际上**只能**建立在 `ADAPTER_ENFORCED` / `RUNTIME_ENFORCED` 之上;Evidence 在安全上的作用，是**证明这些 enforcer 真的有效**,而不是证明 upstream 的行为。
这并不削弱产品，反而让 C vs D 的比较更清晰:**"声明了有强制"对比"测过强制有效"**。但 PRD 必须明确这一点，否则读者会把 VERIFIED_IN_SCOPE 当作对任意输入的安全承诺 —— 这正是 §6 禁止的解释。

**修订要求**

- Admission 的签名改为:
  `Admission(provider, contract, policy, evidence_set, execution_context)`,
  其中 `execution_context = { environment_digest, input_descriptor, invocation_digest }`。
- 输入域判定必须由**确定性**机制给出：要么是 input-domain guard(归类为 ADAPTER_ENFORCED,本身也要接受 E3 mutation 测试),要么由 runtime 强制。
  做不到时，返回 `UNKNOWN: INPUT_DOMAIN_UNDECIDABLE`。
- Policy 规则:对 security_required 属性，**单独的 `UPSTREAM_OBSERVED` 不足以 ALLOW**,必须同时有 ENFORCED,并附带证明该 enforcer 有效的 Evidence。
- Admission 输出一个**绑定 digest 的决策记录**;runner 在 exec 前再校验一次，不一致即拒绝执行。

---

## 3. P1

### P1-1 Evidence shopping:调用方可以挑选 bundle

`evidence_bundle` 由调用方传入。设同一 provider identity 下存在两份 bundle:

- fixture corpus v1 → `VERIFIED_IN_SCOPE`
- fixture corpus v2(新增对抗样本)→ `REFUTED_IN_SCOPE`

fixtures 属于 evidence key(§54),但不属于 provider identity(§4)。因此两份 bundle 都 "matches exact Provider identity"。调用方提交 v1、不提交 v2,就能拿到 ALLOW。

**修订要求**

- Policy 必须固定**最低 suite / fixture corpus 版本**。
- **REFUTED 支配规则**:Admission 需要查询本地 evidence 存储中该 identity 的全部 bundle。只要任一 trusted bundle 为 REFUTED,结果就不得是 ALLOW,与调用方提交了什么无关。
- 由此需要一个最小的 refutation / revocation 索引(仍然只是本地文件，不违反 §51)。

### P1-2 UNVERIFIED_ESCAPE 的授权与计量

- §12 说 "上层可以显式请求"。"上层" 是 Agent 本身吗?如果 Agent 可以自行请求 escape,那么 DENY → escape → 执行 refuted provider,fail-closed 就形同虚设。
- §22 的 E0 主指标没有说明:**经由 escape 执行的 refuted / unsafe 调用是否计入** `Known-Refuted Provider Execution` 和 `Unsafe Execution Allowed`。如果不计入，D 臂可以靠 escape 把违规 "洗" 出指标。

**修订要求:** escape 的授权主体必须是 policy 或人，不能是 Agent;policy 可以禁用 escape。E0 中所有经 escape 发生的违规都计入主指标，并单独报告。

### P1-3 统计规则仍可能产生假 PASS

r3 用 Wilson CI 和最低事件数修掉了 r2 的裸比例问题，但还有三个漏洞:

1. **Episode 不独立。** 同一任务的 5 个 episode 高度相关，Wilson 却假设 iid。
   以 12 个 adversarial 任务 × 5 episode × 2 模型 = 120 个 episode 计,ICC = 0.8 时 design effect ≈ 4.2,有效样本只有约 29。CI 会被系统性低估。
   **要求:** 以任务为单位聚类(task-level cluster bootstrap 或 GLMM),或直接在任务级别计算比例;并说明按模型分层还是合并。
2. **Relative reduction ≥ 70% 没有说明用点估计还是 CI 界。** 在最低支持数下:C = 5/60,D = 1/60,点估计 80%,但 RR 的 95% CI 约为 0.02–1.66,即 reduction 在 **−66% 到 98%** 之间 —— 点估计 PASS,却没有任何证据量。
   "≥ 5 个事件" 这个下限挡不住小样本假 PASS(而且按 P0-1,这 5 个事件本身是可以构造的)。
   **要求:** 用 reduction 的 **CI 下界**做门槛，或者把事件数下限提高到使 CI 宽度可接受的水平(给出功效计算)。
3. **Benign 退化 ≤ 5pp 是一个非劣效判定。** 每臂 120 个 benign episode、成功率约 0.8 时，差值的 95% CI 半宽约 ±10pp(聚类前)。用点估计判定等于看噪声;用 CI 界判定则几乎不可能 PASS。
   **要求:** 写明非劣效检验(CI 界 vs margin),并据此倒推所需的 benign 任务数。

另外，§23 的 "Known-refuted execution rate upper 95% CI ≤ 5%":若 D 为 0 次，Wilson 上界 = 3.84/(n+3.84),需要 **n ≥ 73** 次 refuted-opportunity 才能过线。PRD 应写明分母，并确认 benchmark 能提供这么多机会。

### P1-4 CLOSED_SCOPE 没有封住环境态(回答 Target #2:没有完全消除)

§8.2 的机制完整封住了**文件系统、环境变量、配置、插件、挂载、网络**这一类状态。但在容器 / namespace 内，Provider 仍然能观察到:

- **时钟**:当前时间(只固定了 timezone)。证书过期、license 检查、"距上次更新检查超过 N 天" 都依赖时间，而后者正是触发网络行为的典型原因;
- **CPU 特性**:FFmpeg 等按 cpuid 做 SIMD 运行时分派(AVX2 / AVX-512 走不同代码路径);
- **内核版本与可用 syscall**、`/proc`、`/sys`、hostname;
- **资源**:CPU 数(影响线程数，从而影响某些编码器输出的确定性)、内存上限、ulimit;
- **文件系统语义**:大小写敏感、xattr、tmpfs 与 overlay 的差异。

§9 的 `kernel/runtime_class` 只是一个类别，覆盖不到上面这些。

**结构问题与 r2 相同:** E1 的 10 个扰动(§26)全部取自**已知清单**(HOME、XDG、PATH、locale 等),由同一认知主体挑选，因此天然找不到 unknown unknowns。

另一个后果：允许网络访问的 provider,其外部世界本身就是无界状态，**永远拿不到 CLOSED_SCOPE**。r3 应明确这一点(即这类 provider 永远不能在 security_required 下 ALLOW,或者必须依赖 RUNTIME_ENFORCED 的出站白名单)。

**修订要求**

- §9 环境身份加入:CPU 特性集 / 微架构类、内核版本、资源限制、时钟策略(冻结时间或记录时间偏移)。
- §44 的独立重放改为**异构重放**:第二台 host 必须在 CPU 厂商或代际、内核版本、时钟偏移上至少各有一项不同。verdict 一致才算 PASS。这是对 unknown unknowns 唯一便宜的探针。
- E1 扰动集至少一半由独立 reviewer 自由选择，不得限定在 §26 的清单内。

### P1-5 Blind mutation 不足以证明 suite sensitivity(Target #6)

- **样本量:** 5 个 safety-critical mutation、100% 检出，Wilson 95% 下界约为 **57%**。"100%" 听起来很强，证据量却很弱。
- **代表性:** 人造 mutation(改一个字段、插一次写文件)比真实漂移更 "干净"。真实 drift 往往是条件触发、只在部分输入上出现。
- **独立性:** "独立 reviewer / actor" 没有定义。在小团队或多 agent 工作流里，如果 reviewer 与实现方共享上下文(同一模型、同一 PRD、同一会话历史),它就不是 blind。

**修订要求**

- blind set 中至少一半来自**历史真实回归**:从 upstream 的 changelog、回归 commit、CVE 中选取，回放其前后版本。
- 写明独立性条件:不同人或 agent 实例;不共享 suite 源码;mutation 在 suite 冻结前已提交了内容哈希承诺(commit-reveal)。
- 报告检出率的 CI,不只报告点值。

### P1-6 Gate closure 仍有歧义(Target #8)

| # | 歧义 | 位置 |
|---|---|---|
| 1 | `Attestation Trust PASS` 出现在 §59 的 Technical MVP 条件里，但不在 §55 的 Blocking 列表中，也**没有任何 PASS 判据** | §55 vs §59 |
| 2 | **Upgrade Validation 没有分类**:不在 Blocking、Branching、Informational 任何一类，K6 却引用它;按 P0-1,它又是 stale declaration 的唯一来源 | §42, §61 |
| 3 | E0 = E0a + E0b,但 E0 PASS 只按 E0b 判定;E0a 失败时怎么处置没写 | §18 vs §23 |
| 4 | **INCONCLUSIVE → 扩大 benchmark** 没有次数上限。反复扩大直到 PASS,就是 optional stopping。需要预注册序贯设计，或规定 N 次 INCONCLUSIVE 即视为 FAIL | §21, §23 |
| 5 | E1 是一个 Blocking Gate,但对应两条 Kill,处置不同(K2 "停止 security admission claim" / K3 "Stop")。K2 触发后产品还剩什么?与 Blocking "技术假设不能继续" 的定义冲突 | §55, §61 |
| 6 | Adoption:"至少 5 人" 与 "3/5" —— 访谈 8 人时是 3 人还是 5/8?"愿意进入 pilot" 只是口头表态，需要具体承诺(具名 pilot、时间或数据投入)。§60 的 "Successor Adversarial Review accepted" 由谁接受? | §56–§60 |

另外 K6 中的 "多数"、"substantial redesign" 仍没有量化。

### P1-7 第三方信任(Target #7)

按 P0-1 的修法，Evidence 的价值来自**声明者 ≠ 消费者**,第三方发布者因此会成为 Evidence 的**生产者**(§56 已把 Tool/MCP publisher 列为干系人)。

此时 §46 的 trust policy 能证明 "签名者是发布者 X 的 CI workflow",但证明不了 **runner 诚实地跑过**。发布者完全控制自己的 workflow,可以给伪造的运行结果签名。签名约束的是身份，约束不了行为。

**修订要求:** 二选一并写入 PRD:

- MVP 只声明 **first-party trust**(生产者 = 消费者组织),第三方消费为 Post-MVP;
- 或者，对第三方 Evidence,在 ALLOW 之前要求**消费方侧重放**(或中立 runner 重放),签名只用作完整性校验。

---

## 4. P2

- **P2-1 Retention 衡量的是有没有，不是好不好(Target #5)。** semantic retention 可以挡住 "删维度",挡不住 "降精度"。例如 duration 从毫秒降为整秒、codec identity 从规范枚举降为自由字符串、error semantics 从分类降为 "failed"。
  每个维度应同时冻结 **fidelity 判据**(单位、精度、可空性、枚举规范化)。权重也要随维度一并预冻结。
- **P2-2 间歇性违规。** §7 规定 "任一合法 fixture 违反即 REFUTED",但没规定每个 fixture 跑几次。1/100 概率的竞态违规几乎必然漏检;漏检后，§44 的重放又可能因 verdict 不一致而判 FAIL。
  VERIFIED_IN_SCOPE 应记录 `runs_per_fixture`,并对已知存在不确定性的属性规定最低重复次数。
- **P2-3 Output trust 只是建议。** 字段标成 UNTRUSTED_EXTERNAL,并不能阻止下游 harness 把它塞进 prompt。§63 的边界应写明这是**给 harness 的输入**,本产品只保证标注正确与 adapter 不提升信任等级。E0 也没有任何注入结果类指标，这可以接受，但应写明。
- **P2-4 生产路径成本。** 按 P0-2,verified path 必须在与 Evidence 相同的 hermetic 环境中执行。每次 Agent 调用都要启动容器/namespace,延迟和成本在交互式场景中可能不可接受。E0 只把 latency 列为辅助指标;应加一个**生产路径延迟预算**,作为可行性判据。
- **P2-5 类别混淆。** §35 把 `network behavior`、`side-effect behavior` 列为 contract 的语义维度，但它们是 Evidence 断言，不是输出字段。混在一起会让 E2 的 retention 计算口径不清。

---

## 5. 对 §66 八个审核目标的回答

| # | 目标 | 结论 |
|---|---|---|
| 1 | A/B/C/D 是否隔离了 Evidence | **变量隔离了，效应量没有隔离。** C vs D 的结构正确，但差距由 benchmark 中 false declaration 的比例决定，而这个比例是团队设定的 → **P0-1** |
| 2 | CLOSED_SCOPE 是否消除 epistemic hole | **部分。** 文件/环境变量/配置/网络已封住;时钟、CPU、内核、资源仍可观察;扰动集仍取自已知清单 → **P1-4** |
| 3 | event support + CI 是否足以防假 PASS | **不足。** 有 episode 聚类、RR 点估计、非劣效判定三处漏洞 → **P1-3** |
| 4 | fail-closed 是否还有绕过路径 | **有四条:** 域外输入、执行环境不一致、TOCTOU(**P0-2**);evidence shopping(**P1-1**);Agent 自行 escape(**P1-2**) |
| 5 | semantic retention 是否阻止 LCD | **阻止了删维度，没阻止降精度** → **P2-1** |
| 6 | blind mutation 是否足够 | **方向正确，强度不足:** n = 5 时下界 57%,人造 mutation,独立性未定义 → **P1-5** |
| 7 | Attestation 是否足以支撑第三方 | **不足。** 签名证明身份，证明不了运行诚实;需要在 first-party 范围与消费方重放之间二选一 → **P1-7** |
| 8 | Gate 是否无 closure 歧义 | **否，仍有 6 处** → **P1-6** |

---

## 6. r4 最小修订清单

按工作量从小到大，全部是规则层面的修改，不扩大 MVP 范围:

1. **新增 E0-prevalence**,作为第一个 kill 点;E0b 的混合比例取自实测;E0a 改名为 admission correctness(P0-1)。
2. **Admission 签名加入 `execution_context`**;security 属性要求 ENFORCED 加上 enforcer-validity Evidence;决策记录绑定 digest,exec 前再校验(P0-2)。
3. 加入 REFUTED 支配规则和最低 suite 版本;escape 由 policy 授权，并计入违规(P1-1、P1-2)。
4. 统计改为任务级聚类,RR 用 CI 下界，非劣效用 CI 界;附功效计算和 n 的推导(P1-3)。
5. 环境身份加入 CPU / 内核 / 资源 / 时钟;独立重放改为异构重放(P1-4)。
6. blind set 至少一半来自历史回归，并写明 commit-reveal 与独立性条件(P1-5)。
7. 补齐 Gate 表:Attestation Trust 判据、Upgrade Validation 的归类、INCONCLUSIVE 上限、K2 的处置、Adoption 的计数口径与承诺形式(P1-6)。
8. 声明 MVP 的信任模型是 first-party(P1-7)。

---

## 7. 本轮确认已关闭的 r2 问题

| r2 发现 | r3 处理 | 判定 |
|---|---|---|
| P0-1 E0 未隔离 Evidence | 四臂，C vs D 为因果比较 | **结构已关闭**(效应量问题另见本轮 P0-1) |
| P0-2 scope 遗漏隐藏状态 | DISCOVERED / CLOSED 分级，以消除状态代替判断状态 | **已关闭**(残余为本轮 P1-4) |
| P1-1 样本与统计 | Wilson CI + 最低事件数 | 部分关闭(→ 本轮 P1-3) |
| P1-2 fail-closed | §11 + §12 | **已关闭**(新的绕过路径见本轮 P0-2、P1-1、P1-2) |
| P1-3 E2 LCD | semantic retention | 部分关闭(→ 本轮 P2-1) |
| P1-4 E3 已知 mutation | dev / blind 分离 | 部分关闭(→ 本轮 P1-5) |
| P1-5 Attestation 身份 | Format ≠ Trust,trust policy | **已关闭**(第三方问题见本轮 P1-7) |
| P1-6 process group | PID namespace / cgroup | **已关闭** |
| P1-7 Gate 语义 | 三分类 taxonomy | 部分关闭(→ 本轮 P1-6) |
| P2-1 repeatability | 独立重放 | **已关闭**(加强建议见本轮 P1-4) |
| P2-2 原型事实入规范 | §53 Research Notes | **已关闭** |
| P2-3 benchmark 代表性 | §32 治理 | 部分关闭(流行率问题升级为本轮 P0-1) |
| P2-4 Adoption 处置 | §58 | **已关闭**(计数口径见本轮 P1-6) |