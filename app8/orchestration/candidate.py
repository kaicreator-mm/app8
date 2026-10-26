"""Typed Capability *candidate* assembly; model output is never trusted Evidence."""
from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from app8.contracts import validate_contract
from app8.discovery import SourceDocument
from app8.orchestration.plans import PlanError

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_ID = re.compile(r"[a-z0-9][a-z0-9._-]{3,123}\Z")
_SEMANTIC = frozenset({
    "name", "purpose", "user_job", "inputs", "outputs", "variants",
    "constraints", "negative_boundaries", "failure_modes", "side_effects",
})
_BINDING = frozenset({"binding_id", "kind", "address", "preconditions", "side_effects"})


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise PlanError(f"{name}: bounded nonempty text required")
    if any(ord(ch) < 32 for ch in value):
        raise PlanError(f"{name}: control characters forbidden")
    return value


def _strings(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or len(value) > 30:
        raise PlanError(f"{name}: expected bounded string list")
    return [_text(item, name) for item in value]


def assemble_typed_candidate(
    frozen: dict[str, Any], source: SourceDocument, hypothesis_id: str,
    semantic: dict[str, Any], binding: dict[str, Any], *,
    target_identity: str, target_package_sha256: str, environment_id: str,
) -> dict[str, Any]:
    """Use the existing Capability schema, never assert a verified source/binding.

    Target identity and CLI address are *proposed* until independently
    admitted by a trusted CC02 verifier. The result contains no Evidence and
    cannot be used as an executable grant.
    """
    if not isinstance(source, SourceDocument) or not isinstance(frozen, dict):
        raise PlanError("typed source and frozen proposal required")
    if (frozen.get("schema_version") != "app8-hypothesis-freeze-v1"
            or frozen.get("origin") != "MODEL_PROPOSAL_ONLY"
            or frozen.get("evidence_claimed") is not False
            or frozen.get("source_sha256") != source.content_sha256
            or frozen.get("source_revision") != source.revision
            or not isinstance(frozen.get("proposal_sha256"), str)
            or not _SHA.fullmatch(frozen["proposal_sha256"])):
        raise PlanError("untrusted or mismatched hypothesis freeze")
    entries = frozen.get("hypotheses")
    if not isinstance(entries, list) or len(entries) < 1 or len(entries) > 100:
        raise PlanError("invalid frozen hypothesis set")
    selected = [h for h in entries if isinstance(h, dict) and h.get("id") == hypothesis_id]
    if len(selected) != 1 or not isinstance(hypothesis_id, str):
        raise PlanError("exactly one frozen hypothesis ID required")
    h = selected[0]
    _text(h.get("user_job"), "frozen job")
    if not isinstance(h.get("constraints"), list):
        raise PlanError("frozen constraints invalid")
    if not isinstance(semantic, dict) or set(semantic) != _SEMANTIC:
        raise PlanError("semantic field set mismatch")
    sem = {}
    for field in _SEMANTIC:
        sem[field] = _text(semantic[field], field) if field in {
            "name", "purpose", "user_job"} else _strings(semantic[field], field)
    if sem["user_job"] != h["user_job"]:
        raise PlanError("semantic job must match frozen model hypothesis")
    if any(item not in sem["constraints"] for item in h["constraints"]):
        raise PlanError("cannot omit frozen constraints")
    if not isinstance(binding, dict) or set(binding) != _BINDING:
        raise PlanError("binding field set mismatch")
    if binding["kind"] != "CLI":
        raise PlanError("v0.4 CC-MVP requires a proposed CLI binding")
    chosen_binding = {
        "binding_id": _text(binding["binding_id"], "binding ID"),
        "kind": "CLI",
        "address": _text(binding["address"], "binding address"),
        "preconditions": _strings(binding["preconditions"], "precondition"),
        "side_effects": _strings(binding["side_effects"], "side effect"),
    }
    if not isinstance(target_package_sha256, str) or not _SHA.fullmatch(target_package_sha256):
        raise PlanError("exact target package SHA256 required")
    cid = hypothesis_id.lower().replace("_", "-")
    if not _ID.fullmatch(cid):
        raise PlanError("invalid candidate identity")
    cap = {
        "schema_version": "app8-capability-v1",
        "capability_id": f"cap:{cid}",
        "revision": 1,
        "semantic": sem,
        "source": {
            "repository": _text(source.repository, "source repository"),
            "revision": _text(source.revision, "source revision"),
            "content_sha256": source.content_sha256,
            "license_disposition": "UNKNOWN",
        },
        "target": {
            "identity": _text(target_identity, "target identity"),
            "package_sha256": target_package_sha256,
            "mapping_relation": "UNRESOLVED",
            "environment_id": _text(environment_id, "environment ID"),
        },
        "bindings": [chosen_binding],
        "evidence_refs": [],
        "readiness": {
            "lifecycle_state": "HYPOTHESIZED",
            "export_ready": False,
            "derived_by_policy": True,
            "policy_revision": "cc01-candidate-v1",
            "reason_codes": ["MODEL_PROPOSAL_ONLY", "REAL_EVIDENCE_NOT_ADMITTED"],
        },
        "projection_refs": [],
    }
    validate_contract("capability", cap)
    return {
        "schema_version": "app8-typed-candidate-envelope-v1",
        "origin": "MODEL_PROPOSAL_ONLY",
        "proposal_sha256": frozen["proposal_sha256"],
        "source_anchor": _text(h.get("source_anchor"), "source anchor"),
        "binding_origin": "UNTRUSTED_PROPOSAL",
        "capability": deepcopy(cap),
        "real_execution_status": "NOT_RUN",
        "capability_promotion_allowed": False,
    }
