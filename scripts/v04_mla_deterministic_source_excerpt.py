"""V04-MLA-1 deterministic frozen-source excerpt compiler, not an Oracle.

Only FFmpeg six-slot source *context* compression; never change case IDs,
original full Git blob identities, case jobs or the public denominator.
Private checked blobs / audit markers MUST stay outside the Git repository.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.v04_mla_pilot_reducer import (
    ALLOWLIST, ALLOWLIST_BLOB, SOURCE_BLOB, PilotBlocked,
    git_blob, read_json, ROOT,
)

SCHEMA = "v04-mla-ffmpeg-fixed-prefix-excerpts-v1"
MAX_PREFIX_BYTES = 65536
MAX_TOTAL_EXCERPT_BYTES = 393216
EXPECTED_IDS = frozenset(f"V04-FFMPEG-{i:03d}" for i in range(1, 7))
FIELDS = frozenset(("case_id", "source_anchor"))


def _complete_prefix(raw: bytes) -> bytes:
    """Full raw bytes if short; otherwise longest whole-line prefix <= 32 KiB."""
    if type(raw) is not bytes or not raw or b"\x00" in raw:
        raise PilotBlocked("missing or invalid frozen source bytes")
    if len(raw) <= MAX_PREFIX_BYTES:
        result = raw
    else:
        pos = raw.rfind(b"\n", 0, MAX_PREFIX_BYTES)
        if pos < 0:
            raise PilotBlocked("cannot excerpt a complete source line")
        result = raw[:pos + 1]
    try:
        result.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise PilotBlocked("frozen source excerpt is not UTF-8") from exc
    if len(result) > MAX_PREFIX_BYTES:
        raise PilotBlocked("excerpt exceeds frozen per-source byte cap")
    return result


def compile_ffmpeg_prefix_context(
    frozen_slots: list[dict],
    original_blobs_by_path: dict[str, bytes],
    private_required_markers_by_case: dict[str, list[str]],
    *, repo_root: Path = ROOT,
) -> dict:
    """Compile six unchanged frozen source slots from exact upstream blob bytes.

    Marker checks are a PRIVATE pre-result audit: they cannot affect which
    excerpt bytes are selected. A missing required topic fails closed.
    """
    source_path = repo_root / ALLOWLIST
    if source_path.is_symlink() or not source_path.is_file():
        raise PilotBlocked("frozen source allowlist missing")
    raw_allowlist = source_path.read_bytes()
    if git_blob(raw_allowlist) != ALLOWLIST_BLOB:
        raise PilotBlocked("source allowlist Git identity drift")
    allowlist = read_json(raw_allowlist)
    if (not isinstance(allowlist, dict)
            or allowlist.get("source_pack_blob") != SOURCE_BLOB
            or not isinstance(allowlist.get("assets"), dict)
            or not isinstance(allowlist["assets"].get("FFmpeg"), dict)):
        raise PilotBlocked("source anchor allowlist invalid")
    if not isinstance(frozen_slots, list) or len(frozen_slots) != 6:
        raise PilotBlocked("FFmpeg six-slot denominator cannot change")
    if not isinstance(original_blobs_by_path, dict) or not isinstance(private_required_markers_by_case, dict):
        raise PilotBlocked("private source bytes and claim coverage audit required")
    ids, paths, selected = set(), set(), []
    for slot in frozen_slots:
        if not isinstance(slot, dict) or set(slot) != FIELDS:
            raise PilotBlocked("exact private anchor slot fields required")
        cid = slot["case_id"]
        anchor = slot["source_anchor"]
        if (cid not in EXPECTED_IDS or cid in ids
                or not isinstance(anchor, dict)
                or set(anchor) != {"path", "blob"}):
            raise PilotBlocked("unknown or duplicate FFmpeg source slot")
        ids.add(cid)
        path, sha = anchor["path"], anchor["blob"]
        if (not isinstance(path, str) or path in paths
                or not isinstance(sha, str)
                or allowlist["assets"]["FFmpeg"].get(path) != sha):
            raise PilotBlocked("unapproved or duplicated source anchor")
        paths.add(path)
        data = original_blobs_by_path.get(path)
        if type(data) is not bytes or git_blob(data) != sha:
            raise PilotBlocked("upstream source bytes do not match pinned Git blob")
        prefix = _complete_prefix(data)
        txt = prefix.decode("utf-8")
        markers = private_required_markers_by_case.get(cid)
        if (not isinstance(markers, list) or not markers or len(markers) > 12
                or any(not isinstance(v, str) or not (1 <= len(v) <= 180)
                       or v not in txt for v in markers)):
            raise PilotBlocked("required frozen claim evidence missing from excerpt")
        selected.append({
            "case_id": cid,
            "source_anchor": {"path": path, "blob": sha},
            "original_source_bytes": len(data),
            "excerpt_bytes": len(prefix),
            "excerpt_sha256": hashlib.sha256(prefix).hexdigest(),
            "excerpt_kind": "COMPLETE_BLOB" if len(prefix) == len(data) else "PREFIX_WITH_OMITTED_TAIL",
            "excerpt_text": txt,
        })
    if (ids != EXPECTED_IDS or set(original_blobs_by_path) != paths
            or set(private_required_markers_by_case) != ids):
        raise PilotBlocked("frozen six source anchors or private claim audit incomplete")
    selected.sort(key=lambda row: row["case_id"])
    if sum(row["excerpt_bytes"] for row in selected) > MAX_TOTAL_EXCERPT_BYTES:
        raise PilotBlocked("unbounded source context")
    return {
        "schema_version": SCHEMA,
        "study_id": "V04-MLA-1",
        "source_pack_git_blob": SOURCE_BLOB,
        "asset": "FFmpeg",
        "selection_rule": "FIRST_65536_BYTES_LAST_COMPLETE_NEWLINE",
        "case_denominator_preserved": 6,
        "source_context_is_partial": any(row["excerpt_kind"] != "COMPLETE_BLOB" for row in selected),
        "oracle_or_behavior_verified": False,
        "entries": selected,
    }


def public_excerpt_digest(private_compiled: dict) -> str:
    """Hash canonical *private* excerpt structure; never publish its raw text."""
    if not isinstance(private_compiled, dict) or private_compiled.get("schema_version") != SCHEMA:
        raise PilotBlocked("excerpt compiler output required")
    payload = (json.dumps(private_compiled, ensure_ascii=False,
                          sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
