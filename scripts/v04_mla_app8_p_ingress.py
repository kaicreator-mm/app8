"""V04 P-origin candidate -> actual app8 hypothesis compiler boundary.

Called only AFTER a trusted host receives P bytes; it does not invoke a model,
attest provider origin, establish oracle truth, or authorize promotion.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from app8.discovery import SourceDocument
from app8.orchestration import freeze_hypotheses, PlanError
from scripts.v04_mla_pilot_reducer import (
    ALLOWLIST, ALLOWLIST_BLOB, SOURCE_BLOB, ASSETS, ROOT,
    PilotBlocked, git_blob, read_json,
)

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_BATCH_KEYS = {"schema_version", "study_id", "asset", "role", "source_context_sha256", "cases"}
_ROW_KEYS = {"case_id", "source_anchor", "origin", "kind", "proposal", "constraints"}


def ingest_p_batch_via_app8(
    *, asset: str, source_context_bytes: bytes, source_context_sha256: str,
    frozen_slots: list[dict], p_batch_bytes: bytes,
    repo_root: Path = ROOT,
) -> dict:
    """Exact six-slot P candidate bytes through app8.freeze_hypotheses.

    All returned claims remain MODEL_PROPOSAL_ONLY. A signed real HTTPS host
    receipt is a separate prerequisite for treating these as app8-run results.
    """
    if asset not in ASSETS or not isinstance(source_context_sha256, str) or not _SHA.fullmatch(source_context_sha256):
        raise PilotBlocked("invalid frozen app8 source-context identity")
    if (type(source_context_bytes) is not bytes
            or not source_context_bytes or len(source_context_bytes) > 500_000
            or hashlib.sha256(source_context_bytes).hexdigest() != source_context_sha256):
        raise PilotBlocked("private source context bytes mismatch")
    try:
        context_text = source_context_bytes.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise PilotBlocked("private source context invalid UTF-8") from exc
    if "\x00" in context_text:
        raise PilotBlocked("private source context contains binary data")
    allowlist_path = repo_root / ALLOWLIST
    if allowlist_path.is_symlink() or not allowlist_path.is_file():
        raise PilotBlocked("pinned source allowlist missing")
    allowed_bytes = allowlist_path.read_bytes()
    if git_blob(allowed_bytes) != ALLOWLIST_BLOB:
        raise PilotBlocked("pinned source allowlist drift")
    allowlist = read_json(allowed_bytes)
    if not isinstance(allowlist, dict) or allowlist.get("source_pack_blob") != SOURCE_BLOB:
        raise PilotBlocked("wrong source pack authority")
    allowed = allowlist.get("assets", {}).get(asset)
    if not isinstance(allowed, dict):
        raise PilotBlocked("pinned source asset unavailable")
    if not isinstance(frozen_slots, list) or len(frozen_slots) != 6:
        raise PilotBlocked("frozen six-slot model cohort required")
    if type(p_batch_bytes) is not bytes or not 0 < len(p_batch_bytes) <= 2_000_000:
        raise PilotBlocked("actual P output bytes missing or oversized")
    batch = read_json(p_batch_bytes)
    if (not isinstance(batch, dict) or set(batch) != _BATCH_KEYS
            or batch["schema_version"] != "v04-mla-role-batch-v1"
            or batch["study_id"] != "V04-MLA-1"
            or batch["asset"] != asset or batch["role"] != "P"
            or batch["source_context_sha256"] != source_context_sha256
            or not isinstance(batch["cases"], list) or len(batch["cases"]) != 6):
        raise PilotBlocked("P output batch identity or shape mismatch")
    expect, used_paths = {}, set()
    for slot in frozen_slots:
        if not isinstance(slot, dict) or set(slot) != {"case_id", "source_anchor"}:
            raise PilotBlocked("frozen private slot shape invalid")
        cid, anchor = slot["case_id"], slot["source_anchor"]
        if (not isinstance(cid, str) or not re.fullmatch(
                rf"V04-{asset.upper()}-00[1-6]", cid)
                or cid in expect
                or not isinstance(anchor, dict) or set(anchor) != {"path", "blob"}):
            raise PilotBlocked("frozen case ID or source anchor invalid")
        path, blob = anchor["path"], anchor["blob"]
        if (not isinstance(path, str) or not isinstance(blob, str)
                or path in used_paths or allowed.get(path) != blob):
            raise PilotBlocked("source anchor is not in reviewed frozen allowlist")
        expect[cid] = anchor
        used_paths.add(path)
    if len(expect) != 6:
        raise PilotBlocked("frozen six distinct cases required")
    seen = set()
    proposals = []
    for case in batch["cases"]:
        if not isinstance(case, dict) or set(case) != _ROW_KEYS:
            raise PilotBlocked("P candidate missing or unexpected fields")
        cid = case["case_id"]
        if cid not in expect or cid in seen:
            raise PilotBlocked("P candidate orphan/duplicated case ID")
        seen.add(cid)
        if (case["source_anchor"] != expect[cid]
                or case["origin"] != "LLM_PROPOSED"
                or case["kind"] != "P_CAPABILITY_PREDICTION"):
            raise PilotBlocked("P source scope or hypothesis kind swapped")
        statement, constraints = case["proposal"], case["constraints"]
        if (not isinstance(statement, str) or not statement.strip()
                or len(statement) > 2000 or "\x00" in statement
                or not isinstance(constraints, list) or len(constraints) > 8
                or any(not isinstance(v, str) or not v.strip()
                       or len(v) > 400 or "\x00" in v for v in constraints)):
            raise PilotBlocked("invalid bounded app8 hypothesis fields")
        anchor_text = expect[cid]["path"] + "@" + expect[cid]["blob"]
        if len(anchor_text) > 2000:
            raise PilotBlocked("source anchor text exceeds app8 contract")
        proposals.append({
            "id": cid, "user_job": statement,
            "surface": "FROZEN_SOURCE_CANDIDATE_UNVERIFIED",
            "constraints": constraints,
            "source_anchor": anchor_text,
        })
    if seen != set(expect):
        raise PilotBlocked("P predictor omitted frozen case")
    proposals.sort(key=lambda row: row["id"])
    source = SourceDocument(
        repository="app8-v04-pinned-source-context:" + asset,
        revision=SOURCE_BLOB,
        relative_path="PRIVATE_VERIFIED_MULTI_ANCHOR_CONTEXT",
        content_sha256=source_context_sha256,
        text=context_text,
    )
    try:
        frozen = freeze_hypotheses({
            "schema_version": "app8-hypotheses-v1",
            "source_sha256": source.content_sha256,
            "source_revision": source.revision,
            "hypotheses": proposals,
        }, source)
    except (PlanError, ValueError, TypeError) as exc:
        raise PilotBlocked("app8 hypothesis compiler rejected P candidates") from exc
    return {
        "schema_version": "v04-mla-app8-p-ingress-v1",
        "study_id": "V04-MLA-1",
        "asset": asset,
        "case_count": 6,
        "status": "APP8_HYPOTHESIS_COMPILER_ACCEPTED_P_CANDIDATE_ONLY",
        "p_batch_sha256": hashlib.sha256(p_batch_bytes).hexdigest(),
        "private_source_context_sha256": source_context_sha256,
        "app8_frozen_hypotheses_sha256": frozen["proposal_sha256"],
        "app8_hypotheses_origin": frozen["origin"],
        "actual_app8_predictor_transport_independently_verified": False,
        "independent_semantic_gold_verified": False,
        "execution_oracle_verified": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
