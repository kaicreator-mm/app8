#!/usr/bin/env python3
"""SE14 synthetic algorithmic tests; no frozen real search ranks are produced."""
import copy
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from bm25_fair import (BASELINE_FIELDS, CAPABILITY_EXTRA_FIELDS, CORPUS_BLOB,
                       QUERY_BLOB, QUERY_FAMILIES, SOURCE_PACK_BLOB, CONFIG_BLOB,
                       bm25_rank, tokenize, validate_index, validate_queries)

HERE = pathlib.Path(__file__).resolve().parent


def fake_index():
    entries = []
    for asset, prefix in (("FFmpeg", "F"), ("pandas", "P"), ("MinIO", "M"), ("LibreOffice", "L")):
        for i in range(1, 17):
            base = {k: None for k in BASELINE_FIELDS}
            base["operation_name"] = f"synthetic tool {prefix}{i:02d}"
            extra = {k: None for k in CAPABILITY_EXTRA_FIELDS}
            extra["semantic_goal"] = f"synthetic capability {prefix}{i:02d}"
            entries.append({"id": f"{prefix}{i:02d}", "asset": asset,
                            "source_anchor": {"path": "TEST_ONLY", "blob": "a" * 40},
                            "registry_fields": base, "capability_extra": extra})
    return {"schema_version": "se14-paired-index-v1", "source_pack_blob": SOURCE_PACK_BLOB,
            "corpus_blob": CORPUS_BLOB, "items": entries}


def fake_queries():
    items = []
    idx = 1
    for family, count in QUERY_FAMILIES.items():
        for _ in range(count):
            items.append({"id": f"Q{idx:02d}", "family": family,
                          "text": "TEST_ONLY_SYNTHETIC"})
            idx += 1
    return {"schema_version": "se14-query-corpus-v1", "query_blob": QUERY_BLOB, "queries": items}


def fake_lookup():
    src = fake_index()
    qry = fake_queries()
    return {
        "schema_version": "se14-frozen-input-lookup-v1",
        "source_pack_blob": SOURCE_PACK_BLOB, "corpus_blob": CORPUS_BLOB,
        "query_blob": QUERY_BLOB, "config_blob": CONFIG_BLOB,
        "items": {item["id"]: {
            "asset": item["asset"], "source_path": item["source_anchor"]["path"],
            "source_blob": item["source_anchor"]["blob"]
        } for item in src["items"]},
        "queries": {q["id"]: {"family": q["family"], "text": q["text"]}
                    for q in qry["queries"]}
    }


class TestFrozenBM25(unittest.TestCase):
    def test_unicode_nfkc_and_nonword_split(self):
        self.assertEqual(tokenize("ＦＦＭＰＥＧ-Video_98 foo/bar"),
                         ["ffmpeg", "video", "98", "foo", "bar"])

    def test_identical_documents_have_canonical_id_tie(self):
        self.assertEqual(bm25_rank([("B", "audio"), ("A", "audio")], "audio"),
                         [("A", bm25_rank([("B", "audio"), ("A", "audio")], "audio")[0][1]),
                          ("B", bm25_rank([("B", "audio"), ("A", "audio")], "audio")[0][1])])

    def test_no_matching_term_returns_id_ties(self):
        out = bm25_rank([("B", "video"), ("A", "audio")], "basket")
        self.assertEqual([x[0] for x in out], ["A", "B"])
        self.assertTrue(all(x[1] == 0 for x in out))

    def test_query_duplicates_do_not_gain_weight(self):
        docs = [("A", "alpha beta"), ("B", "beta")]
        self.assertEqual(bm25_rank(docs, "alpha beta"), bm25_rank(docs, "alpha alpha beta"))

    def test_expected_64_fixed_ids(self):
        docs = validate_index(fake_index(), fake_lookup())
        self.assertEqual(len(docs), 64)
        self.assertEqual(len({x[0] for x in docs}), 64)
        self.assertTrue(all(doc[2].startswith(doc[1]) for doc in docs))

    def test_rejects_missing_metadata_field(self):
        sample = fake_index()
        sample["items"][0]["registry_fields"].pop("help_examples")
        with self.assertRaises(ValueError):
            validate_index(sample, fake_lookup())

    def test_rejects_invalid_capability_extra(self):
        sample = fake_index()
        sample["items"][0]["capability_extra"]["private_label"] = "leak"
        with self.assertRaises(ValueError):
            validate_index(sample, fake_lookup())

    def test_rejects_duplicate_item(self):
        sample = fake_index()
        sample["items"][0]["id"] = "F02"
        with self.assertRaises(ValueError):
            validate_index(sample, fake_lookup())

    def test_rejects_changed_source_anchor(self):
        sample = fake_index()
        sample["items"][0]["source_anchor"]["blob"] = "b" * 40
        with self.assertRaises(ValueError):
            validate_index(sample, fake_lookup())

    def test_rejects_changed_query_text(self):
        sample = fake_queries()
        sample["queries"][0]["text"] = "secretly changed query"
        with self.assertRaises(ValueError):
            validate_queries(sample, fake_lookup())

    def test_fixed_48_query_distribution(self):
        self.assertEqual(len(validate_queries(fake_queries(), fake_lookup())), 48)

    def test_rejects_wrong_query_family_balance(self):
        sample = fake_queries()
        sample["queries"][0]["family"] = "variant"
        with self.assertRaises(ValueError):
            validate_queries(sample, fake_lookup())

    def test_rank_cli_rejects_absent_label_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "ranked.json"
            cp = subprocess.run([sys.executable, str(HERE / "bm25_fair.py"),
                                 "--paired-index", str(pathlib.Path(tmp) / "missing.json"),
                                 "--query-corpus", str(pathlib.Path(tmp) / "missing.json"),
                                 "--label-freeze-receipt", str(pathlib.Path(tmp) / "missing-receipt.json"),
                                 "--out", str(target)], capture_output=True, text=True)
            self.assertNotEqual(cp.returncode, 0)
            self.assertFalse(target.exists())

    def test_rank_cli_rejects_unreviewed_label_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = pathlib.Path(tmp)
            index = td / "index.json"
            query = td / "queries.json"
            receipt = td / "receipt.json"
            output = td / "ranked.json"
            index.write_text(json.dumps(fake_index()), encoding="utf-8")
            query.write_text(json.dumps(fake_queries()), encoding="utf-8")
            receipt.write_text(json.dumps({"schema_version": "se14-independent-label-freeze-v1",
                                           "independent_label_sha256": "a" * 64,
                                           "label_freeze_review_approved": False,
                                           "index_sha256": hashlib.sha256(index.read_bytes()).hexdigest(),
                                           "query_sha256": hashlib.sha256(query.read_bytes()).hexdigest(),
                                           "config_blob": "2149627397d2a48c58bc8b5fd0d8c654fdfbc977"}), encoding="utf-8")
            cp = subprocess.run([sys.executable, str(HERE / "bm25_fair.py"),
                                 "--paired-index", str(index), "--query-corpus", str(query),
                                 "--label-freeze-receipt", str(receipt), "--out", str(output)],
                                capture_output=True, text=True)
            self.assertNotEqual(cp.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
