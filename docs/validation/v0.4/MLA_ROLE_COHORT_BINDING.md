# V04-MLA-1: four-asset P/R/X cohort-to-transcript binding

Supports #165/#166. Research-only helper \`scripts.v04_mla_role_cohort_binding.bind_role_cohort\` composes the merged public frozen-source 24-case validator (#167) and P/R/X exact-byte transcript metadata validator (#169).

A trusted caller supplies four asset-specific P/R/X batch captures, each with source context, configuration, input envelope bytes and actual output bytes. This helper recomputes all three output transcript SHA256 digests for every asset and requires every one of the **six case slots per asset** to bind to the respective exact batch commitment; swaps/orphans/extra private fields are rejected. Asset source contexts must be distinct. Same-family R/X is explicitly provisional. Returned report contains only safe digests and source cohort counts, never raw transcripts.

**Important limits:** This is **post-capture structural linkage**, not proof of provider-side invocation, temporal freezing, prompt isolation, source semantics or independent Gold. A caller can submit invented outputs; actual trusted transport receipts, private immutable chronology and deterministic target/oracle evidence are still required to admit empirical behavior. No PASS or Capability promotion is possible from this code alone.

Tests (synthetic, no providers):

\`\`\`bash
python -m pytest tests/qualification/test_v04_mla_role_cohort_binding.py -q
python -m pytest tests -q
\`\`\`

No old SE10/SE11 contract modifications. Pilot/Release NOT_RUN/NO. This is one concern/PR and is not merged without exact-HEAD test evidence.
