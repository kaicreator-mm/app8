# E03 frozen external cohort manifest

Protocol binding:

```text
protocol_path = docs/product/v0.1/l1/E03-adoption-protocol.md
protocol_blob = 7ceefde5973544554da485665d40a165a120ed25
issue = #13
freeze_date = 2026-10-08
cohort_size = 8
```

## Freeze semantics

This file freezes the exact eight real external interview targets before any E03 outcome is known. It does **not** claim that outreach, consent, scheduling, an interview, or a pilot commitment has already occurred. Outreach and interview execution belong to E03-B (#14).

No participant may be replaced because of a response or outcome. If a frozen target declines or is unreachable, that remains part of the frozen cohort evidence; replacement requires a successor Product Evidence protocol/version rather than post-outcome substitution.

Public records use opaque IDs P01..P08. The selected people are real current practitioners and are bound by an identity commitment over a public professional identity. The canonical preimage is:

```text
<public professional full name>|<current role string>|<public source URL>
```

The full name is intentionally not copied into this public manifest. The role + authoritative source URL is a public professional locator sufficient for E03-B to resolve the intended person, and the SHA-256 commitment prevents silent substitution.

## Recruitment channels

Preregistered channels are official project/company community or leadership contact routes associated with the participant's current public professional role. No private email address, credential, NDA material, or non-public contact information is stored here.

## Inclusion criteria

A target is included only when all are true:

1. a real identifiable person, not a synthetic/LLM persona;
2. outside the app8 authoring organization/team;
3. currently operating in one of the frozen stakeholder classes;
4. current public professional evidence supports hands-on responsibility relevant to agents/tool platforms, AI security, or AI governance;
5. an official public project/company/community route exists through which E03-B can attempt recruitment.

## Exclusion criteria

Exclude:

- app8 authors or members of the app8 authoring organization/team;
- synthetic, generated, role-play, composite, or fictional personas;
- people whose only fit is generic AI interest with no current operational role;
- unverifiable/private identities without a durable professional source;
- substitutions selected after any interview outcome is known.

## Frozen cohort

| ID | Stakeholder class | Public professional locator | Recruitment channel | Inclusion basis | Identity commitment (SHA-256) |
|---|---|---|---|---|---|
| P01 | Agent/tool-platform practitioner | Current LangChain co-founder/CEO on the official LangChain About page: https://www.langchain.com/about | LangChain official community/forum route | Leads an agent engineering platform and open-source agent frameworks used for production agent development, observability, evaluation and deployment. | `49a1b685461302e6b485990c36c5eaa6daadf37d7feb69afe47b32e619d8d86c` |
| P02 | Agent/tool-platform practitioner | Current CrewAI founder/CEO identified in CrewAI's 2026 agentic-AI material: https://crewai.com/blog/the-state-of-agentic-ai-in-2026 | CrewAI official community route | Leads a production agent platform focused on agent orchestration, operations, trust, governance and reliability. | `ef895a5cc23d6c751837e7bfb0b6df9bce935a01cde497a7da3984e73b367906` |
| P03 | Agent/tool-platform practitioner | LlamaIndex CEO/co-founder on the official LlamaIndex site: https://www.llamaindex.ai/blog/llamaindex-and-weaviate-ba3ff1cbf5f4 | LlamaIndex official community/company contact route | Leads an agent/data-tool platform with production ingestion, retrieval, parsing and agent tooling. | `d38d737216c5d68cc097f1291b25303545fcf82ae058fd864e09fb8c6050c6d1` |
| P04 | Agent/tool-platform practitioner | AG2 founder/CEO in the official 2026 AG2 outlook: https://www.ag2.ai/blog/agentic-ai-outlook-2026 | AG2 official maintainer support/community route | Leads a multi-agent framework/platform whose current focus includes orchestration, verification and production operation of agent systems. | `946a4dfe52f64ad6800563efe36f12532723153e2794f7687d04ee6b092cf53b` |
| P05 | Security/governance practitioner | Co-lead of the Agentic Security Initiative in the OWASP GenAI Security Project leadership roster: https://owasp.org/projects/genai-security | OWASP GenAI Security Project leadership contact route | Direct operational responsibility for security guidance around agentic systems. | `493fa19a2dcab32fb8756d542be11f49f271d1df80183325bec017d85f920d76` |
| P06 | Security/governance practitioner | Co-lead of the AI Governance Initiative in the OWASP GenAI Security Project leadership roster: https://owasp.org/projects/genai-security | OWASP GenAI Security Project leadership contact route | Direct operational responsibility for AI governance guidance and control frameworks. | `55b9b574edba760067ad81081298ba25a747151570bf91b2fd9f744df62fb3ce` |
| P07 | Security/governance practitioner | Technical Lead in the OWASP GenAI Security Project leadership roster: https://owasp.org/projects/genai-security | OWASP GenAI Security Project leadership contact route | Direct technical responsibility for GenAI security guidance and practitioner controls. | `f094693c378e6998c22b3541b9df61fe031273fea19a58ca9a841d5ae2f4d42f` |
| P08 | Security/governance practitioner | Co-chair / Top 10 for LLM founder / co-lead in the OWASP GenAI Security Project leadership roster: https://owasp.org/projects/genai-security | OWASP GenAI Security Project leadership contact route | Leads a widely used AI/LLM application security risk framework and related practitioner guidance. | `5fa04a262b46b74c78839cceca95ef8f29655667919e3188607fc0cfce637f51` |

Composition:

```text
Agent/tool-platform practitioners = 4
Security/governance practitioners = 4
Tool/MCP publisher-only slots = 0
Total = 8
```

This exceeds both minimum class requirements (>=3 and >=3) without using the two flexible slots.

## Anti-bias lock

- No participant replacement after any response/outcome is known.
- No synthetic/LLM persona may enter the cohort.
- No app8 author may be counted as external.
- Interview questions must distinguish concrete recurring problems from general interest.
- A positive classification requires a concrete pilot commitment; interest, praise, hypothetical willingness, or survey-only intent is insufficient.
- E03-A records no interview outcome and makes no PASS/FAIL judgment.
