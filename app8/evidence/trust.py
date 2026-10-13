"""Validate authenticated external runner observations; NEVER mint behavioral truth.

An HMAC proves access to a provisioned runner secret, not OS isolation or
correctness of semantic claims. Privileged runner/secret storage and negative
escape tests are requirements of #125, not capabilities of this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_NONCE = re.compile(r"[0-9a-f]{32}\Z")
_FIELDS = frozenset({"schema_version", "nonce", "runner_id", "sandbox_policy_sha256",
                     "plan_sha256", "source_sha256", "target_sha256", "image_sha256",
                     "stdout_sha256", "stderr_sha256", "exit_code", "execution_status"})


class ReceiptError(ValueError):
    """Forged, unbound, invalid or replayed observation receipt."""


@dataclass(frozen=True)
class AcceptedObservation:
    receipt_sha256: str
    nonce: str
    status: str = "RUNNER_RECEIPT_AUTHENTICATED_NOT_BEHAVIORAL_TRUTH"
    host_sandbox_verified: bool = False
    capability_export_ready: bool = False


def _canonical(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _required_digest(value: Any, label: str) -> None:
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise ReceiptError(f"{label}: exact lowercase SHA256 required")


class ReceiptVerifier:
    """Verifier-side credential and durable nonce ledger, not a signing runner."""

    def __init__(self, *, secret: bytes, runner_id: str, policy_sha256: str, nonce_db: str | Path):
        if not isinstance(secret, bytes) or len(secret) < 32:
            raise ReceiptError("runner verification key must be >=32 private bytes")
        if not isinstance(runner_id, str) or not runner_id or len(runner_id) > 128:
            raise ReceiptError("runner identity required")
        _required_digest(policy_sha256, "sandbox policy")
        self._secret = secret
        self._runner_id = runner_id
        self._policy_sha256 = policy_sha256
        self._db = sqlite3.connect(nonce_db, isolation_level=None, timeout=15)
        self._db.execute("CREATE TABLE IF NOT EXISTS used_nonces (nonce TEXT PRIMARY KEY, receipt_sha256 TEXT NOT NULL)")

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> "ReceiptVerifier":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def verify(self, signed: dict[str, Any], *, expected_plan_sha256: str,
               expected_source_sha256: str, expected_target_sha256: str,
               expected_image_sha256: str) -> AcceptedObservation:
        for name, value in (("plan", expected_plan_sha256), ("source", expected_source_sha256),
                            ("target", expected_target_sha256), ("image", expected_image_sha256)):
            _required_digest(value, name)
        if not isinstance(signed, dict) or set(signed) != {"receipt", "mac_sha256"}:
            raise ReceiptError("signed envelope exact fields required")
        receipt, mac = signed["receipt"], signed["mac_sha256"]
        if not isinstance(receipt, dict) or set(receipt) != _FIELDS:
            raise ReceiptError("receipt exact fields required")
        _required_digest(mac, "receipt MAC")
        for name in ("sandbox_policy_sha256", "plan_sha256", "source_sha256", "target_sha256",
                     "image_sha256", "stdout_sha256", "stderr_sha256"):
            _required_digest(receipt[name], name)
        if not isinstance(receipt["nonce"], str) or not _NONCE.fullmatch(receipt["nonce"]):
            raise ReceiptError("nonce must be 16 bytes of lowercase hex")
        if (receipt["schema_version"] != "app8-observation-receipt-v1" or
                receipt["runner_id"] != self._runner_id or
                receipt["sandbox_policy_sha256"] != self._policy_sha256 or
                receipt["execution_status"] != "EXECUTED" or
                type(receipt["exit_code"]) is not int):
            raise ReceiptError("runner/policy/status/exit_code mismatch")
        expected = (expected_plan_sha256, expected_source_sha256,
                    expected_target_sha256, expected_image_sha256)
        found = tuple(receipt[key] for key in ("plan_sha256", "source_sha256",
                                               "target_sha256", "image_sha256"))
        if found != expected:
            raise ReceiptError("receipt not bound to exact frozen execution subjects")
        payload = _canonical(receipt)
        computed = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(computed, mac):
            raise ReceiptError("untrusted or modified receipt MAC")
        receipt_digest = hashlib.sha256(payload).hexdigest()
        try:
            self._db.execute("INSERT INTO used_nonces(nonce,receipt_sha256) VALUES (?,?)",
                             (receipt["nonce"], receipt_digest))
        except sqlite3.IntegrityError as exc:
            raise ReceiptError("replayed observation nonce") from exc
        return AcceptedObservation(receipt_digest, receipt["nonce"])
