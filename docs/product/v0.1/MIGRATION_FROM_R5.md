# Migration from PRD v0.1-r5 to the decomposed v0.1 L1 authority package

Purpose: make every material move/deletion reviewable.  
Source: `docs/product/prd-v0.1-r5.md`

## 1. New authority graph

~~~text
PRD.md
  defines product claims / black-box behavior / invariants / kill criteria

L1_EVIDENCE_INDEX.md
  maps product claims -> preregistered L1 evidence

l1/*-protocol.md
  defines how each L1 claim is tested before data collection

l1/*-result.md
  records immutable result terminals; currently NOT_RUN

L2_QUESTION_REGISTER.md
  records unresolved architecture/security questions that passed Transfer Test

PRODUCT_FREEZE.md
  pins exact blobs and aggregates; never redefines facts
~~~

## 2. r5 section migration

| r5 area | Successor authority |
|---|---|
| §1 Product thesis/value channels | PRD §§1–4; E02 protocol for falsification |
| §2 security property classes | PRD security boundary + Q-L2-001/Q-L2-007; internal taxonomy deferred |
| §§3–4 MVP/canonical model | PRD §§5–6; internal object graph deferred to L2 |
| §§5–14 Provider/Evidence/scope/refutation/admission/TOCTOU mechanics | Product invariants retained in PRD; exact mechanics moved to Q-L2-002..008 |
| §15 threat model | Product-level threat boundary is frozen in PRD §4; Q-L2-001 chooses an enforcement mechanism that must satisfy it; output-trust mechanics remain Q-L2-007 |
| §§16–21 L1 lifecycle/CAL/PREV/ADOPT/Review/Freeze | PRD §§8–12 + L1_EVIDENCE_INDEX + E00/E01/E03 protocols + PRODUCT_FREEZE |
| §§22–28 post-Freeze technical gates | Removed from L1 PRD authority; become L2/release-design inputs after Freeze |
| §24 T2 four-arm experiment | Replaced by E02 Evidence Decision-Value protocol; old formulation intentionally retired |
| §§29 fixtures / §34 preregistration governance | L1_EVIDENCE_INDEX + E00–E03 protocols |
| §30 performance | Q-L2-009 |
| §31 cross-provider alignment | PRD PCL-004/non-goal; post-v0.1 branch, not Freeze prerequisite |
| §32 upgrade/staleness | E01 for stale problem evidence; detailed compatibility/release mechanics deferred |
| §33 local Evidence store | L2 architecture, not product PRD |
| §§35–36 reviewer/gate mapping | L1_EVIDENCE_INDEX review rule + ADS directly |
| §38 product boundary | PRD black-box behavior/non-goals |
| §39 What r5 does not prove | preserved by result placeholders and each protocol's What Was NOT Proven |
| §§40–41 terminal/review targets | superseded by exact successor review Issue |

## 3. Material r4 concepts previously deleted in r5

The following r4 concepts are explicitly accounted for rather than silently dropped:

- **Output trust** → restored as PRD INV-007 + Q-L2-007.
- **Hard-case adaptation probe** → moved to `PRODUCT_RESEARCH_BACKLOG.md` R-001 as non-blocking future Product Evidence, not L2 architecture authority.
- **Kill criteria** → restored as PRD K1–K4, tied to PCL-001/002/003/005.
- **Anti-metrics** → restored in PRD §14.
- **Technical suite sensitivity / replay / attestation gates** → intentionally moved out of L1 Freeze authority into future L2/release design; they are not claimed solved.
- **Agent four-arm comparison** → intentionally removed as an L1 product claim because Provider selection and raw-shell performance are not required for v0.1 thesis. E02 now tests the narrower claim actually made by PCL-003.

## 4. Semantic deletions

Intentionally deleted from current Product authority:

- universal Capability as a required abstraction;
- public Registry/Marketplace;
- Agent Provider ranking;
- detailed Linux/kernel/sandbox mechanism;
- exact refutation-overlap algebra;
- exact attestation format;
- exact content-addressed store design;
- specific post-Freeze release-gate design.

Reason: these are non-goals or L2/release questions, not L1 product facts.

## 5. No silent closure

Moving an r5 P1/P2 question into L2 does not close it.

The Independent Product Reviewer must verify every `L2_REQUIRED` transfer. If a negative answer would invalidate a product claim, the question must return to L1_BLOCKING.
