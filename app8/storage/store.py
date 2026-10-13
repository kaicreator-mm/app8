"""SQLite-first append-only Evidence store; no model output is made authoritative here."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
from typing import Any, Callable

from app8.contracts import validate_contract

SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class IntegrityError(ValueError):
    """A content hash, duplicate ID, or retained record is inconsistent."""


def _canonical(doc: dict[str, Any]) -> bytes:
    return (json.dumps(doc, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class EvidenceStore:
    """Append-only, fail-closed store. Evidence validation is delegated to T01."""

    def __init__(self, root: str | Path, *, validator: Callable[[str, Any], Any] = validate_contract):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.objects = self.root / "objects" / "sha256"
        self.objects.mkdir(parents=True, exist_ok=True)
        self.validator = validator
        self.db = sqlite3.connect(self.root / "evidence.sqlite3", timeout=15)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id TEXT PRIMARY KEY,
                sha256 TEXT UNIQUE NOT NULL,
                payload BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                kind TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                payload BLOB NOT NULL
            );
            CREATE INDEX IF NOT EXISTS events_subject ON events(subject, sequence);
            CREATE TRIGGER IF NOT EXISTS evidence_update_block
                BEFORE UPDATE ON evidence BEGIN SELECT RAISE(ABORT, 'immutable evidence'); END;
            CREATE TRIGGER IF NOT EXISTS evidence_delete_block
                BEFORE DELETE ON evidence BEGIN SELECT RAISE(ABORT, 'immutable evidence'); END;
            CREATE TRIGGER IF NOT EXISTS events_update_block
                BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'immutable event'); END;
            CREATE TRIGGER IF NOT EXISTS events_delete_block
                BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'immutable event'); END;
        """)

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> "EvidenceStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def put_artifact(self, data: bytes) -> str:
        if not isinstance(data, bytes):
            raise TypeError("Artifact must be bytes")
        digest = _digest(data)
        path = self.objects / digest[:2] / digest
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            if path.read_bytes() != data:
                raise IntegrityError("Artifact hash collision or corrupted object")
        else:
            with os.fdopen(fd, "wb") as output:
                output.write(data)
                output.flush()
                os.fsync(output.fileno())
        return digest

    def get_artifact(self, digest: str) -> bytes:
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            raise IntegrityError("Invalid content hash")
        data = (self.objects / digest[:2] / digest).read_bytes()
        if _digest(data) != digest:
            raise IntegrityError("Stored artifact corrupted")
        return data

    def append_evidence(self, document: dict[str, Any]) -> str:
        self.validator("evidence", document)
        data = _canonical(document)
        digest = _digest(data)
        evidence_id = document["evidence_id"]
        with self.db:
            old = self.db.execute("SELECT sha256 FROM evidence WHERE evidence_id=?", (evidence_id,)).fetchone()
            if old is not None:
                if old[0] != digest:
                    raise IntegrityError("Evidence ID cannot be overwritten")
                return digest
            self.db.execute("INSERT INTO evidence VALUES (?,?,?)", (evidence_id, digest, data))
        return digest

    def get_evidence(self, evidence_id: str) -> dict[str, Any] | None:
        row = self.db.execute("SELECT sha256,payload FROM evidence WHERE evidence_id=?", (evidence_id,)).fetchone()
        if row is None:
            return None
        if _digest(row[1]) != row[0]:
            raise IntegrityError("Evidence payload corrupted")
        return json.loads(row[1])

    def append_event(self, subject: str, kind: str, payload: dict[str, Any]) -> int:
        if not isinstance(subject, str) or not subject or not isinstance(kind, str) or not kind:
            raise ValueError("Event subject/kind required")
        if not isinstance(payload, dict):
            raise ValueError("Event payload must be an object")
        data = _canonical(payload)
        with self.db:
            cursor = self.db.execute("INSERT INTO events (subject,kind,sha256,payload) VALUES (?,?,?,?)",
                                     (subject, kind, _digest(data), data))
        return int(cursor.lastrowid)

    def history(self, subject: str) -> list[dict[str, Any]]:
        out = []
        for seq, kind, digest, data in self.db.execute(
            "SELECT sequence,kind,sha256,payload FROM events WHERE subject=? ORDER BY sequence", (subject,)
        ):
            if _digest(data) != digest:
                raise IntegrityError("Event payload corrupted")
            out.append({"sequence": seq, "kind": kind, "payload": json.loads(data)})
        return out
