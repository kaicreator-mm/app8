import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from app8.discovery import SourceError, discover_source


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "readme.md").write_bytes(b"# Example\nThis is a hypothesis, not evidence.\n")
        self.sha = hashlib.sha256((self.root / "readme.md").read_bytes()).hexdigest()
        self.kw = {"repository":"example/software", "revision":"exact-commit", "expected_sha256":self.sha}

    def test_exact_snapshot_read_only(self):
        doc = discover_source(self.root,"readme.md",**self.kw)
        self.assertEqual(doc.content_sha256,self.sha)
        self.assertEqual(doc.status,"SOURCE_ONLY_UNVERIFIED")
        self.assertIn("hypothesis",doc.text)

    def test_wrong_source_hash_fails(self):
        with self.assertRaises(SourceError):
            discover_source(self.root,"readme.md",**dict(self.kw,expected_sha256="0"*64))

    def test_parent_traversal_fails(self):
        with self.assertRaises(SourceError):
            discover_source(self.root,"../readme.md",**self.kw)

    def test_binary_pixel_input_forbidden(self):
        for filename in ("image.png", "image.svg", "scanned.pdf"):
            with self.assertRaises(SourceError):
                discover_source(self.root,filename,**self.kw)

    def test_unreviewed_format_fails(self):
        with self.assertRaises(SourceError):
            discover_source(self.root,"blob.exe",**self.kw)

    def test_size_budget_enforced(self):
        with self.assertRaises(SourceError):
            discover_source(self.root,"readme.md",max_bytes=4,**self.kw)

    def test_source_symlink_forbidden(self):
        outside=self.root/"readme.md"
        try:
            (self.root/"alias.md").symlink_to(outside)
        except OSError:
            self.skipTest("symlinks unavailable")
        with self.assertRaises(SourceError):
            discover_source(self.root,"alias.md",**self.kw)

    def test_non_utf8_rejected(self):
        (self.root/"bad.txt").write_bytes(b"\xff\x00")
        with self.assertRaises(SourceError):
            discover_source(self.root,"bad.txt",**dict(self.kw,expected_sha256=hashlib.sha256(b"\xff\x00").hexdigest()))

    def test_missing_identity_fails(self):
        with self.assertRaises(SourceError):
            discover_source(self.root,"readme.md",**dict(self.kw,revision=""))

if __name__ == "__main__":
    unittest.main()
