# app8 产品需求文档（PRD）v0.1 Successor r2 — 基于证据的软件能力编译器

> **文档性质：中文对照版，非新增或替代的产品权威。** 对产品主张、边界、Gate、状态或术语有歧义时，以英文 [PRD.md](./PRD.md)、[L1_EVIDENCE_INDEX.md](./L1_EVIDENCE_INDEX.md) 及相应的 GitHub exact-blob 证据为准。本文不批准 Product Freeze、L2 或正式实现。
>
> 英文 PRD 来源 blob：`998348fe1fd79c4a99d72a96c00a5da641b9afa6`；L1 Evidence Index 来源 blob：`5f6c7cf40e6a7b3cf7163b078d892f34a4ef1498`。
>
> L1 研究任务依赖关系参考 [Issue #25](https://github.com/kaicreator-mm/app8/issues/25)。它**不是** Product Freeze 之后的正式实现 Task DAG。

**英文原稿状态**：`DRAFT_FOR_INDEPENDENT_REVIEW`  
**当前项目方向**：`NARROW_AND_PROCEED`  
**Product Freeze**：`NO`  
**L2 Ready**：`NO`  
**Successor 产品定义来源**：[Issue #21](https://github.com/kaicreator-mm/app8/issues/21)  
**开发规范固定版本**：`kaicreator-mm/ai-development-standard@7929012f36a2202dcc2edc7a414b8163adc7afbd`（4.9.0）  

## 1. 产品定义

app8 是一个**由 LLM 驱动、以证据为基础的软件能力编译器**（Evidence-backed Software Capability Compiler）。

它把现有软件的知识和真实行为转化为可复用的、**经证据支持的能力**（Evidence-backed Capability），再将同一能力投影为 Agent/LLM 易于使用的接口与知识。

产品长期稳定的事实权威**不是 CLI、MCP、Skill，也不是某个适配器**，而是：

~~~text
Capability 语义
+ 真实行为证据（Behavioral Evidence）
+ 来源与有效性（Provenance / Currentness）
+ 软件绑定身份（Binding Identity）
~~~

CLI、MCP、Skill、Agent 文档、搜索元数据是可替换的**投影/消费端**，必须基于同一份事实权威。

### 1.1 主要输出

- Evidence-backed Capability 包；
- 面向 Agent 的 CLI 投影；
- MCP 投影；
- 可移植的 Skill 投影；
- Agent/LLM 文档；
- 可搜索的 Capability Metadata。

### 1.2 输入范围

“软件资产”（Software Asset）不限于 GUI 应用，可包括 CLI 工具、库、SDK、API、服务、源代码仓库、二进制、桌面/服务器应用、网站/Electron 应用，以及这些资产的组合。

## 2. 用户问题与产品机会

成熟软件已实现大量有用功能，但 Agent 在使用它们时重复付出高成本：

- 任务运行时重新阅读冗长文档；
- 围绕原始 flag、函数、端点推理，而不是面向用户目的的能力；
- 编写一次性胶水代码和 Wrapper；
- 独立生成 CLI/MCP/Skill，造成语义漂移；
- 误信未经真实软件验证的模型生成接口；
- 丢失版本特定行为、约束、副作用和失败语义；
- 重造成熟开源软件已经解决的接入与调用机制。

**产品机会**：将已有软件编译为可复用、有可验证证据的 Agent 能力，同时优先学习、复用成熟开源工程，而不是重新实现每一种接口机制。

## 3. 产品核心与非核心边界

### 3.1 app8 自有核心

app8 对以下语义和契约承担产品责任：

1. Capability 的用户意图和语义；
2. Capability 的生命周期与就绪度；
3. Evidence 的事实语义；
4. 正向与负向/反驳证据；
5. Provenance 来源追溯；
6. 软件、绑定、版本、环境的 Currentness；
7. 反证与证据闭环；
8. 基于证据的 Capability 编译；
9. 投影契约；
10. Capability 级检索语义。

### 3.2 非核心：复用优先

以下能力是产品所需，但不因此要求 app8 自研：

- 通用 CLI 生成；
- Web/Electron 表面发现；
- AST、框架、源代码分析；
- MCP 与 Skill 生成；
- Agent 效用评测基础设施；
- 后端健康检查/路由；
- 打包、安装机制。

优先 `REUSE / HARVEST / ADAPT / DIRECT_REUSE`。把这些功能放进一个仓库并不天然构成差异化。

## 4. 核心编译执行闭环

~~~text
软件知识 / 可发现接口
          ↓
LLM-A：UNDERSTAND（理解）
          ↓
Capability Hypothesis（能力假设）
          ↓
LLM-B：FALSIFY（寻找反例）
          ↓
Evidence / Test Plan（证据/测试计划）
          ↓
确定性的真实执行 / 观察
          ↓
Behavioral Evidence（行为证据）
          ↓
LLM-C：COMPILE（证据约束的编译）
          ↓
Evidence-backed Capability
          ↓
CLI / MCP / Skill / Docs / Search
~~~

核心差异不是“三次 LLM 调用”，而是**认知角色隔离 + 真实世界观察**：模型提出假设、主动寻求反证，事实由真实软件的执行或观察产生，最后只能在证据允许的范围内编译。

### 4.1 LLM-A：UNDERSTAND

依据文档、教程、示例及发现的接口，提出：

- 能力的用户目的及使用时机；
- 输入/输出；
- 重要约束、前置条件；
- 副作用；
- 变体和模式；
- 可能的原生绑定；
- 示例、操作配方；
- 预期错误/失败语义。

输出是 `Capability Hypothesis`，**不是已经验证的事实**。

### 4.2 LLM-B：FALSIFY

针对假设设计有边界、可执行的求证、收窄或反驳方案，包括：

- 可执行 fixture；
- 正向用例；
- 负向/反例用例；
- 近似命中、边界用例；
- 可观测的预期输出；
- 副作用检查；
- 版本/平台检查；
- 重放需求；
- 能揭露文档歧义或隐藏限制的测试。

目标不只是“怎样让它通过”，还必须追问“**怎样证明这个说法不成立**”。

### 4.3 确定性真实执行

环境允许时，针对**实际的软件和绑定**执行/观察，记录：

- 命令或调用；
- 输入与 fixtures；
- stdout/stderr 或等价观测；
- 输出文件等产物；
- 状态变化及副作用；
- 版本、环境和绑定身份；
- 断言、失败和反例。

凡声称验证真实行为的地方，模型判断不得代替真实执行。

### 4.4 LLM-C：COMPILE

在证据可用且足够时，把假设与证据约束编译为面向 Agent 的 Capability：

- 哪些底层接口属于同一语义能力；
- 哪些变体需要分开；
- 哪些限制必须暴露为参数/前置条件；
- 哪些绑定真正可互换；
- 哪些错误、恢复建议必须保留；
- 哪些能力声称必须收窄或被反驳。

`COMPILED` 不等于 `EVIDENCED`，更不自动等于 `EXPORT_READY`。

## 5. 离线开源生态学习与模块采收（LLM-0）

app8 可以在低频、离线或构建期分析成熟开源项目，避免重复发明：

~~~text
成熟开源项目
  → LLM-0：生态/代码分析
  → 可复用模式或模块候选
  → 来源/许可证处置
  → app8 自有功能契约
  → 独立验证
  → KEEP / ADAPT / DIRECT_REUSE / DROP
~~~

LLM-0 回答的是：“生态已经学会了什么，app8 没必要再重新学习或实现？”它**不是**每次编译目标软件的必经运行时步骤。

支持三种概念性复用层次：

| 层次 | 含义 |
|---|---|
| `LEVEL_1_PATTERN` | 只学习工程模式，不必引入上游代码 |
| `LEVEL_2_REIMPLEMENTED_MODULE` | 抽取功能契约，独立实现 app8 通用模块，并保留来源 |
| `LEVEL_3_DIRECT_REUSE` | 当许可、质量、边界允许时直接依赖、引入或复用上游代码 |

**硬约束**：`LLM_REWRITE != LICENSE_ERASURE`。用模型改写、重构源码，不会自动消除上游版权和许可证义务。采收引擎、语言覆盖、代码分析框架、模块机制属于 L2/实施决策，除非证据表明其影响产品主张。

## 6. 能力理解的主要知识来源

通常按以下顺序优先获取语义材料：

1. 官方文档；
2. 官方教程、Cookbook、示例；
3. 内置 help、manpage、参考材料；
4. API/SDK/库参考；
5. README 与样例项目；
6. 源代码、类型与 Schema；
7. 二进制/静态分析或反编译；
8. UI Automation、Accessibility Tree 等结构化系统/UI 语义。

文档/教程通常比原始可调用接口更能表达用户意图。较低层的资料用于补足空白、求证、诊断失败、找回绑定、核实未记录的行为和实现事实，不应直接把“所有函数”提升为“所有 Capability”。

## 7. Evidence 是事实核心

Evidence 不是另一个准入治理产品；它是防止能力语义和投影只依赖模型猜测的事实层。

参考生命周期：

~~~text
DISCOVERED（发现）
   ↓
HYPOTHESIZED（形成假设）
   ↓
TEST_PLANNED（生成测试计划）
   ↓
EVIDENCED（有证据） / REFUTED（已反驳） / BLOCKED（受阻）
   ↓ 仅对满足证据与就绪条件的对象
COMPILED（已编译）
   ↓ 通过就绪门禁
EXPORT_READY（可导出）
~~~

这一示意**不允许**把 `REFUTED`、`BLOCKED` 或仅 `COMPILED` 直接标为 `EXPORT_READY`；具体状态机、充分性条件须保留在后续权威审查中。

一个 Evidence Package 可以保存：来源声称、调用/绑定身份、软件/Provider 版本、fixture/input、运行环境、真实观测、输出产物和状态增量、正负证据、已知限制、已知不支持场景、重放资料及来源/时效性。

单个通过的 fixture **不等于**对任意输入的正确性或通用安全性证明。证据可支持、收窄或反驳最初的假设。

## 8. Evidence-backed Capability 模型

核心语义单元是**对用户有意义的能力**，而不是裸函数、端点、flag 或一次 UI 操作。

示例：

~~~text
Capability: media.trim

经证据支持的行为：
- 有边界的视频裁剪
- stream-copy 快速变体受到关键帧限制
- 精确变体需要解码/重编码

Bindings：
- ffmpeg 原生 CLI
- 可选的库绑定

Projections：
- 规范化 CLI
- MCP Tool
- Skill Recipe
- Agent Docs
~~~

一个能力可以汇集多个底层接口、多种绑定；实现同一用户目的的函数不应该机械地拆成多个顶层 Agent 工具。

内部 IR Schema 是 `L2_REQUIRED`，但不得移除证据关联、来源、负向证据、变体、约束、绑定身份、版本/环境范围和 readiness/currentness。

## 9. 单一事实权威，多种投影

~~~text
Evidence Corpus（证据库）
       ↓
Evidence-backed Capability
       ↓
CLI / MCP / Skill / Agent Docs / Search Metadata
~~~

每个投影器只能消费同一个冻结的 Capability/Evidence 权威。它可以追加表达形式特有的元数据，不能重新解读原软件并改变语义事实。

投影结果允许明确返回：

- `SUPPORTED`：支持；
- `UNSUPPORTED`：没有受支持的投影；
- `BLOCKED`：受条件阻止；
- `STALE`：已过期，需要重新验证。

不得悄悄替换为不同能力来掩盖不支持。

## 10. Capability 语义搜索

允许按用户意图检索，例如：

~~~text
将 DOCX 转为 PDF
分析一个 pcap 文件
从视频中提取音频
~~~

每项结果至少应表明：软件资产、Capability、证据/就绪状态、可用绑定与投影、版本/平台限制，以及重要的负面/不支持边界。

`DISCOVERED` 或 `HYPOTHESIZED` 的材料不能冒充 `EXPORT_READY`。v0.1 不要求公共市场（Marketplace）。

## 11. 接口发现与绑定策略

允许的发现/绑定路径：

- 原生 API、SDK、库；
- 原生 CLI、Headless；
- 协议、IPC、RPC、本地服务；
- 文件或结构化数据接口；
- 源码、类型、Schema 分析；
- 授权条件下的二进制静态分析/反编译；
- Windows UI Automation、Accessibility Tree、语义 DOM 等结构化 UI；
- 把现有内部能力暴露为稳定接口的最小 OSS Fork/Patch；
- 生成的轻量 Adapter/Shim。

优先稳定、可程序化的接口，而不是脆弱的交互路径。

### 严禁从像素推导自动化

以下路径**不得**用作 app8 的能力发现、绑定或执行机制：

- 截图/图像理解来发现 UI 控件；
- 视觉模型定位按钮、菜单；
- OCR 或视觉布局推断驱动 UI；
- 像素/模板匹配；
- 根据坐标/像素推导的 Computer Use。

~~~text
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
SEMANTIC_STRUCTURED_UI = ALLOWED
~~~

结构化 Accessibility/UI Automation 提供可机器读取的角色、状态和动作，因而允许使用；无法找到可靠合法绑定时必须返回 `UNSUPPORTED/BLOCKED`。针对**输出图像/视频产物**的验证与“从截图寻找 UI 控件”不是同一回事。

## 12. Fork、逆向与合规边界

针对开源软件，如果功能已经存在于内部，但没有适合 Agent 的稳定接口，可以通过最小 Fork/Patch 暴露 Headless/结构化接口，再生成证据并绑定为 Capability。

针对闭源软件或二进制文件，仅在**获得授权且合法**的前提下开展静态分析、反编译和内部接口发现。app8 不将规避 DRM、授权或技术访问控制作为产品能力。

对改造代码保留来源、许可和后续 upstream 生命周期记录；具体合规执行机制由 L2/流程决定。

## 13. 产品主张（SPCL-001～007）

以下是必须经过 L1 证据验证的**可证伪产品主张**，不是已经取得的结果：

| 标识 | 主张 | 核心验证 |
|---|---|---|
| `SPCL-001` | 异构软件的文档、示例及有限底层分析，可提取有用的、面向用户的语义 Capability，具备可接受准确性与覆盖 | SE10 |
| `SPCL-002` | 对抗性测试计划与真实执行能够确认、收窄或反驳不完整/错误假设，避免“模型自己证明自己” | SE11 |
| `SPCL-003` | 同一冻结的 Capability 权威能生成 CLI、MCP、Skill、Agent 文档和搜索元数据，且无重大语义漂移 | SE12 |
| `SPCL-004` | Agent 使用 app8 投影处理代表性任务，在可比预算下明显优于只依靠原生接口/文档的 Agent | SE13 |
| `SPCL-005` | 可按自然语言意图检索出相关 Capability，并正确表示证据、就绪度和时效性 | SE14 |
| `SPCL-006` | 即使禁止像素驱动自动化，也可为代表性软件组合中的相当一部分有用能力建立可靠绑定 | SE15 |
| `SPCL-007` | 至少一个真实用户群存在反复发生的能力编译需求，并愿投入真实资产、任务、环境、人力或维护者评审 | SE16 |

各项研究的具体抽样、主指标、阈值、PASS/FAIL/BLOCKED 规则，以**冻结的独立实验协议**为准，不得从此中文版临时发明或修改阈值。

## 14. 市场与竞品结论（SE09）

扩展竞品研究覆盖了 CLI-Anything、OpenCLI、OpenAI cli-creator、Skilldo、UPskill、MCPify、Agent Reach 等相邻或直接对比方向；原始来源、固定版本和许可处置参见 [SE09_COMPARATOR_EVIDENCE.md](./SE09_COMPARATOR_EVIDENCE.md)。

~~~text
CATEGORY_VALIDATION = VERY_STRONG
DIRECT_COMPETITION = HIGH
FEATURE_DIFFERENTIATION = LOW
ARCHITECTURAL_DIFFERENTIATION = MEDIUM
UNIFIED_PRODUCT_GAP = MEDIUM
PRODUCT_DIRECTION = NARROW_AND_PROCEED
~~~

通用 CLI/MCP/Skill 生成、Web/Electron 适配、路由与注册表等已有成熟竞品，不能作为 app8 的单独差异化声明。

经研究仍值得继续证伪的方向是：**有行为证据的 Capability 事实权威 + 对抗性反证闭环 + 单一权威驱动可替换消费端**。研究并未证明其商业护城河、实际 Agent 效用或跨软件泛化能力。

## 15. MVP 对外可观察行为

v0.1 候选产品应能够：

1. 接收软件资产及关联知识来源；
2. 枚举语义/程序化接口；
3. 形成带来源的 Capability 假设；
4. 生成有边界的对抗性证据/测试计划；
5. 环境允许时执行或采集真实证据；
6. 持久保存正向与负向/反驳证据；
7. 明确标记能力的生命周期、就绪状态；
8. 从冻结证据编译 Evidence-backed Capability；
9. 从同一权威生成代表性的 CLI、MCP、Skill、Agent 文档投影；
10. 发布可搜索 Capability Metadata；
11. 回应语义 Capability 查询；
12. 上游软件或证据时效性变化时重新验证或标记 `STALE`；
13. 找不到合法接口时拒绝像素自动化，而非静默使用截图/视觉方案。

外部成熟开源方案可承担非核心发现、导出、评估功能；MVP 不要求从零自研所有机制。

## 16. MVP 非目标

v0.1 **不要求**：

- 通用 Agent Runtime/Orchestrator；
- 软件准入/安全治理产品；
- 通用跨软件 Ontology；
- 公共 Marketplace；
- 重造成熟 CLI/MCP/Skill 基础设施；
- 为每个开源项目自动采收模块；
- 为每项上游软件长期维护 Fork；
- 用有限测试证明任意输入的普遍安全；
- 基于截图/像素的 Computer Use；
- 所有软件资产都可自动成功导出。

## 17. 不可削弱的产品不变量（SINV-001～012）

| 标识 | 不变量 |
|---|---|
| `SINV-001` | 声明不是 Evidence；文档和模型推断仅形成声称/假设 |
| `SINV-002` | 模型输出不得自证或自行提升为 `EVIDENCED/EXPORT_READY` |
| `SINV-003` | 对抗性反证是第一等公民，必须主动尝试发现限制、负例与反例 |
| `SINV-004` | 负面证据持久保存，含不支持变体与已观测限制 |
| `SINV-005` | Evidence 必须有软件/Provider、版本/构建、环境、绑定、输入和观察边界 |
| `SINV-006` | CLI/MCP/Skill/Docs/Search 从同一事实权威派生，不得各自重造语义真相 |
| `SINV-007` | 允许结构化语义接口；禁止像素衍生自动化 |
| `SINV-008` | 非核心机制先考虑成熟 OSS 复用/采收，再决定自研 |
| `SINV-009` | LLM 改写不消除来源及版权/许可证义务 |
| `SINV-010` | 复用并暴露已有软件，不以复制成熟应用的业务实现为目标 |
| `SINV-011` | `UNSUPPORTED/BLOCKED` 是合法结果，不得伪造能力 |
| `SINV-012` | 历史证据和反证可审计保留，新解释不得抹除旧事实 |

## 18. 产品成功与终止/转向条件

Product Freeze 的必要条件包括全部 successor L1 证据、独立对抗性 Product Review 和 **有效未关闭 P0=0、P1=0**。

| 编号 | 失败条件与处置 |
|---|---|
| `SK1` | 冻结代表性软件组合中的语义 Capability 提取失败 |
| `SK2` | 证据/反证过程不能可靠区分真实支持与重大不支持 |
| `SK3` | 单一 Capability 权威无法驱动多个消费端而避免重大语义漂移 |
| `SK4` | app8 投影未带来实质 Agent 效用改善 |
| `SK5` | 语义搜索未达标；移除搜索需显式 Product 决策 |
| `SK6` | 禁用像素自动化后覆盖过低；应缩小软件支持类别，**不得放松禁令** |
| `SK7` | 没有任何目标用户群显示重复发生的真实需求和试点投入意愿 |

LLM-0 全自动模块采收失败本身不构成产品终止条件；可以回退到人工精选模式、直接 OSS 复用或按契约独立实现。

## 19. 必须完成的 successor L1 证据

正式映射权威是 [L1_EVIDENCE_INDEX.md](./L1_EVIDENCE_INDEX.md)，具体可执行研究不得以本文替代已预注册协议。

| 研究 | 目标 | 必要边界 |
|---|---|---|
| `SE09` | 扩展竞品/市场证据 | 区分品类有效与 app8 差异化；研究不是运行时能力证明 |
| `SE10` | 语义能力提取 | 异构组合、独立参考集；处罚幻觉、能力过拆/重复、错误合并与失败语义丢失 |
| `SE11` | 反证/行为证据质量 | 正例、重大错误例、边界例；真实执行、独立真值、控制误提升和误拒绝 |
| `SE12` | 单一权威/多消费端 | CLI/MCP 真正调用软件；Skill/Docs/搜索保留约束、变体、错误；冻结输入 |
| `SE13` | Agent 效用 | Raw 接口/文档基线与 app8 投影组预算可比、任务评分独立 |
| `SE14` | 能力搜索质量 | 与常规 Tool/CLI/MCP Registry 检索公平对比；就绪误表述零容忍 |
| `SE15` | 无像素方式的能力覆盖 | 冻结代表资产和能力清单；截图、OCR、坐标等不可计入成功 |
| `SE16` | 真实用户试点拉力 | 真实外部参与者；当前重复痛点 + 明确资源承诺，泛泛兴趣不算通过 |
| Final Independent Product Review | 最终独立 Product 审查 | exact package，P0/P1 全关闭，研究无越权 |

继承的旧版 `E00`（Issue #9）只可作为研究方法资产，**不是** successor Gate PASS；原 E01/E02/E03 及旧 Product Freeze 路径不适用于新产品。

### 19.1 L1 研究依赖 DAG（Issue #25；不是正式实施 Task DAG）

~~~text
SE10 / SE11 / SE12 / SE13 / SE14 / SE15 / SE16
           各实验协议可并行编写
                      ↓
               协议独立 Review
                      ↓
             协议冻结与执行授权

SE10 真实执行 ─┐
SE11 真实执行 ─┼──→ SE12 真实执行 ─→ SE13 真实执行
               │
SE14 真实执行 ─┼────────────────────────────┐
SE15 真实执行 ─┤                            │
SE16 真实执行 ─┘                            │
SE12 / SE13 结果 ───────────────────────────┘
                                           ↓
                                  Product Freeze Candidate
                                           ↓
                                  Final Independent Review
~~~

- 协议撰写允许并行，但每个真实研究必须遵守依赖、冻结对象和预注册阈值。
- `SE12` 执行必须等待 `SE10/SE11` 的冻结 Capability/Evidence 对象；`SE13` 执行还需 `SE12` 的冻结投影。
- Web 端负责研究、协议、审查和管理；需要真实软件、环境/执行证据和 Agent 基准测试的任务由 Local Agent/Real Host 完成。
- 协议审查 PASS 只能允许相应协议推进；**不等于**该实验执行 PASS，更不等于 Product Freeze。
- 项目实时执行状态以 [#25](https://github.com/kaicreator-mm/app8/issues/25)、[#40](https://github.com/kaicreator-mm/app8/issues/40) 及各协议/执行 Issue 为准，不因本文件生成而改变。

## 20. L1 → L2 转交测试

问题只有同时满足以下条件，才能标记 `L2_REQUIRED`：

1. 答案不会改变目标用户、产品问题、`SPCL-001..007`、MVP 黑盒行为、Evidence-before-readiness、单一权威多消费端、像素禁令或终止条件；
2. L1 已知至少一种技术上可信的实施路径；
3. 有多种合理的 L2 架构可满足同一产品契约；
4. 某候选架构失败只导致架构转向，而不是推翻产品主张。

如果否定答案会证明产品主张不成立，必须判为 `L1_BLOCKING`，不能借“下放 L2”绕过。

典型 L2 领域包括：

- Capability IR Schema；
- Evidence Store、Content Addressing、Replay；
- Discovery 组合与模块契约；
- LLM-A/B/C 编排、路由、缓存；
- 确定性执行 Harness；
- 投影生成与一致性机制；
- Structured Semantic UI 绑定；
- 逆向、最小 Fork 生命周期；
- Search Index 与 Ranking 实现；
- Currentness、Revalidation；
- LLM-0 模块采收；
- 许可证与来源自动化校验。

详细问题及不得改变的产品边界见 [L2_QUESTION_REGISTER.md](./L2_QUESTION_REGISTER.md)。

## 21. Product Freeze 的权威范围

Freeze 绑定的是**完整、精确的 successor 证据包**，不是单独一个 PRD 文件。

至少包含：

- successor PRD exact blob；
- successor L1 Evidence Index exact blob；
- 扩展 SE09 证据 exact blob；
- successor L2 Question Register exact blob；
- 从前代产品迁移/处置的 exact blob；
- 全部必须的 successor 实验协议与结果；
- 最终独立 Product Review；
- 固定版本的 ADS。

`PRODUCT_FREEZE.md` 是聚合清单，不得自行重定义 Product/L1。旧版 v0.1 Product Freeze 不能转为 successor Freeze。

只有所有要求通过、无有效未关闭 P0/P1 且 L1→L2 转交检查通过，才有资格宣告 Product Freeze。随后才能形成有依据的 L2 Architecture Evidence，再制定**正式实现 Task DAG**。

## 22. 当前阶段与结论

~~~text
PRODUCT_DIRECTION = NARROW_AND_PROCEED
SUCCESSOR_PRODUCT = EVIDENCE_BACKED_SOFTWARE_CAPABILITY_COMPILER
CORE_RUNTIME = UNDERSTAND -> FALSIFY -> REAL_EXECUTION -> COMPILE
OFFLINE_EVOLUTION = LLM_0_ECOSYSTEM_MINING
REUSE_HARVEST_FIRST = YES
LLM_REWRITE_LICENSE_ERASURE = NO
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
SEMANTIC_STRUCTURED_UI = ALLOWED
LEGACY_E00 = RETAINED_RESEARCH_ASSET

PRODUCT_FREEZE = NO
L2_READY = NO
FORMAL_IMPLEMENTATION_TASK_DAG = NOT_AUTHORIZED
~~~

后续路径：

~~~text
成功完成 successor L1 研究及最终独立 Product Review
  → Product Freeze（exact package）
  → L2 Architecture Evidence
  → 正式 Task DAG
  → 实施、真实验证、发布资格审查
~~~

## 附录 A：中文术语与英文权威映射

| 英文 | 中文建议 | 含义 |
|---|---|---|
| Software Asset | 软件资产 | 被理解、验证与接入的真实软件对象 |
| Capability Hypothesis | 能力假设 | 模型提出、尚未由事实确认的能力 |
| Evidence-backed Capability | 经证据支持的能力 | 带行为证据、范围、绑定及来源的可复用语义能力 |
| Behavioral Evidence | 行为证据 | 对真实软件执行/观测形成的结果 |
| Binding | 绑定 | 指向具体原生接口/实现和版本环境的映射 |
| Projection | 投影 | 从 Capability 权威生成的 CLI/MCP/Skill/Docs/Search 表达 |
| Falsification | 反证/证伪 | 主动检验假设如何失效、收窄或被反驳 |
| Provenance | 来源追溯 | 可以定位原始资料、版本及派生过程 |
| Currentness | 有效性/时效性 | 当前证据对目标软件、环境、版本是否仍适用 |
| Readiness | 就绪度 | 是否满足投影/导出所需证据与约束 |

## 附录 B：来源与同步约束

- 产品事实：[`docs/product/v0.1-successor/PRD.md`](./PRD.md)，来源 blob `998348fe1fd79c4a99d72a96c00a5da641b9afa6`。
- 主张与 Gate：[`L1_EVIDENCE_INDEX.md`](./L1_EVIDENCE_INDEX.md)，来源 blob `5f6c7cf40e6a7b3cf7163b078d892f34a4ef1498`。
- 竞品/复用证据：[`SE09_COMPARATOR_EVIDENCE.md`](./SE09_COMPARATOR_EVIDENCE.md)。
- L2 候选问题：[`L2_QUESTION_REGISTER.md`](./L2_QUESTION_REGISTER.md)。
- 研究执行依赖：[Issue #25](https://github.com/kaicreator-mm/app8/issues/25)。
- Review 注意事项：[Issue #24](https://github.com/kaicreator-mm/app8/issues/24)、[Issue #40](https://github.com/kaicreator-mm/app8/issues/40)。
- 历史已被取代的产品主张：[`docs/product/v0.1/PRD.md`](../v0.1/PRD.md)，仅供历史追溯。

**同步规则**：如果英文权威 PRD、L1 Index 或经批准的产品决策变化，应核对并更新本中文版的来源 blob 和内容；中文文件本身不能改变权威 Gate 或代替独立 Review。