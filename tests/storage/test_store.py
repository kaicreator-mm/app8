import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app8.storage import EvidenceStore, IntegrityError


def validated(kind, doc):
    assert kind == "evidence"
    return doc


class EvidenceStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = EvidenceStore(self.temp.name, validator=validated)
        self.addCleanup(self.store.close)

    def test_artifact_roundtrip_content_addressed(self):
        data = b"observed fixture log"
        digest = self.store.put_artifact(data)
        self.assertEqual(digest, hashlib.sha256(data).hexdigest())
        self.assertEqual(self.store.get_artifact(digest), data)
        self.assertEqual(self.store.put_artifact(data), digest)

    def test_artifact_path_traversal_rejected(self):
        with self.assertRaises(IntegrityError):
            self.store.get_artifact("../etc/passwd")

    def test_corrupted_artifact_detected(self):
        digest = self.store.put_artifact(b"trusted")
        (Path(self.temp.name)/"objects"/"sha256"/digest[:2]/digest).write_bytes(b"tampered")
        with self.assertRaises(IntegrityError):
            self.store.get_artifact(digest)

    def test_duplicate_evidence_id_idempotent_only(self):
        doc = {"evidence_id":"ev:1", "observation":{"execution_status":"EXECUTED"}}
        original = self.store.append_evidence(doc)
        self.assertEqual(original, self.store.append_evidence(doc))
        self.assertEqual(self.store.get_evidence("ev:1"), doc)
        with self.assertRaises(IntegrityError):
            self.store.append_evidence({"evidence_id":"ev:1", "observation":{"execution_status":"BLOCKED"}})

    def test_database_immutable_delete_update(self):
        self.store.append_evidence({"evidence_id":"ev:1"})
        with self.assertRaises(sqlite3.DatabaseError):
            self.store.db.execute("UPDATE evidence SET payload=? WHERE evidence_id='ev:1'", (b"override",))
        with self.assertRaises(sqlite3.DatabaseError):
            self.store.db.execute("DELETE FROM evidence")
        self.assertIsNotNone(self.store.get_evidence("ev:1"))

    def test_negative_event_persists_history(self):
        self.store.append_event("cap:1234", "REFUTED", {"reason":"counterexample"})
        self.store.append_event("cap:1234", "STALE", {"reason":"target changed"})
        h = self.store.history("cap:1234")
        self.assertEqual([x["kind"] for x in h], ["REFUTED", "STALE"])
        with self.assertRaises(sqlite3.DatabaseError):
            self.store.db.execute("DELETE FROM events")

    def test_persistent_db(self):
        self.store.append_evidence({"evidence_id":"ev:123"})
        with EvidenceStore(self.temp.name, validator=validated) as second:
            self.assertIsNotNone(second.get_evidence("ev:123"))

    def test_injection_bound_parameters(self):
        bad = "ev:1'); DROP TABLE evidence; --"
        self.store.append_evidence({"evidence_id":bad})
        self.assertIsNotNone(self.store.get_evidence(bad))
        self.assertEqual(self.store.history("x' OR 1=1 --"), [])

    def test_validator_must_succeed(self):
        with EvidenceStore(self.temp.name, validator=lambda *args: (_ for _ in ()).throw(ValueError("invalid"))) as s:
            with self.assertRaises(ValueError):
                s.append_evidence({"evidence_id":"ev:untrusted"})
            self.assertIsNone(s.get_evidence("ev:untrusted"))

if __name__ == "__main__":
    unittest.main()
