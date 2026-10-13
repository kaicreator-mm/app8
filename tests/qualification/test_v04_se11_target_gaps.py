"""Structural fixtures for SE11 candidate-gaps report; no hidden truth."""
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.v04_se11_target_gaps import ROOT, CANDIDATE, UnfrozenTarget, report


class TargetGapTests(unittest.TestCase):
    def test_exact_four_real_target_candidates_not_approved(self):
        data = report(ROOT)
        self.assertEqual([x["asset"] for x in data["targets"]],
                         ["FFmpeg","pandas","MinIO","LibreOffice"])
        self.assertFalse(data["final_se11_execution_target_manifest_generated"])
        self.assertFalse(data["hidden_truth_generated"])
        self.assertEqual(data["se11_empirical_status"],"NOT_RUN")
        self.assertFalse(data["product_release_qualified"])
        self.assertTrue(all(not t["independent_applicability_approved"]
                            for t in data["targets"]))

    def test_pandas_dependency_gap_is_explicit(self):
        data = report(ROOT)
        pandas = data["targets"][1]
        self.assertIn("freeze_exact_numpy_python_dateutil_six_dependencies",
                      pandas["remaining_freeze_gates"])
        self.assertEqual(len(pandas["artifact_expected_sha256"]),1)

    def test_libreoffice_diverged_cannot_silently_pass(self):
        lo = report(ROOT)["targets"][3]
        self.assertEqual(lo["candidate_repository_relation"],"DIVERGED")
        self.assertIn("prove_release_specific_applicability_for_DIVERGED_source",
                      lo["remaining_freeze_gates"])

    def test_drifted_candidate_bytes_are_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            p=root/CANDIDATE
            p.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/CANDIDATE,p)
            with p.open("ab") as stream: stream.write(b" ")
            with self.assertRaisesRegex(UnfrozenTarget,"exact Git blob drift"):
                report(root)

    def test_candidate_checkout_is_lf_pinned_on_windows(self):
        attrs = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn(
            "/research/e11/execution-targets/execution-target-selection.json text eol=lf",
            attrs.splitlines(),
        )

    def test_missing_candidate_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(UnfrozenTarget,"unavailable"):
                report(Path(td))


if __name__=="__main__":
    unittest.main()
