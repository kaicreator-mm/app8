# V04-MLA structural outcome preflight (no semantic authority)

Supports #165, #149 and #150. Depends on source-bound 24-case pilot schema from #167 and is compatible with #168 (signed execution-only bridge) and #169 (blind transcript structural capture).

\`app8.mla.preflight.reduce_evidence_preflight\` first reuses the existing byte-pinned 76-source allowlist check, exact 6×4 cohort, immutable per-case identity and fixed sampled/exception human-card selection. It then demands exactly 24 rows, rejects extra hidden/oracle/human-self-attestation fields, orphan/duplicate IDs, malformed or switched SHA256 references, and preserves blocked cases in the original denominator. It exposes the six **requested** case classes for auditing but will not mistake them for six empirically verified outcomes.

**Conservative truth fence:** public SHA256 references, model votes, J grading and self-described human decisions do not prove behavior. All requested positive/refuted/narrowed/source-only outcomes remain \`UNVERIFIED\` and requested \`BLOCKED\` remains \`BLOCKED\` until a separately reviewed trusted oracle admits real decisive observation and bounded human decisions. The public reducer **never** returns PASS or authorizes Capability promotion. The 24-case pilot remains \`PROVISIONAL\` or \`BLOCKED_HUMAN_REVIEW_BUDGET\`. The independent-oracle verification/scoring integration is **not implemented** here.

Required testing on a clean exact PR HEAD:

\`\`\`bash
python -m pytest tests/qualification/test_v04_mla_preflight.py -q
python -m pytest tests -q
\`\`\`

Synthetic tests only; no provider credentials, hidden Gold, Docker probes or real target executions. This is not the original SE10/SE11 empirical score, independent Fresh review, metric freeze, formal Release, or a successor qualification PASS.

This research qualification tool intentionally lives under `scripts/`, not the installed `app8` runtime package: it relies on a source-checkout-only immutable research allowlist. Installed-wheel behavior and product Capability authority remain unchanged.
