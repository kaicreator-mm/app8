# v0.4 SE11 — target identity and approval gap report

Supports [#158](https://github.com/kaicreator-mm/app8/issues/158) and [#150](https://github.com/kaicreator-mm/app8/issues/150). Unlike the final `se11-execution-target-manifest-v1`, this artifact is **not approved** and is NOT a hidden-truth corpus.

At a clean exact-SHA checkout:

```bash
python scripts/v04_se11_target_gaps.py --out /tmp/app8-se11-public-target-gaps.json
python -m pytest tests/qualification/test_v04_se11_target_gaps.py -q
```

The generator byte-pins the historical four-target candidate Git blob `ee247c95eb56081e4014210f1013fb66f783345a`. It enumerates only known source revisions, expected executable/package SHA256 values, historical runtime lanes, and unresolved eligibility gates. **Actual binary availability was separately rechecked by the operator in Issue #150**, and this script does not revalidate physical bytes or execute targets.

Remaining independent evidence:
- All targets: final reviewed source→target mapping + claim applicability references and a new exact manifest SHA256.
- pandas: freeze runtime dependencies (`numpy`, `python-dateutil`, `six`) before hidden truth/evaluation.
- LibreOffice: prove each expected claim applies to official release `26.8.1.1`, because source branches diverge; no master-only behavior automatically transferred.
- Then and **only then**: independently curate 80 private truth claims, freeze exact references and decisive fixtures, generate public commitment via existing `research/e11/stage-b/commit_hidden.py`. Allow the model to plan only after truth is sealed.

This generator never labels claims, builds a nominally approved `se11-execution-target-manifest-v1`, runs a tool, or declares SE11 PASS/Release PASS. Output is safe PUBLIC metadata; historical target readiness strings remain explicitly labeled **candidate recorded** and cannot override newer host evidence.
