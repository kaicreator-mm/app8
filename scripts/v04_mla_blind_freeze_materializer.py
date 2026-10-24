"""Pre-output blind-freeze materializer for V04-MLA-1 P/R/X role inputs.

Materializes, before any model response exists, the exact blind role input
metadata (the four-field envelope per role), the frozen role configuration
and the binding to the exact privileged outbound request bytes, then persists
one canonical record file and returns its SHA256 anchor.
`app8/mla/blind_capture.py::verify_blind_capture` later demands exactly those
input bytes; this module makes the freeze a produced-before-output artifact
instead of a post-hoc declaration. The v4 pilot produced no such record;
none may be created retroactively from sealed v4 results.

Structural only: no provider calls, no oracle, no truth, no promotion
authority. The function accepts no response-derived data at all. Wall-clock
"before first response" ordering is a property of the caller's trusted
orchestration, evidenced by the record's privileged request digest matching
the ordered-host-ledger reservation taken before the response event; the code
itself cannot prove time and reports that flag as False.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

from app8.mla.blind_capture import (
    CONFIG_FIELDS, INPUT_FIELDS, ROOT_FIELDS, ROLES, SOURCE_BLOB, VIS,
)
from app8.mla.trusted_provider_dispatch import (
    ProviderDispatchBlocked, frozen_invocation_digest,
)
from scripts.v04_mla_pilot_reducer import PilotBlocked, read_json

RECORD_VERSION = "v04-mla-blind-freeze-materialization-v1"
STUDY_ID = "V04-MLA-1"
FREEZE_VERSION = "v04-mla-blind-freeze-v1"
RECORD_FIELDS = frozenset({
    "schema_version", "study_id", "freeze", "role_inputs", "privileged_requests",
})
PRIVILEGED_FIELDS = frozenset({"request_envelope_sha256", "request_body_sha256"})
_IDENTITY_FIELDS = ("model_family", "provider", "model_version")
_CONFIG_DIGEST_FIELDS = ("prompt_sha256", "sampling_sha256")
_ENVELOPE_DIGEST_FIELDS = ("task_instruction_sha256",)
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def _valid_sha(value) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _privileged_request_binding(profile, request_bytes, approved_origins,
                                config: dict) -> dict:
    """Bind the frozen role config to the exact outbound privileged request."""
    if (not isinstance(profile, dict)
            or profile.get("model_family") != config["model_family"]
            or profile.get("provider") != config["provider"]):
        raise PilotBlocked(
            "privileged profile identity differs from frozen role configuration")
    try:
        digest = frozen_invocation_digest(
            profile, request_bytes, approved_origins=approved_origins)
    except ProviderDispatchBlocked as exc:
        raise PilotBlocked(
            "privileged outbound request failed frozen digest validation") from exc
    return {"request_envelope_sha256": digest,
            "request_body_sha256": _sha(request_bytes)}


def materialize_blind_freeze(*, source_context_sha256: str,
                             role_material: dict, approved_origins: set,
                             record_path: Path) -> dict:
    """Materialize and persist the pre-output blind freeze record, fail-closed.

    The record embeds the frozen P/R/X configuration, each role's exact
    four-field input envelope bytes, and the exact privileged outbound request
    binding computed with the production frozen-invocation digest. Returns
    digests, the record SHA256 anchor and the exact envelope bytes; nothing
    derived from any model response is accepted or emitted.
    """
    if not _valid_sha(source_context_sha256):
        raise PilotBlocked("invalid frozen source context digest")
    if not isinstance(role_material, dict) or set(role_material) != set(ROLES):
        raise PilotBlocked("exact P/R/X pre-output role material required")
    if not isinstance(approved_origins, set) or not approved_origins:
        raise PilotBlocked("privileged approved HTTPS origins required")
    freeze = {
        "schema_version": FREEZE_VERSION,
        "study_id": STUDY_ID,
        "source_pack_git_blob": SOURCE_BLOB,
        "frozen_before_first_response": True,
        "source_context_sha256": source_context_sha256,
        "roles": {},
    }
    role_inputs, privileged, envelope_bytes = {}, {}, {}
    for role in ROLES:
        material = role_material[role]
        expected = set(_IDENTITY_FIELDS) | set(_CONFIG_DIGEST_FIELDS) \
            | set(_ENVELOPE_DIGEST_FIELDS) | {"profile", "request_bytes"}
        if not isinstance(material, dict) or set(material) != expected:
            raise PilotBlocked("exact pre-output role material fields required")
        config = {field: material[field]
                  for field in _IDENTITY_FIELDS + _CONFIG_DIGEST_FIELDS}
        if any(not isinstance(config[field], str) or not config[field].strip()
               for field in _IDENTITY_FIELDS):
            raise PilotBlocked("model identity missing")
        if any(not _valid_sha(material[field])
               for field in _CONFIG_DIGEST_FIELDS + _ENVELOPE_DIGEST_FIELDS):
            raise PilotBlocked(
                "precommitted prompt/sampling/task digests must be SHA256")
        envelope = {
            "source_pack_git_blob": SOURCE_BLOB,
            "source_context_sha256": source_context_sha256,
            "task_instruction_sha256": material["task_instruction_sha256"],
            "visibility_scope": VIS[role],
        }
        raw = _canonical(envelope)
        config["input_sha256"] = _sha(raw)
        freeze["roles"][role] = config
        role_inputs[role] = envelope
        envelope_bytes[role] = raw
        privileged[role] = _privileged_request_binding(
            material["profile"], material["request_bytes"],
            approved_origins, config)
    record = {
        "schema_version": RECORD_VERSION,
        "study_id": STUDY_ID,
        "freeze": freeze,
        "role_inputs": role_inputs,
        "privileged_requests": privileged,
    }
    record_bytes = _canonical(record)
    record_sha256 = _persist(record_path, record_bytes)
    return {
        "schema_version": RECORD_VERSION,
        "study_id": STUDY_ID,
        "status": "PRE_OUTPUT_BLIND_FREEZE_MATERIALIZED_STRUCTURAL_ONLY",
        "record_path": str(record_path),
        "record_sha256": record_sha256,
        "role_input_sha256": {role: freeze["roles"][role]["input_sha256"]
                              for role in ROLES},
        "privileged_request_envelope_sha256": {
            role: privileged[role]["request_envelope_sha256"] for role in ROLES},
        "privileged_request_body_sha256": {
            role: privileged[role]["request_body_sha256"] for role in ROLES},
        "role_input_envelope_bytes": envelope_bytes,
        "pre_output_ordering_proven_by_code": False,
        "trusted_provider_invocation_proven": False,
        "provider_side_oracle_isolation_proven": False,
        "independent_semantic_gold_verified": False,
        "real_behavior_oracle_verified": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }


def _persist(record_path: Path, record_bytes: bytes) -> str:
    if not isinstance(record_path, Path) or not record_path.name:
        raise PilotBlocked("concrete new freeze record path required")
    if record_path.exists():
        raise PilotBlocked("freeze record already exists; refusing overwrite")
    parent = record_path.parent
    if not parent.is_dir():
        raise PilotBlocked("freeze record parent directory missing")
    tmp = parent / (record_path.name + ".materializing.tmp")
    tmp.write_bytes(record_bytes)
    os.replace(tmp, record_path)
    if record_path.read_bytes() != record_bytes:
        raise PilotBlocked("persisted freeze record bytes diverged")
    return _sha(record_bytes)


def load_materialized_freeze(record_bytes: bytes, *,
                             expected_record_sha256: str) -> dict:
    """Parse a persisted record into exact `verify_blind_capture` inputs.

    Fails closed unless the bytes hash to the materialization-time SHA256
    anchor and every embedded envelope regenerates exactly the frozen
    `input_sha256` with the pinned context and per-role visibility scope.
    """
    if not isinstance(record_bytes, bytes) or not record_bytes:
        raise PilotBlocked("freeze record bytes missing")
    if (not _valid_sha(expected_record_sha256)
            or _sha(record_bytes) != expected_record_sha256):
        raise PilotBlocked(
            "freeze record digest differs from materialization-time anchor")
    record = read_json(record_bytes)
    if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
        raise PilotBlocked("exact freeze record fields required")
    if record["schema_version"] != RECORD_VERSION or record["study_id"] != STUDY_ID:
        raise PilotBlocked("unknown freeze record identity")
    freeze = record["freeze"]
    if (not isinstance(freeze, dict) or set(freeze) != ROOT_FIELDS
            or freeze["schema_version"] != FREEZE_VERSION
            or freeze["study_id"] != STUDY_ID
            or freeze["frozen_before_first_response"] is not True
            or not _valid_sha(freeze["source_context_sha256"])
            or not isinstance(freeze["roles"], dict)
            or set(freeze["roles"]) != set(ROLES)):
        raise PilotBlocked("invalid embedded blind freeze structure")
    if (not isinstance(record["role_inputs"], dict)
            or set(record["role_inputs"]) != set(ROLES)
            or not isinstance(record["privileged_requests"], dict)
            or set(record["privileged_requests"]) != set(ROLES)):
        raise PilotBlocked("role inputs and privileged bindings required for every role")
    inputs = {}
    for role in ROLES:
        envelope = record["role_inputs"][role]
        if (not isinstance(envelope, dict) or set(envelope) != INPUT_FIELDS
                or envelope["source_pack_git_blob"] != SOURCE_BLOB
                or envelope["source_context_sha256"] != freeze["source_context_sha256"]
                or envelope["visibility_scope"] != VIS[role]
                or not _valid_sha(envelope["task_instruction_sha256"])):
            raise PilotBlocked(
                "embedded role input context, scope or digest invalid")
        config = freeze["roles"][role]
        if not isinstance(config, dict) or set(config) != CONFIG_FIELDS:
            raise PilotBlocked("embedded role configuration invalid")
        raw = _canonical(envelope)
        if _sha(raw) != config["input_sha256"]:
            raise PilotBlocked(
                "embedded role input differs from frozen exact bytes")
        binding = record["privileged_requests"][role]
        if (not isinstance(binding, dict) or set(binding) != PRIVILEGED_FIELDS
                or not _valid_sha(binding["request_envelope_sha256"])
                or not _valid_sha(binding["request_body_sha256"])):
            raise PilotBlocked("invalid privileged request binding")
        inputs[role] = raw
    return {
        "freeze": freeze,
        "role_inputs": inputs,
        "privileged_requests": record["privileged_requests"],
    }
