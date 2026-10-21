"""No-network deterministic excerpt contract tests; no candidate truths."""
import hashlib
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.v04_mla_pilot_reducer import PilotBlocked
from scripts.v04_mla_deterministic_source_excerpt import (
    MAX_PREFIX_BYTES, _complete_prefix, compile_ffmpeg_prefix_context,
    public_excerpt_digest
)


class PrefixExcerptTests(unittest.TestCase):
    def test_short_blob_unchanged(self):
        self.assertEqual(_complete_prefix(b"first\nsecond"), b"first\nsecond")

    def test_long_blob_uses_last_complete_line_not_cherrypicked_sections(self):
        raw = (b"first evidence\n" + b"x" * (MAX_PREFIX_BYTES - 20)
               + b"\nfollow-on private topic" + b"x" * 8000)
        out = _complete_prefix(raw)
        self.assertTrue(out.endswith(b"\n"))
        self.assertTrue(len(out) <= MAX_PREFIX_BYTES)
        self.assertEqual(out, raw[:len(out)])
        self.assertNotIn(b"follow-on private topic", out)

    def test_exact_last_allowed_lf_is_included(self):
        raw = (b"x" * (MAX_PREFIX_BYTES - 1)
               + b"\n" + b"after bounded context")
        result = _complete_prefix(raw)
        self.assertEqual(len(result), MAX_PREFIX_BYTES)
        self.assertEqual(result, raw[:MAX_PREFIX_BYTES])

    def test_lf_one_byte_past_cap_blocks_not_overreads(self):
        raw = (b"x" * MAX_PREFIX_BYTES
               + b"\n" + b"outside frozen limit")
        with self.assertRaisesRegex(PilotBlocked, "complete source line"):
            _complete_prefix(raw)

    def test_substantive_automatic_stream_rules_fit_sixtyfour_kib_prefix(self):
        # Source-independent synthetic fixture: assert material semantic lines
        # are included when positioned after 32 KiB but before 64 KiB.
        raw = (b"intro\n" + b"i" * 32768 + b"\n"
               + b"for video, it is the stream with the highest resolution,\n"
               + b"for audio, it is the stream with the most channels,\n"
               + b"Data or attachment streams are not automatically selected\n"
               + b"x" * MAX_PREFIX_BYTES)
        out = _complete_prefix(raw)
        self.assertIn(b"highest resolution", out)
        self.assertIn(b"most channels", out)
        self.assertIn(b"Data or attachment streams", out)
        self.assertLessEqual(len(out), MAX_PREFIX_BYTES)

    def test_line_too_large_fails_closed(self):
        with self.assertRaisesRegex(PilotBlocked, "complete source line"):
            _complete_prefix(b"x" * (MAX_PREFIX_BYTES + 1))

    def test_missing_source_or_non_utf8_blocks(self):
        with self.assertRaises(PilotBlocked):
            _complete_prefix(b"")
        with self.assertRaises(PilotBlocked):
            _complete_prefix(b"\xff\xfe\n")
        with self.assertRaises(PilotBlocked):
            _complete_prefix(b"hi\x00there")

    def test_digest_binds_private_excerpt_bytes(self):
        x = {"schema_version": "v04-mla-ffmpeg-fixed-prefix-excerpts-v1",
             "entries": [{"excerpt_text": "actual source"}]}
        d = public_excerpt_digest(x)
        self.assertEqual(len(d), 64)
        x["entries"][0]["excerpt_text"] += " changed"
        self.assertNotEqual(d, public_excerpt_digest(x))

    def test_reject_six_slots_with_no_approved_private_markers(self):
        # Blocks even before any source read when exact frozen six slots absent.
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(PilotBlocked):
                compile_ffmpeg_prefix_context([], {}, {}, repo_root=Path(t))


if __name__ == "__main__":
    unittest.main()
