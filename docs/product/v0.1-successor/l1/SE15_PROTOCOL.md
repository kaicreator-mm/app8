# SE15 Protocol — Non-Pixel Capability Exportability

Status: AMENDMENT_CANDIDATE_FOR_FRESH_REVIEW
Execution: HOLD_FOR_IDENTITY_AMENDMENT_REVIEW
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

## 2. Frozen portfolio and source/execution identity separation

Use these five **Knowledge Source / asset identities** for candidate discovery and provenance:

- FFmpeg/FFmpeg@f2bf7a2440d1e49023e4b3ed0e224a8806d388b8
- pandas-dev/pandas@82c18c170b9aea7cbb96ef54b8005bed07c94220
- minio/minio@7aac2a2c5b7c882e68c1ce017d8256be2feea27f
- LibreOffice/core@016fd5d049256dc849111f60870f15201fcd1526
- Microsoft Windows Notepad official help/package identity on the Windows execution host.

For binding/execution, freeze a separate **Execution Target identity** per asset. An Execution Target does **not** need to be built from the exact Knowledge Source commit.

Preferred Execution Target order:

1. official publisher release binary/installer/package;
2. official publisher package-registry artifact or container image;
3. publisher-recommended build with durable provenance and cryptographic identity;
4. reproducible source build only when no suitable official artifact exists or a selected Capability is explicitly source-only/unreleased.

Every target must record exact version/build/package identity, checksum or immutable digest, acquisition provenance, platform/runtime, and any publisher-provided release/tag/source mapping.

Freeze a Source -> Execution mapping class before binding work:

- `EXACT_SOURCE_BUILD`;
- `OFFICIAL_RELEASE_MAPPED`;
- `OFFICIAL_RELEASE_VERSIONED`;
- `PUBLISHER_RECOMMENDED_BUILD`;
- `SOURCE_ONLY_REQUIRED`.

A Knowledge Source claim that is not applicable to the chosen Execution Target version must be recorded as a version/currentness boundary; the target may not be changed after binding outcomes become visible merely to rescue coverage.

For ordinary released capabilities, source compilation is **not** required when a suitable official release artifact exists.

The Notepad execution target remains the exact official Microsoft package/app identity frozen on the Windows host and is exercised only through Windows UI Automation/accessibility semantics for the structured-UI lane.

Before inspecting Notepad's UIA tree, the execution manifest must freeze:

- Windows edition/build;
- Notepad package/application version;
- executable/package identity;
- UI Automation client/runtime version.

A host lacking Notepad may install the official Microsoft Notepad package before the environment manifest is frozen. After UIA inspection begins, the fifth target may not be replaced.

## 3. Frozen Capability sample and operational ranking

Exactly 5 user-meaningful Capabilities per asset are selected **before any binding/UIA inspection**.

Two independent curators rank each asset's user-facing candidate set using only the frozen official docs/tutorials/help. Candidate ID is the canonical intent label + sorted source-anchor refs. Score each candidate before resolving curator disagreement:

- documented prominence: 0–3 (front-page/common tutorial/task workflow > niche reference);
- user job completeness: 0–3 (user-observable outcome vs raw API call);
- independent example support: 0–2 (two or more user-facing workflows = 2; one = 1);
- ordinary actionability: 0–2 (concrete inputs/outcome reproducible = 2).

Rank by descending sum; tie-break by ascending canonical Candidate ID, then ascending source-anchor ID. Curators must publish individual rankings and a combined score ledger; disagreement >2 points invokes third blind curator using same rubric, median of three scores decides. Select exactly top 5 per asset. No convenience-based replacement.

For Notepad, all rankings must precede inspection of UIA controls or machine accessibility/actionability. Freeze complete 25-subject list and curator ledger.

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

## 6. Binding classification and environment BLOCKED taxonomy

Each frozen Capability is one of:

- DIRECT_NATIVE;
- THIN_ADAPTER;
- MINIMAL_FORK;
- STRUCTURED_SEMANTIC_UI;
- UNSUPPORTED;
- BLOCKED_ENVIRONMENT.

**UNSUPPORTED** includes intrinsic absent/unrecoverable binding, hard interface mismatch, unsuccessful patch/adapter, and any execution or stability failure attributable to that Capability. A difficult binding is never a host BLOCKED classification.

**BLOCKED_ENVIRONMENT** is permitted only for independently evidenced external obstacles beyond the Capability's interface, e.g., real-host hardware unavailable, OS installation prohibited by host policy, upstream distribution permanently unavailable, or externally imposed access/network/credential denial unrelated to binding feasibility. Routine setup errors, missing package that can be installed, permission requests under operator control, and generated adapter failures are NOT BLOCKED.

Required remediation before BLOCKED: (1) one documented retry on the same frozen host, (2) an independent setup diagnosis, (3) attempt normal supported installation/configuration when authorized, (4) evidence explaining why further remediation would violate the frozen environment/policy or is objectively unavailable. A second reviewer adjudicates each BLOCKED classification from exact logs **blind to aggregate coverage score**.

## 7. Primary metrics and denominators

**Primary pooled useful coverage uses ALL 25 frozen Capabilities** as denominator, including BLOCKED_ENVIRONMENT as non-success. Per-asset primary coverage denominator is always 5; no denominator shrinkage is allowed.

Also report an explicitly secondary non-blocked coverage metric, blocked cases count, route distribution, unsupported rate, Notepad structured-semantic UI success rate and pixel-policy violations.

## 8. Frozen PASS thresholds

PASS requires:

- successful bindings >=18/25 (at least 0.70, integer-rounded upward);
- at least 4/5 assets have >=3/5 successful bindings;
- zero pixel-policy violation;
- at least one successful STRUCTURED_SEMANTIC_UI Capability on Notepad **if** its pinned accessibility tree exposes actionable semantics, with no substitute route;
- BLOCKED_ENVIRONMENT <=5/25, all with independently adjudicated required remediation evidence;
- zero reclassification of intrinsic/binding failure as BLOCKED.

If Notepad exposes no actionable semantic tree for a selected Capability, preserve negative evidence; no screenshot/coordinate fallback or GUI target substitution.

## 9. Anti-cheating

Freeze exact Knowledge Source identities, Execution Target identities, Source -> Execution mapping classes/provenance, host/Notepad/UIA identities, 25-subject ranking and selection ledger, route definitions, remediation protocol, blocked taxonomy and thresholds before binding work.

Do not remove hard cases, change candidate ranks, or redefine Capability after difficulty or accessibility outcomes become visible.

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
SE15_PROTOCOL = IDENTITY_AMENDMENT_CANDIDATE_FOR_FRESH_REVIEW
SE15_EXECUTION = HOLD_FOR_IDENTITY_AMENDMENT_REVIEW
PRODUCT_FREEZE = NO
L2_READY = NO
~~~
