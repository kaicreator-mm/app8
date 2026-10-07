# SE09 — Expanded Market / Comparator Evidence

Status: COMPLETE_RESEARCH / PROPOSED_PASS / FRESH_REVIEW_REQUIRED  
Successor authority: Issue #21  
ADS process-gap follow-up: kaicreator-mm/ai-development-standard#929

## 1. Research question

Does the clarified app8 thesis still represent a material product gap after comparing the strongest current software-to-Agent projects, or is app8 only bundling features that already exist?

The tested successor thesis is not "generate a CLI/MCP/Skill".

The tested thesis is:

~~~text
heterogeneous software knowledge
  -> semantic capability hypothesis
  -> adversarial evidence planning
  -> real behavioral evidence
  -> Evidence-backed Capability authority
  -> multiple Agent-facing projections
~~~

with a reuse-first/offline ecosystem-mining strategy for implementation knowledge and modules.

## 2. Research correction

The initial comparator sweep was insufficient. It over-indexed on MCP/Skill/exporter terminology and missed the GUI-to-CLI / agent-native-CLI / Agent-harness cluster.

The expanded sweep therefore adds:

- problem/job vocabulary;
- input/source vocabulary;
- output/interface vocabulary;
- "agent-native software" / "GUI-to-CLI" / "Agent harness" vocabulary;
- second-hop comparison from strong comparators;
- explicit differentiation between category validation and app8 differentiation.

This research gap is also recorded as an ADS evolution candidate in ai-development-standard#929.

## 3. Exact comparator evidence

### C1 — HKUDS/CLI-Anything

~~~text
repo = HKUDS/CLI-Anything
main = 34f519533bc175d2fe287ab8316b0dd99bb9cc43
HARNESS.md blob = 4fd881137c280cf33fcbf9342b91629524906136
license = Apache-2.0
~~~

Observed strengths:

- explicit "GUI-to-CLI for Open Source Software" Agent-harness methodology;
- backend-engine discovery;
- GUI-action to API mapping;
- data-model and existing-CLI discovery;
- stateful CLI architecture;
- real-software E2E;
- artifact/output validation;
- round-trip and Agent tests;
- SKILL.md generation;
- CLI-Hub discovery/installation.

Disposition:

~~~text
CATEGORY = direct comparator
ALREADY_SOLVES = large share of software -> Agent CLI harness
REUSE_VALUE = very high
APP8_MUST_NOT_REIMPLEMENT = generic CLI-harness methodology/runtime without evidence-backed reason
DISTINCT_GAP = CLI Harness is the product authority; no demonstrated general Evidence-backed Capability authority driving many projections
~~~

### C2 — jackwener/OpenCLI

~~~text
repo = jackwener/OpenCLI
main = 24136945847afbfad266c6c46a8cd335377f9112
README blob = e350b847636050f7ab9f98e7815066831ac8bfea
license = Apache-2.0
~~~

Observed strengths:

- websites, browser sessions and Electron apps -> deterministic CLI interfaces;
- structured DOM snapshots rather than screenshot-only interpretation;
- network endpoint discovery;
- logged-in browser-session reuse;
- adapter authoring/verification/repair;
- Electron/CDP support;
- Skill-based Agent use.

Disposition:

~~~text
CATEGORY = direct adjacent comparator
ALREADY_SOLVES = Web/Electron semantic-surface discovery and CLI adapter generation
REUSE_VALUE = very high
DISTINCT_GAP = does not establish a cross-software behavioral Evidence-backed Capability authority independent of its adapters
~~~

### C3 — OpenAI skills / cli-creator

~~~text
repo = openai/skills
main = 49f948faa9258a0c61caceaf225e179651397431
cli-creator blob = 60e5a9a03f89cf66a60aa798bfc6f3c3fa5ed8c4
~~~

Observed strengths:

- API docs / OpenAPI / SDK docs / curl / web app / admin tool / scripts -> durable Agent CLI;
- strong Agent CLI command-contract guidance;
- doctor/discovery/resolve/read/write/raw-escape-hatch patterns;
- stable JSON;
- auth/config guidance;
- companion Skill.

Disposition:

~~~text
CATEGORY = direct adjacent comparator
ALREADY_SOLVES = docs/API/SDK -> good Agent CLI contract
REUSE_VALUE = high as CLI export/profile knowledge
DISTINCT_GAP = artifact-first; no general behavioral Evidence-backed Capability layer demonstrated
~~~

### C4 — SkillDoAI/skilldo

~~~text
repo = SkillDoAI/skilldo
main = 11e5f9edec0fe733ab54faa554cf39df8a02180b
README blob = 02947f2677f1b0cd43251c0efa82fc5d67be7e70
license = AGPL-3.0
~~~

Observed strengths:

- source/tests/docs -> Extract + Map + Learn;
- Fact Ledger;
- Create -> Review -> Test loop;
- locally executed generated examples;
- multiple language ecosystems;
- per-stage model routing.

Disposition:

~~~text
CATEGORY = very close conceptual comparator
ALREADY_SOLVES = library knowledge extraction + fact normalization + validated Skill generation
REUSE_VALUE = very high at architecture/pattern level
LICENSE_CAUTION = strong copyleft; LLM rewrite does not erase source-license obligations
DISTINCT_GAP = scoped primarily to library->Skill; Fact Ledger is not yet the general cross-interface behavioral capability authority app8 proposes
~~~

### C5 — huggingface/upskill

~~~text
repo = huggingface/upskill
main = 5462a245bed95aab3a5d2264197e893d27318663
README blob = 2f34ed3f1e8a2c5f0e1a7023e09169be60a5f799
license = Apache-2.0
~~~

Observed strengths:

- Skill generation from task/traces;
- automatic test generation;
- baseline vs with-Skill evaluation;
- teacher/student model patterns;
- repeated/multi-model benchmarking;
- token/success measurements;
- failure-driven refinement.

Disposition:

~~~text
CATEGORY = evaluation comparator
ALREADY_SOLVES = much of Agent utility evaluation for Skills
REUSE_VALUE = high
DISTINCT_GAP = evaluates Skill utility rather than serving as software behavioral Capability authority
~~~

### C6 — amarnath3003/MCPify

~~~text
repo = amarnath3003/MCPify
main = 164a59212d3513bedfee98d8d0edf7adbb056889
README blob = 36c07c55468aecfe92ffdbf9d48112436b1c5700
license file = CC BY 4.0
~~~

Observed strengths:

- backend/OpenAPI/database/event/frontend analysis;
- workflow detection;
- call-graph/graph-style analysis;
- MCP generation;
- optional AI enhancement;
- simulation/safety surfaces.

Disposition:

~~~text
CATEGORY = direct MCP compiler comparator
ALREADY_SOLVES = substantial source/surface discovery + code->MCP pipeline
REUSE_VALUE = high for analyzer patterns
DISTINCT_GAP = discovered callable/tool surface remains close to output authority; no demonstrated general behavioral Evidence-backed Capability authority
~~~

### C7 — Agent Reach

~~~text
repo = alksnd/Agent-Reach
main = 71b85f8b978d8a8c5febd7152c602d2d4a5d2eea
README blob = 64fee8249d013601281102a4bf7fdf2410f72671
license = MIT
~~~

Observed strengths:

- explicitly positions itself as a capability layer rather than another tool;
- selects/installs/health-checks/routes upstream tools;
- ordered fallback backends;
- currentness and backend replacement as operating concerns.

Disposition:

~~~text
CATEGORY = capability-routing comparator
ALREADY_SOLVES = practical backend selection/currentness for its channel domain
REUSE_VALUE = high for binding health/routing patterns
DISTINCT_GAP = capability layer is primarily routing/availability; it does not claim the app8 evidence-to-semantic-capability compiler pipeline
~~~

## 4. What is already commoditized

The expanded evidence rejects these as standalone app8 differentiation:

~~~text
GUI/App -> CLI
Web/Electron -> CLI
Docs/API/SDK -> CLI
Code -> MCP
Library -> Skill
CLI -> Skill
Skill evaluation
Tool/CLI registry
Backend health/routing
~~~

Therefore app8 must not claim novelty or moat from merely offering these outputs in one repository.

## 5. Remaining product gap

The strongest remaining gap is narrower:

~~~text
Software knowledge and surfaces
          ↓
LLM semantic understanding
          ↓
Capability Hypothesis
          ↓
LLM adversarial falsification planning
          ↓
real execution / observation
          ↓
Behavioral Evidence
          ↓
LLM capability compilation
          ↓
Evidence-backed Capability
          ↓
many replaceable projections/consumers
~~~

The key distinction is not the existence of multiple exporters.

It is that the stable authority is a behavioral, provenance-bound Capability representation that can survive exporter replacement and drive:

- CLI;
- MCP;
- Skill;
- Agent docs;
- capability search;
- binding selection/currentness;
- later revalidation.

## 6. Ecosystem harvesting finding

The comparator codebases are valuable implementation evidence, but directly embedding all projects as runtime adapters would make app8 large and tightly coupled.

Proposed Product/architecture direction:

~~~text
External OSS
  -> LLM-assisted code/architecture analysis
  -> reusable pattern/module candidate
  -> provenance + license gate
  -> app8-owned contract
  -> independent validation
  -> KEEP / ADAPT / DIRECT_REUSE / DROP
~~~

Three reuse levels are required conceptually:

~~~text
LEVEL_1_PATTERN
learn the engineering pattern only

LEVEL_2_REIMPLEMENTED_MODULE
derive a functional contract and independently implement a general app8 module

LEVEL_3_DIRECT_REUSE
reuse/vendor/depend on upstream only when license, quality and module boundary justify it
~~~

Important boundary:

~~~text
LLM_REWRITE != LICENSE_ERASURE
~~~

Any code-derived module must retain durable provenance and a license disposition appropriate to the actual reuse/derivation path.

The exact harvesting implementation is L2/implementation work unless later evidence shows it changes the Product thesis.

## 7. LLM architecture finding

The comparator landscape supports preserving three distinct runtime reasoning roles:

~~~text
LLM-A = UNDERSTAND
software knowledge -> Capability Hypothesis

LLM-B = FALSIFY
Capability Hypothesis -> adversarial Evidence/Test Plan

REAL EXECUTION = REALITY JUDGE
actual software -> observations

LLM-C = COMPILE
hypothesis + positive/negative evidence -> Evidence-backed Capability
~~~

An additional low-frequency/offline role is useful:

~~~text
LLM-0 = LEARN
open-source ecosystem -> patterns/modules/profiles
~~~

LLM-0 is not required on every target-software compilation.

The distinguishing claim is not "four LLM calls"; it is separation of epistemic roles plus real execution between hypothesis and compilation.

## 8. Differentiation disposition

~~~text
CATEGORY_VALIDATION = VERY_STRONG
DIRECT_COMPETITION = HIGH
FEATURE_DIFFERENTIATION = LOW
ARCHITECTURAL_DIFFERENTIATION = MEDIUM
UNIFIED_PRODUCT_GAP = MEDIUM
SEARCH_COVERAGE_CONFIDENCE = MEDIUM_HIGH
~~~

The evidence does not justify a claim that app8 has no competitors.

It does justify continuing only if app8 remains centered on:

~~~text
Evidence-backed Capability authority
+ behavioral falsification/evidence
+ one authority -> replaceable consumers
~~~

## 9. Build-vs-reuse disposition

~~~text
CLI_GENERATOR = REUSE/HARVEST_FIRST
WEB_ELECTRON_DISCOVERY = REUSE/HARVEST_FIRST
MCP_SURFACE_ANALYSIS = REUSE/HARVEST_FIRST
LIBRARY_FACT_EXTRACTION = REUSE/HARVEST_FIRST
AGENT_UTILITY_EVAL = REUSE/HARVEST_FIRST
BINDING_ROUTING = REUSE/HARVEST_FIRST

APP8_CORE_OWNERSHIP =
Capability semantics
Evidence semantics
Provenance/currentness
Falsification loop
Capability compilation
Projection contracts
Capability-level search semantics
~~~

## 10. What was NOT proven

This research did not prove:

- that Evidence-backed Capability provides measurable Agent utility;
- that the Capability abstraction can be extracted with acceptable precision/coverage;
- that LLM-generated falsification plans are reliable enough;
- that one factual authority can drive all projections without semantic drift;
- that capability-level search adds material value;
- that automated OSS module harvesting materially reduces implementation cost;
- that the proposed architecture is legally sufficient for every upstream license;
- that app8 has a sustainable business moat.

Those remain successor L1/L2 questions.

## 11. SE09 terminal

~~~text
SE09_RESEARCH = COMPLETE
SE09_PROPOSED_VERDICT = PASS
CATEGORY_VALIDATION = VERY_STRONG
DIRECT_COMPETITION = HIGH
FEATURE_DIFFERENTIATION = LOW
ARCHITECTURAL_DIFFERENTIATION = MEDIUM
UNIFIED_PRODUCT_GAP = MEDIUM
PRODUCT_DIRECTION = NARROW_AND_PROCEED
FRESH_REVIEW_REQUIRED = YES
PRODUCT_FREEZE = NO
L2_READY = NO
~~~
