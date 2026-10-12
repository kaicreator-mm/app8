# SE15 Protocol — Non-Pixel Capability Exportability

Status: DRAFT_FOR_FRESH_REVIEW
Execution: NOT_AUTHORIZED
Parent: Issue #25
Owning task: Issue #31
Product authority: main@908cee661f3747439bb0366b158903cb9b38b413

## 1. Falsifiable question

Across heterogeneous software, can app8 bind a material share of useful Capabilities without screenshot/Vision/OCR/pixel-derived UI automation?

Hard invariant:

~~~text
PIXEL_DERIVED_AUTOMATION = FORBIDDEN
SEMANTIC_STRUCTURED_UI = ALLOWED
~~~

## 2. Frozen portfolio

Use these five target identities:

- FFmpeg/FFmpeg@f2bf7a2440d1e49023e4b3ed0e224a8806d388b8
- pandas-dev/pandas@82c18c170b9aea7cbb96ef54b8005bed07c94220
- minio/minio@7aac2a2c5b7c882e68c1ce017d8256be2feea27f
- LibreOffice/core@016fd5d049256dc849111f60870f15201fcd1526
- Microsoft Windows Notepad package/app identity on the Windows execution host, exercised only through Windows UI Automation/accessibility semantics for the structured-UI lane.

Before inspecting Notepad's UIA tree, the execution manifest must freeze:

- Windows edition/build;
- Notepad package/application version;
- executable/package identity;
- UI Automation client/runtime version.

A host lacking Notepad may install the official Microsoft Notepad package before the environment manifest is frozen. After UIA inspection begins, the fifth target may not be replaced.

## 3. Frozen Capability sample

Before binding attempts, an independent semantic reviewer selects the top 5 user-meaningful Capabilities per asset from official user-facing material, for 25 total.

For Notepad, selection is based on ordinary user-visible product behavior/documentation before inspecting which UIA controls happen to be easy to automate.

Selection occurs before inspecting whether a preferred binding is easy or difficult.

## 4. Allowed success routes

- native API/SDK/library;
- native CLI/headless;
- protocol/IPC/RPC/local service;
- structured file/data interface;
- source/type/schema-derived thin adapter;
- authorized binary/static analysis;
- minimal OSS fork/patch;
- Windows UI Automation/accessibility tree;
- semantic DOM/accessibility structure.

## 5. Forbidden routes

A success may not rely on:

- screenshot/image interpretation for control discovery;
- Vision-model menu/button localization;
- OCR/layout inference to drive the UI;
- pixel/template matching;
- hard-coded coordinate clicking;
- any silent fallback from semantic UI to pixels.

Output artifact inspection of images/video is allowed when validating software results; it is not UI-control discovery.

## 6. Binding classification

Each Capability is classified as exactly one:

- DIRECT_NATIVE;
- THIN_ADAPTER;
- MINIMAL_FORK;
- STRUCTURED_SEMANTIC_UI;
- UNSUPPORTED;
- BLOCKED_ENVIRONMENT.

For successful classes, record implementation effort band and stability/currentness risks.

## 7. Primary metrics

- useful bindable coverage = successful Capabilities / non-blocked frozen Capabilities;
- per-asset coverage;
- route distribution;
- unsupported rate;
- structured-semantic UI success rate for Notepad;
- pixel-policy violations.

## 8. Frozen PASS thresholds

PASS requires:

- pooled useful bindable coverage >= 0.70;
- at least 4 of 5 assets achieve >= 0.60 coverage;
- no pixel-policy violation;
- at least one successful structured-semantic UI Capability on Notepad if its accessibility tree exposes actionable semantics;
- no more than 20% of total cases BLOCKED_ENVIRONMENT.

If Notepad exposes no actionable semantic tree for a selected Capability, report negative evidence; do not substitute a screenshot route or another GUI target.

## 9. Anti-cheating

Freeze portfolio, exact environment versions, 25-Capability sample and route definitions before binding attempts.

Do not remove hard cases or redefine user-meaningful capability after seeing accessibility/binding difficulty.

## 10. Outputs

Produce:

- exact environment/version manifest;
- frozen Capability sample;
- binding evidence per Capability;
- scripts/adapters/patch refs where used;
- structured-UI tree evidence where used;
- coverage table;
- unsupported/blocked cases;
- terminal;
- What Was NOT Proven.

## 11. What this study cannot prove

SE15 does not prove universal software coverage, long-term maintenance cost, extraction quality, Agent utility or legal authorization for arbitrary reverse engineering. It only tests the frozen portfolio under the no-pixel policy.

## 12. Protocol terminal

~~~text
SE15_PROTOCOL = READY_FOR_FRESH_REVIEW
SE15_EXECUTION = NOT_AUTHORIZED
PRODUCT_FREEZE = NO
L2_READY = NO
~~~
