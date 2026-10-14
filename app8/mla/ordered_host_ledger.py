"""Privileged-host-only ordered MLA model invocation ledger.

A durable SQLite BEGIN IMMEDIATE sequence plus HMAC chain proves ordering *inside
the keyed host service*. A DB snapshot is NOT an independent external time stamp;
provider identity, actual transport and task semantics still need verification.
This module never sends a request or grants oracle/release authority.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
ROLES = ("P", "R", "X")
SHA = re.compile(r"[0-9a-f]{64}\Z")
KINDS = {"FREEZE", "RESERVE", "RESPONSE"}
LIMIT_FIELDS = frozenset({
    "billing_currency", "max_total_input_tokens", "max_total_output_tokens",
    "max_total_cost_microunits", "max_total_wall_ms",
    "max_per_call_input_tokens", "max_per_call_output_tokens",
    "max_per_call_cost_microunits", "max_per_call_wall_ms",
})
METRICS = ("input_tokens", "output_tokens", "cost_microunits", "wall_ms")
CAPS = {
    "input_tokens": ("max_total_input_tokens", "max_per_call_input_tokens"),
    "output_tokens": ("max_total_output_tokens", "max_per_call_output_tokens"),
    "cost_microunits": ("max_total_cost_microunits", "max_per_call_cost_microunits"),
    "wall_ms": ("max_total_wall_ms", "max_per_call_wall_ms"),
}
FREEZE_FIELDS = frozenset({
    "schema_version", "study_id", "protocol_sha256", "scorer_sha256",
    "source_pack_git_blob", "cohort_sha256", "case_job_sha256",
    "model_input_sha256", "eligible_j_case_ids", "budget",
    "campaign_nonce", "human_selection_seed_sha256",
    "source_selection_seed_sha256", "r2_verdict_comment_id",
})


class MLAChronologyBlocked(ValueError):
    """Host-side immutable event order or usage does not satisfy the freeze."""


def _raw(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _sha(x: Any) -> bool:
    return isinstance(x, str) and SHA.fullmatch(x) is not None


def _validate_freeze(doc: dict) -> None:
    if not isinstance(doc, dict) or set(doc) != FREEZE_FIELDS:
        raise MLAChronologyBlocked("exact pre-run freeze fields required")
    if (doc["schema_version"] != "v04-mla-privileged-invocation-freeze-v1"
            or doc["study_id"] != "V04-MLA-1"
            or doc["source_pack_git_blob"]
                != "4b3c9b62b1899653524f19a286924f942605210a"):
        raise MLAChronologyBlocked("incorrect frozen study identity")
    if any(not _sha(doc[k]) for k in
           ("protocol_sha256", "scorer_sha256", "cohort_sha256", "case_job_sha256",
            "campaign_nonce", "human_selection_seed_sha256",
            "source_selection_seed_sha256")):
        raise MLAChronologyBlocked("missing pre-run campaign, seeds or protocol commitment")
    if type(doc["r2_verdict_comment_id"]) is not int or doc["r2_verdict_comment_id"] <= 0:
        raise MLAChronologyBlocked("independent reviewer comment ID must be pinned")
    pins = doc["model_input_sha256"]
    if not isinstance(pins, dict) or set(pins) != set(ASSETS):
        raise MLAChronologyBlocked("four complete asset model-input pins required")
    for asset in ASSETS:
        if (not isinstance(pins[asset], dict)
                or set(pins[asset]) != set(ROLES)
                or any(not _sha(pins[asset][role]) for role in ROLES)):
            raise MLAChronologyBlocked("12 immutable model-input pins required")
    eligible = doc["eligible_j_case_ids"]
    if (not isinstance(eligible, list) or len(eligible) > 12
            or any(not isinstance(x, str) or
                   re.fullmatch(r"V04-(FFMPEG|PANDAS|MINIO|LIBREOFFICE)-00[1-6]", x) is None
                   for x in eligible)
            or len(set(eligible)) != len(eligible)):
        raise MLAChronologyBlocked("invalid prior J eligibility cap")
    b = doc["budget"]
    if not isinstance(b, dict) or set(b) != LIMIT_FIELDS:
        raise MLAChronologyBlocked("numeric budget and currency missing")
    if (not isinstance(b["billing_currency"], str)
            or re.fullmatch(r"[A-Z]{3}", b["billing_currency"]) is None
            or any(type(b[x]) is not int or b[x] <= 0 for x in LIMIT_FIELDS
                   if x != "billing_currency")):
        raise MLAChronologyBlocked("invalid numeric budget or currency")
    for overall, single in CAPS.values():
        if b[overall] < b[single]:
            raise MLAChronologyBlocked("aggregate cap below single-call cap")


class OrderedMLAHostLedger:
    """Keyed, SQLite transaction-serialised one-campaign source-host ledger.

    Only the privileged host process may construct this with its secret key.
    No status from caller-provided bytes proves an external provider invocation.
    """

    def __init__(self, db_path: str | Path, *, host_hmac_key: bytes):
        if not isinstance(host_hmac_key, bytes) or len(host_hmac_key) < 32:
            raise MLAChronologyBlocked("privileged HMAC key required")
        # In-memory/relative paths silently destroy the promised durability,
        # and symlinked database paths are unsafe for sealed host evidence.
        if not isinstance(db_path, (str, Path)):
            raise MLAChronologyBlocked("absolute durable database path required")
        target = Path(db_path)
        if (not target.is_absolute() or target.is_symlink()
                or not target.parent.is_dir() or target.parent.is_symlink()
                or (target.exists() and not target.is_file())):
            raise MLAChronologyBlocked("durable non-symlink SQLite path required")
        self._key = host_hmac_key
        self.db = sqlite3.connect(target, isolation_level=None, timeout=15)
        try:
            self.db.execute("PRAGMA synchronous=FULL")
            self.db.execute("""CREATE TABLE IF NOT EXISTS mla_host_events(
                seq INTEGER PRIMARY KEY, kind TEXT NOT NULL,
                payload BLOB NOT NULL, prev_mac TEXT NOT NULL,
                mac TEXT NOT NULL)""")
            self.db.executescript("""
                CREATE TRIGGER IF NOT EXISTS mla_host_events_no_update
                BEFORE UPDATE ON mla_host_events BEGIN
                  SELECT RAISE(ABORT, 'immutable MLA event'); END;
                CREATE TRIGGER IF NOT EXISTS mla_host_events_no_delete
                BEFORE DELETE ON mla_host_events BEGIN
                  SELECT RAISE(ABORT, 'immutable MLA event'); END;
            """)
        except BaseException:
            self.db.close()
            raise

    def close(self) -> None:
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _load(self) -> list[dict]:
        events = []
        previous = "0" * 64
        for seq, kind, payload, prev_mac, mac in self.db.execute(
                "SELECT seq,kind,payload,prev_mac,mac FROM mla_host_events ORDER BY seq"):
            if kind not in KINDS or seq != len(events) + 1 or prev_mac != previous:
                raise MLAChronologyBlocked("host event order or HMAC chain invalid")
            unsigned = str(seq).encode() + b"\0" + kind.encode() + b"\0" + payload + b"\0" + prev_mac.encode()
            expected = hmac.new(self._key, unsigned, hashlib.sha256).hexdigest()
            if not isinstance(mac, str) or not hmac.compare_digest(mac, expected):
                raise MLAChronologyBlocked("unverified host event MAC")
            try:
                item = json.loads(payload)
                if _raw(item) != payload or not isinstance(item, dict):
                    raise ValueError("noncanonical")
            except (ValueError, UnicodeError, TypeError) as exc:
                raise MLAChronologyBlocked("corrupted event body") from exc
            events.append({"seq": seq, "kind": kind, "data": item, "mac": mac})
            previous = mac
        return events

    def _record(self, kind: str, item: dict, previous: list[dict]) -> dict:
        seq = len(previous) + 1
        prev_mac = previous[-1]["mac"] if previous else "0" * 64
        payload = _raw(item)
        unsigned = str(seq).encode() + b"\0" + kind.encode() + b"\0" + payload + b"\0" + prev_mac.encode()
        mac = hmac.new(self._key, unsigned, hashlib.sha256).hexdigest()
        self.db.execute(
            "INSERT INTO mla_host_events(seq,kind,payload,prev_mac,mac) VALUES(?,?,?,?,?)",
            (seq, kind, payload, prev_mac, mac))
        return {"seq": seq, "event_mac": mac}

    def _txn(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            return self._load()
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def freeze(self, manifest: dict) -> dict:
        """Host must commit this event before any provider transport begins."""
        _validate_freeze(manifest)
        history = self._txn()
        try:
            if history:
                raise MLAChronologyBlocked("campaign already frozen; no revision allowed")
            proof = self._record("FREEZE", manifest, history)
            self.db.execute("COMMIT")
            return {
                **proof, "status": "HOST_LOCAL_ORDERED_FREEZE_ONLY",
                "external_time_witness_verified": False,
                "provider_transport_verified": False,
                "empirical_qualification_pass": False,
            }
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def verify_precommitted_human_seed(self, public_pilot: dict) -> None:
        """Structural cross-check against pre-output human sampling commitment.

        Cannot prove when the freeze occurred. External witness gate must attest
        chronology before any live provider transport.
        """
        events = self._load()
        if not events or events[0]["kind"] != "FREEZE":
            raise MLAChronologyBlocked("no committed frozen sampling seed")
        manifest = events[0]["data"]
        _validate_freeze(manifest)
        if (not isinstance(public_pilot, dict)
                or public_pilot.get("study_id") != manifest["study_id"]
                or public_pilot.get("human_selection_seed_sha256")
                   != manifest["human_selection_seed_sha256"]):
            raise MLAChronologyBlocked("human audit selection seed drift")

    def reserve(self, *, role: str, asset: str, case_id: str | None,
                request_sha256: str) -> dict:
        """Atomically reserve worst-case per-call budget BEFORE dispatch."""
        history = self._txn()
        try:
            if not history or history[0]["kind"] != "FREEZE":
                raise MLAChronologyBlocked("no committed pre-run freeze")
            freeze = history[0]["data"]
            _validate_freeze(freeze)
            if not _sha(request_sha256):
                raise MLAChronologyBlocked("invalid frozen request SHA")
            past = [e for e in history if e["kind"] == "RESERVE"]
            done = {e["data"]["reserve_seq"] for e in history if e["kind"] == "RESPONSE"}
            if any(e["seq"] not in done for e in past):
                raise MLAChronologyBlocked("outstanding provider dispatch not settled")
            if len(past) >= 24:
                raise MLAChronologyBlocked("24-call model limit reached")
            if asset not in ASSETS or role not in (*ROLES, "J"):
                raise MLAChronologyBlocked("invalid asset or model role")
            # Execute P for every asset before any R/X/J output exists.
            # This enforces one useful ordering boundary; it does NOT prove
            # provider-side access controls or independent model identities.
            p_assets = {e["data"]["asset"] for e in past
                        if e["data"]["role"] == "P"}
            if role in ("R", "X") and len(p_assets) != 4:
                raise MLAChronologyBlocked("P prediction batches must all precede R/X")
            if role == "P" and any(e["data"]["role"] in ("R", "X", "J")
                                   for e in past):
                raise MLAChronologyBlocked("P cannot be dispatched after R/X")
            if role in ROLES:
                if (case_id is not None
                        or request_sha256 != freeze["model_input_sha256"][asset][role]
                        or any(e["data"]["asset"] == asset and e["data"]["role"] == role
                               for e in past)):
                    raise MLAChronologyBlocked("base model input mismatch or replay")
            else:
                if (case_id not in freeze["eligible_j_case_ids"]
                        or not case_id.startswith("V04-" + asset.upper() + "-")
                        or sum(e["data"]["role"] == "J" for e in past) >= 12
                        or any(e["data"]["case_id"] == case_id and e["data"]["role"] == "J"
                               for e in past)):
                    raise MLAChronologyBlocked("unapproved J escalation or hard limit")
                if sum(e["data"]["role"] != "J" for e in past) != 12:
                    raise MLAChronologyBlocked("baseline P/R/X not reserved")
            budget = freeze["budget"]
            for metric, (overall, single) in CAPS.items():
                spent_or_reserved = sum(
                    budget[single] if e["seq"] not in done else next(
                        x["data"]["usage"][metric] for x in history
                        if x["kind"] == "RESPONSE" and x["data"]["reserve_seq"] == e["seq"])
                    for e in past)
                if spent_or_reserved + budget[single] > budget[overall]:
                    raise MLAChronologyBlocked("pre-dispatch cumulative resource reservation exceeds cap")
            row = {"role": role, "asset": asset, "case_id": case_id,
                   "request_sha256": request_sha256}
            proof = self._record("RESERVE", row, history)
            self.db.execute("COMMIT")
            return {**proof, "status": "RESERVED_BEFORE_EXTERNAL_CALL",
                    "provider_transport_verified": False}
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def record_response(self, *, reserve_seq: int, response_sha256: str,
                        usage: dict) -> dict:
        """Record provider-adapter-returned digest and meters, never semantic truth."""
        history = self._txn()
        try:
            if not _sha(response_sha256):
                raise MLAChronologyBlocked("invalid provider response hash")
            if not isinstance(usage, dict) or set(usage) != set(METRICS):
                raise MLAChronologyBlocked("exact metered call usage required")
            if (type(reserve_seq) is not int
                    or reserve_seq < 2 or reserve_seq > len(history)
                    or history[reserve_seq-1]["kind"] != "RESERVE"
                    or any(e["kind"] == "RESPONSE" and e["data"]["reserve_seq"] == reserve_seq
                           for e in history)):
                raise MLAChronologyBlocked("orphan/replayed provider response")
            budget = history[0]["data"]["budget"]
            for metric, (_, cap) in CAPS.items():
                if (type(usage[metric]) is not int or usage[metric] < 0
                        or usage[metric] > budget[cap]):
                    raise MLAChronologyBlocked("provider usage exceeds reserved cap")
            proof = self._record("RESPONSE", {
                "reserve_seq": reserve_seq, "response_sha256": response_sha256,
                "usage": usage,
            }, history)
            self.db.execute("COMMIT")
            return {**proof, "status": "LOCAL_TRANSPORT_RESULT_RECORDED",
                    "provider_receipt_independently_authenticated": False,
                    "independent_behavior_oracle_verified": False,
                    "formal_product_release_qualified": False}
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def frozen_billing_currency(self) -> str:
        """Return the pinned ledger currency only after verifying its MAC chain."""
        events = self._load()
        if not events or events[0]["kind"] != "FREEZE":
            raise MLAChronologyBlocked("trusted spend freeze unavailable")
        _validate_freeze(events[0]["data"])
        return events[0]["data"]["budget"]["billing_currency"]

    def audit(self) -> dict:
        """Verify HMAC chain; never disclose raw request or provider prompt bytes."""
        events = self._load()
        return {
            "schema_version": "v04-mla-host-local-ordered-ledger-audit-v1",
            "event_count": len(events),
            "freeze_committed": bool(events and events[0]["kind"] == "FREEZE"),
            "reservation_count": sum(e["kind"] == "RESERVE" for e in events),
            "response_count": sum(e["kind"] == "RESPONSE" for e in events),
            "last_event_mac": events[-1]["mac"] if events else None,
            "host_local_hmac_chain_verified": True,
            "external_witness_verified": False,
            "provider_receipt_independently_authenticated": False,
            "independent_behavior_oracle_verified": False,
            "formal_product_release_qualified": False,
        }
