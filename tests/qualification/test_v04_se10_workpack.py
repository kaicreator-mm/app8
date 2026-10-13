"""Synthetic structural tests for source workpack, never scored SE10 evidence."""
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.v04_se10_source_workpack import (
    ALLOWLIST_PATH, PACK_PATH, ROOT, FrozenInputError, workpack
)


class SourceWorkpackTests(unittest.TestCase):
    def test_exact_76_unlabelled_anchors(self):
        result = workpack(ROOT)
        self.assertEqual(result["source_anchor_count"], 76)
        self.assertEqual(result["source_counts"],
                         {"FFmpeg":14,"pandas":21,"MinIO":18,"LibreOffice":23})
        self.assertEqual(len(result["anchors"]), 76)
        self.assertFalse(result["semantic_gold_generated"])
        self.assertFalse(result["independent_gold_attestation_generated"])
        self.assertEqual(result["se10_empirical_verdict"], "NOT_RUN")
        self.assertFalse(any("truth_class" in a or "canonical_identity" in a
                             for a in result["anchors"]))

    def test_stable_order_and_repeated_output(self):
        a = workpack(ROOT)
        b = workpack(ROOT)
        self.assertEqual(a, b)
        self.assertEqual(a["anchors"][:14],
                         sorted(a["anchors"][:14], key=lambda x:x["source_path"]))

    def _clone_inputs(self, dst: Path):
        for part in (ALLOWLIST_PATH, PACK_PATH):
            target = dst / part
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / part, target)

    def test_allowlist_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._clone_inputs(root)
            with (root / ALLOWLIST_PATH).open("ab") as output:
                output.write(b" ")
            with self.assertRaisesRegex(FrozenInputError, "allowlist exact Git blob mismatch"):
                workpack(root)

    def test_source_manifest_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._clone_inputs(root)
            with (root / PACK_PATH).open("ab") as output:
                output.write(b" ")
            with self.assertRaisesRegex(FrozenInputError, "source pack exact Git blob mismatch"):
                workpack(root)

    def test_missing_file_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(FrozenInputError, "missing or symlinked"):
                workpack(Path(td))


if __name__ == "__main__":
    unittest.main()
