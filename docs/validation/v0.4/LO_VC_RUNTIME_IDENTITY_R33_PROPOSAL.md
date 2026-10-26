# v0.4 / LO-002 — prospective VC++ x64 runtime identity amendment (R33)

> **Status: PROPOSED / NOT ADOPTED.** Design-only, single-concern Product/L2 review subject. Does **not** change the original frozen Execution Target, authorize a runner, create a verified mapping approval, relax an `absent_behavior=BLOCK` gate, or qualify the product. No evaluated output has been generated under this proposal.

## Immutable evidence and source pins

- Target integration branch: `version/v0.4@73a48ffe9458746326f26eb6169f65b62928e959` (tree `d1d406c0f1616b86bb1f8c6ee659290b1465028a`), pinned ADS `v4.9.0@7929012f36a2202dcc2edc7a414b8163adc7afbd`.
- Frozen source of the preflight contract: `research/e11/execution-targets/freeze-libreoffice-official.ps1@fef62bbc2c88c06d35a055360d667849c8ffd8f0`. Its x64 VC++ detector (around lines 50–102) enumerates the two `Uninstall` trees, selects a Microsoft Publisher + GUID-keyed + exact name-family/version record; `-Install` denies when exactly one record is not found. Its manifest records `MICROSOFT_V14_X64_EXACT_NAME_FAMILY_WITH_BOUNDED_ZERO_REVISION_SUFFIX_NORMALIZATION`. **This file and historical manifest are untouched.**
- Product origin issue `#69`: target is LibreOffice official 26.8.1.1 x64 MSI, SHA256 `c6298b10cfa1748bcbedad94c62ce771e240e5021bfd6d7a967cd571b04b5312`; no package/source substitution.
- `#150 R31` (issuecomment-6408137504): the named Uninstall identity for x64 runtime 14.51.36247.0 oscillated absent/present on a shared Windows host; no observed MSI installer event explained it. It remains **P1**, and LO-002 real Oracle was **NOT_RUN**.
- `#150 R32` (issuecomment-6408449530): real Windows 64-bit PowerShell reported both `VC\\Runtimes\\x64` views `Installed=1` and `Version=v14.51.36247.00` (14/51/36247/0); `System32\\vcruntime140.dll` and `msvcp140.dll` reported FileVersion 14.51.36247.0, SHA256 respectively `D1F4225DF2CD877DBF130D5668A021DCE3F94118455FF5EC952061C30AFC9CE7` and `7C26614E1D733892C2DEAC7E245CE115504B1D80592DD0A01B08E3E5A55F89CA`. Six repeat snapshots/20 s were equal; the original Uninstall identity was still unstable. Private host evidence is reported, **not replayed by this Web-only author**.
- Microsoft first-party deployment guidance: https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files and https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist . These document the dedicated `VisualStudio\\14.0\\VC\\Runtimes\\x64` registry version and v14 binary compatibility; they do not certify the present host or this application's runtime closure.

## Product/L2 choice — two independent ways to clear this *one* runtime identity blocker

**A. Preferred where practical: clean isolated Windows baseline, original rule unchanged.** Supply an isolated host/VM with reproducible `Uninstall` identity, pinned official MSI and exact VC 14.51.36247.0, and no competing writers. Keep the frozen detector and its original `absent_behavior=BLOCK`. This avoids an architecture or contract amendment. All unrelated LO approvals still apply.

**B. Alternative (this proposal): new, prospective, host-bound runtime-receipt predicate.** Do **not** rewrite an existing frozen manifest. If Product/L2 accepts this *prospectively* and independent Reviewer passes its contract, generate a **new candidate revision** with an explicit `vc_runtime_identity_policy=MSVC14_X64_REGISTRY_DLL_V1`. For the same approved host, require together:

1. A known 64-bit Windows PowerShell process and recorded OS/arch, exact intended LO executable and MSI hashes; detect registry view deliberately (no silent x86/x64 redirection or user-local substitute).
2. Dedicated **x64** `HKLM\\SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64` (or its explicit 32-bit view, when documented and pinned for this host) with `Installed=1` and `Major=14, Minor=51, Bld=36247, Rbld=0`, compatible `Version=v14.51.36247.00`. For R32's host the **both-view equality** is an additional observed identity pin, not an automatic requirement for every other Windows installation.
3. `C:\\Windows\\System32\\vcruntime140.dll` and `msvcp140.dll` both present, exact 14.51.36247.0 file versions, **both R32 SHA256 digests**, valid Microsoft Authenticode where meaningful. Unexpected architecture, absent/changed DLL, version mismatch or signature failure -> **BLOCK**. Do not equate matching `FileVersion` text alone with verified binary authenticity.
4. Two independently timestamped, non-mutating receipts under the same exact environment identity, one **immediately before** and one **immediately after** the approved *non-decisive* instrument calibration. If values drift or an unexplained writer affects trusted runtime values -> stop/fail closed. The six short R32 samples are *preliminary*, not replacement evidence for this before/after tuple.
5. Record both original legacy `Uninstall` observation and new values without deleting unfavorable evidence. `original_named_gate=BLOCKED` remains an explicit historical field. Only an accepted, separately reviewed **successor predicate** may claim `new_runtime_receipt=PASS`; never rewrite old PASS/FAIL/NOT_RUN.
6. Negative tests: wrong arch, absent `Installed`, malformed/mismatched registry versions, missing/wrong-hash DLL, failed signature, changing between receipts, untrusted/conflicting registry views, missing host/LO binding, and replay of an R32 prior-host receipt on a new candidate. On any ambiguity, **BLOCK**.

This runtime predicate would verify only **VC++ dependency presence and identity**, not LibreOffice PageRange behavior, the 12-page fixture, model score, MSI↔source build provenance or the independent DIVERGED authority's wider claim.

## Execution and authority sequence

`Product/L2 scoped decision (A or B)` → `independent source/contract review` → if B: `one-concern additive host predicate implementation + deterministic negatives` → `fresh exact-version-baseline / alternate-host review` → `operator approval for Xpdf reader + headless instrument/calibration` → `reviewed out-of-band authority root provisioning and independent claim-scoped DIVERGED admission` → `real signed receipt + deterministic Oracle` → `bounded H decisions / honest SE10+SE11 terminal` → `#151 release qualification`.

**Strict non-goals:** no unilateral `-Install`, repair, uninstall, registry write, shared VC bundle replacement, arbitrary version upgrade, public root-key preimage, hidden-fixture inspection, true-oracle claim, paid LLM dispatch or `main` merge. Kimi R31's `APPROVE_EXPECTATION_SET_APPLICABILITY` is bounded and not a target behavior execution permit. MinIO-005 remains separately authorized and blocked; this proposed contract does not serialize its lane.

## Current disposition and review request

```text
REVIEW_SCOPE=PROSPECTIVE_VC_IDENTITY_PREDICATE_ONLY
PROPOSED_CHOICE=B_IF_CLEAN_BASELINE_A_NOT_AVAILABLE
PRODUCT_L2_FREEZE=NO
INDEPENDENT_REVIEW=NOT_RUN
RUNNER_PATCH=NOT_RUN
CURRENT_UNINSTALL_GATE=BLOCKED
REAL_LIBREOFFICE_ORACLE=NOT_RUN
FORMAL_V04_RELEASE_QUALIFIED=NO
```

Reviewer must decide whether the exact observed 14.51.36247.0 **runtime binary identity** is sufficient for the LO-002 invocation dependency under approved trust assumptions and whether both-view mismatches or unknown external writers necessitate further P1 blockers. Do not sign off merely because the first-party docs explain runtime registry versioning.
