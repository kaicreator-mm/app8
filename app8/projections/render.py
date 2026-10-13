"""CLI/MCP/Skill/Docs/Search derive from one frozen Capability semantic snapshot."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from typing import Any

from app8.readiness import Readiness

KINDS = ("CLI", "MCP", "SKILL", "DOCS", "SEARCH")
HASH = re.compile(r"[0-9a-f]{64}\Z")


class ProjectionError(ValueError):
    """Projection cannot be derived without stable authority and evidence pins."""


def canonical(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def _render(kind: str, cap: dict, binding: dict | None) -> dict:
    sem = cap["semantic"]
    if kind == "CLI":
        return {"command": binding["address"] if binding else None,
                "user_job": sem["user_job"], "constraints": list(sem["constraints"]),
                "failure_modes": list(sem["failure_modes"])}
    if kind == "MCP":
        return {"tool_name": cap["capability_id"].replace(":", "_"),
                "description": sem["purpose"], "inputs": list(sem["inputs"]),
                "binding_id": binding["binding_id"] if binding else None,
                "negative_boundaries": list(sem["negative_boundaries"])}
    if kind == "SKILL":
        return {"title": sem["name"], "instructions": sem["user_job"],
                "constraints": list(sem["constraints"]),
                "failures": list(sem["failure_modes"])}
    if kind == "DOCS":
        return {"name": sem["name"], "purpose": sem["purpose"],
                "inputs": list(sem["inputs"]), "outputs": list(sem["outputs"]),
                "side_effects": list(sem["side_effects"])}
    return {"title": sem["name"], "intent": sem["user_job"],
            "negative_boundaries": list(sem["negative_boundaries"]),
            "constraints": list(sem["constraints"])}


def build_projections(capability: dict[str, Any], readiness: Readiness,
                      evidence_snapshot_sha256: str) -> dict[str, dict]:
    if not isinstance(evidence_snapshot_sha256, str) or not HASH.fullmatch(evidence_snapshot_sha256):
        raise ProjectionError("exact Evidence snapshot SHA256 is mandatory")
    cid, revision = capability["capability_id"], capability["revision"]
    if type(revision) is not int or revision < 1:
        raise ProjectionError("invalid frozen Capability revision")
    bindings = capability["bindings"]
    if any(b.get("kind") == "PIXEL" for b in bindings):
        raise ProjectionError("PIXEL_DERIVED_AUTOMATION_FORBIDDEN")
    cli = next((b for b in bindings if b["kind"] == "CLI"), None)
    mcp = next((b for b in bindings if b["kind"] in {"CLI", "LIBRARY_API", "SERVICE_API", "IPC_RPC", "OSS_ADAPTER", "STRUCTURED_UI"}), None)
    semantic_hash = digest(capability["semantic"])
    outputs = {}
    for kind in KINDS:
        supported = (kind not in {"CLI", "MCP"}) or (cli is not None if kind == "CLI" else mcp is not None)
        obj = {
            "schema_version":"app8-projection-v1", "kind":kind,
            "capability_id":cid, "capability_revision":revision,
            "semantic_sha256":semantic_hash, "evidence_snapshot_sha256":evidence_snapshot_sha256,
            "supported":supported,
            "status": "UNSUPPORTED_PROJECTION" if not supported else ("READY" if readiness.export_ready else "UNREADY"),
            "invocation_enabled":bool(readiness.export_ready and supported and kind in {"CLI", "MCP"}),
            "semantic":deepcopy(capability["semantic"]),
            "rendered":_render(kind,capability,cli if kind=="CLI" else mcp),
        }
        obj["projection_sha256"] = digest(obj)
        outputs[kind] = obj
    return outputs


def verify_projection_suite(capability: dict, snapshot_sha256: str,
                            projections: dict[str, dict]) -> bool:
    """Internal T03 verifier: detects drift. Does not itself prove real Evidence."""
    if not isinstance(projections, dict) or set(projections) != set(KINDS):
        return False
    if not isinstance(snapshot_sha256, str) or not HASH.fullmatch(snapshot_sha256):
        return False
    semantic_hash = digest(capability["semantic"])
    for kind, obj in projections.items():
        if (obj.get("kind") != kind or obj.get("capability_id") != capability["capability_id"] or
            obj.get("capability_revision") != capability["revision"] or
            obj.get("semantic_sha256") != semantic_hash or
            obj.get("semantic") != capability["semantic"] or
            obj.get("evidence_snapshot_sha256") != snapshot_sha256):
            return False
        claimed = obj.get("projection_sha256")
        unsigned = {k:v for k,v in obj.items() if k!="projection_sha256"}
        if claimed != digest(unsigned):
            return False
        if not obj.get("supported",False):
            return False
    return True
