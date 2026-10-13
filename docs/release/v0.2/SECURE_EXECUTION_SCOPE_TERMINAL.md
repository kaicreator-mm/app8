# app8 v0.2 — Secure Execution Scope Terminal

Status: **SECURE_EXECUTION_ENGINEERING_SCOPE_COMPLETE / FORMAL_RELEASE_NOT_QUALIFIED**  
Controller: [Issue #123](https://github.com/kaicreator-mm/app8/issues/123)  
Baseline after evidence-integrity fix PR #136: `51b3aa9cd6310ef58309b011be101b0d63a3c9eb`.  
Independent-human Product review: owner waiver #92, **not** an independent-review PASS.

## Final decision

The v0.2 **Docker execution/Evidence pipeline engineering scope** is complete and all scoped accepted tests have recorded outcomes. This does not mean that the entire app8 product is production-ready, nor does it create a release tag or publish a signed distribution.

```text
V02_SANDBOX_POLICY=IMPLEMENTED
V02_DANGEROUS_LEGACY_SUBPROCESS_FALLBACK=DISABLED
V02_REAL_HOST_ISOLATION_PROBES=22/22_PASS_ACROSS_TWO_HOSTS_WITH_PINNED_POLICY
V02_RUNNER_R1_REAL_HOST=42/42_PASS_ACROSS_TWO_HOSTS_ON_PR134_SOURCE
V02_RUNNER_R1_AUTHENTICATED_EVIDENCESTORE_INGRESS=PASS_SCOPED
V02_POST_MERGE_EVIDENCE_INTEGRITY_FIX=#136_MERGED
V02_FIX_WINDOWS_UNIT_TESTS=72/72_PASS
V02_FIX_UBUNTU_TARGETED_UNIT_TESTS=8/8_PASS
V02_FIX_FULL_REAL_DOCKER_CROSS_HOST_RETARGET=NOT_RUN
V02_FULL_PRODUCT_RELEASE_QUALIFICATION=NO
SE10_SE11_EMPIRICAL_PRODUCT_EFFECTIVENESS=UNPROVEN
```

## Evidence chain and bounded authority

| Work item | Outcome | Scope |
|---|---|---|
| #129 / PR #130 | Closed, unit-tested | Unsafe direct subprocess execution disabled, even with caller isolation booleans |
| #124 / PR #127 | Closed, policy tests 16/16 PASS | Digest-pinned Docker arguments, network none, read-only, nonroot, cap drop, bounded resources |
| #125 | Closed, Windows 11/11 + Ubuntu 11/11 PASS | Real-host isolation negatives on fixed Docker Engine versions and cached image digest |
| #126 / PR #128, #131, #132 | Closed, targeted tests PASS | Signed full Evidence v2, private HMAC verification, anti-replay, EvidenceStore ingress, default-deny Readiness |
| #133 / PR #134 | Closed, Windows 21/21 + Ubuntu 21/21 PASS | Real Docker host runner, external wall/output enforcement, signed smoke evidence, scoped synthetic readiness |
| #135 / PR #136 | Closed, Windows unit 72/72 + Ubuntu targeted unit 8/8 PASS | Correctly BLOCK limit-aborted/truncated probes and reject a modified plan/command before execution |

Source authority:
- #125 real host terminal comment `6146523804`.
- #133 real host terminal comment `6148223178`, PR #134 merged at `38ef466abee2e7b76b9950270ba65148549b576f`.
- #135 exact-HEAD unit terminal comment `6149598918`, fix HEAD `be0c310fb2a7d114b1404e7619ee17ebadebf1e4`, tree `27dd0579d6cd2b64c6d2e40a8b6fd6bd13e7d082`, squash merge `51b3aa9cd6310ef58309b011be101b0d63a3c9eb`.

The #135 tests exercised the source and fake-Docker regression harness under Windows and WSL2 Ubuntu. They are **not a fresh full real-Docker cross-host validation of PR #136's changed decision logic**. The #125 isolation policy bytes were unchanged; its 22 negative probes were reused rather than repeated. These distinctions must remain visible.

## Product capability status

The secure runner can execute explicitly allowlisted and digest-pinned commands on the documented hosts, capture bounded real observations, generate HMAC-signed Evidence, append it to an immutable store, and apply scoped readiness policy. A smoke Capability validated under the pinned execution subject may reach scoped `EXPORT_READY`; it cannot be generalized to arbitrary software or user jobs.

**Not proven:** SE10 capability extraction precision/coverage, SE11 general adversarial falsification effectiveness, other SE12–SE16 product claims, broad untrusted image/command safety, unrestricted platform compatibility, live MCP/Skill delivery, general-availability release stability.

The legacy `app8.execution.adapter.run_invocation` remains disabled. Model proposals are never direct execution authority; frozen approved plans, exact target identities, privileged key custody, currentness and real observations are required.

## Release and next-scope decision

```text
VERSION_TAG_CREATED=NO
GITHUB_RELEASE_PUBLISHED=NO
V02_ENGINEERING_SCOPE_ACCEPTED=YES_WITH_EXPLICIT_TEST_SCOPE
FORMAL_RELEASE_PASS=NO
MODEL_SELF_CERTIFIED_EVIDENCE=FORBIDDEN
PRODUCT_EMPIRICAL_SE10_SE11=UNPROVEN
REOPEN_V01_PRODUCT_RESEARCH_FOR_V02=NO
```

Full product Release Qualification, if later requested, requires a separately scoped release plan with real target capability evaluation, failure/currentness cases and coverage evidence; a successful smoke test is not that evaluation.

Do not rerun the already completed LibreOffice #69 installation, v0.1 two-host preflight or #125 isolation suite without a relevant baseline/security change. No new real-host task is required merely to close this **engineering scope**.
