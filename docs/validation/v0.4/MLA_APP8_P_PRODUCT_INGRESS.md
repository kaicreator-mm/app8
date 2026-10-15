# V04-MLA-1 P input integration into actual app8 hypothesis contract

**State:** prospectively authored code bridge, source-only structural check. No real P model was invoked. Issue #166.

The existing `app8.orchestration.freeze_hypotheses` validates `app8-hypotheses-v1`, but it does **not** itself make an LLM request: `app8.cli.compile_preview` reads hypothesis JSON from a file. The standalone MLA HTTPS transport accepts an OpenAI-compatible model request; those two components were not an app8-specific prediction/evaluation integration by themselves. A typed `v04-mla-role-batch-v1` result from a generic LLM is therefore NOT automatically evidence of app8 product prediction.

New `scripts/v04_mla_app8_p_ingress.py` is the smallest non-network P ingress:
1. Checks the exact six independently frozen opaque IDs and original source anchors against the reviewed source allowlist Git blob, preserving 6×4 denominator.
2. Requires actual private source-context bytes SHA256 equal the prospectively selected asset context digest; do not confuse this compiled multi-anchor context with a single upstream file.
3. Parses the six typed P candidate results, rejects extra truth fields, duplicates, swapped origins/roles/sources, oversize proposals and unbounded constraints.
4. Maps all six into app8's existing `app8-hypotheses-v1` structure and **calls the real** `freeze_hypotheses`. Emits a private-safe proposal digest with `origin=MODEL_PROPOSAL_ONLY`, all truth/release/transport authority flags `false`. No stored Evidence, projection, semantic Gold or behavior-support claim is created.

This bridge is **necessary but not sufficient**: the trusted host must separately prove actual P provider transport, that P was evaluated using the app8-product prompt/spec, pre-run blind input contract, exact model/profile and 24 jobs; after P, use the same cohort-bound R/X isolation and H/oracle validation. It is false to say the generic P call became an app8 Predictor just because the compiler accepts the JSON.

No new model/Provider default is approved, and nothing here changes the original SE10/SE11 frozen protocols or declares qualified accuracy or Release PASS.
