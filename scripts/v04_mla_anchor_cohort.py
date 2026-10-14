"""Pre-run deterministic 6x4 anchor assignment for V04-MLA-1.

This code checks public source identities, not semantics or a chronological
freeze. A separate trusted operator must attest that the seed and assignments
were retained before P/R/X prediction transcripts.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.v04_mla_pilot_reducer import (
    ALLOWLIST, ALLOWLIST_BLOB, ASSETS, ROOT, SOURCE_BLOB,
    PilotBlocked, git_blob, is_sha256, read_json, validate
)

VERSION = "v04-mla-source-anchor-selection-r1"


def _source_list(repo_root: Path) -> dict:
    p = repo_root / ALLOWLIST
    if p.is_symlink() or not p.is_file():
        raise PilotBlocked("frozen reviewed source allowlist unavailable")
    data = p.read_bytes()
    if git_blob(data) != ALLOWLIST_BLOB:
        raise PilotBlocked("source allowlist Git blob mismatch")
    obj = read_json(data)
    if (not isinstance(obj, dict)
            or obj.get("source_pack_blob") != SOURCE_BLOB
            or not isinstance(obj.get("assets"), dict)
            or set(obj["assets"]) != set(ASSETS)):
        raise PilotBlocked("frozen source identity drift")
    return obj["assets"]


def select_anchors(seed_sha256: str, *, repo_root: Path = ROOT) -> dict:
    """Choose six distinct frozen source paths for each asset, without labels."""
    if not is_sha256(seed_sha256):
        raise PilotBlocked("reviewer-supplied 256-bit selection seed required")
    assets = _source_list(repo_root)
    slots = []
    for asset in ASSETS:
        mapping = assets[asset]
        if not isinstance(mapping, dict) or len(mapping) < 6:
            raise PilotBlocked("fewer than six frozen anchors")
        ranked = []
        for path, blob in mapping.items():
            if not isinstance(path, str) or not path or not isinstance(blob, str):
                raise PilotBlocked("malformed frozen source anchors")
            digest = hashlib.sha256(
                (seed_sha256 + ":" + asset + ":" + path + ":" + blob).encode("utf-8")
            ).hexdigest()
            ranked.append((digest, path, blob))
        ranked.sort(key=lambda row: (row[0], row[1]))
        for index, (_rank, path, blob) in enumerate(ranked[:6], 1):
            slots.append({
                "case_id": f"V04-{asset.upper()}-{index:03d}",
                "asset": asset,
                "source_anchor": {"path": path, "blob": blob},
            })
    if len(slots) != 24:
        raise PilotBlocked("wrong prospective cohort size")
    serialized = (json.dumps(slots, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False) + "\n").encode("utf-8")
    return {
        "schema_version": VERSION,
        "source_pack_git_blob": SOURCE_BLOB,
        "allowlist_git_blob": ALLOWLIST_BLOB,
        "source_selection_seed_commitment_sha256":
            hashlib.sha256(bytes.fromhex(seed_sha256)).hexdigest(),
        "anchor_assignment_sha256": hashlib.sha256(serialized).hexdigest(),
        "slots": slots,
        "pre_prediction_freeze_attested": False,
        "semantic_reference_gold_verified": False,
    }


def validate_anchor_assignment(pilot_public: dict, seed_sha256: str,
                               *, repo_root: Path = ROOT) -> dict:
    """Refuse omitted, reordered or substituted case-to-source assignments."""
    counts, cases = validate(repo_root, pilot_public)
    expected = select_anchors(seed_sha256, repo_root=repo_root)
    by_id = {item["case_id"]: item for item in cases}
    if set(by_id) != {item["case_id"] for item in expected["slots"]}:
        raise PilotBlocked("cohort case slots changed after prospective assignment")
    for slot in expected["slots"]:
        row = by_id[slot["case_id"]]
        if (row["asset"] != slot["asset"]
                or row["source_anchor"] != slot["source_anchor"]):
            raise PilotBlocked("source anchor slot differs from selected seed")
    return {
        "schema_version": "v04-mla-anchor-identity-check-v1",
        "study_id": "V04-MLA-1",
        "status": "SOURCE_ANCHOR_ASSIGNMENT_STRUCTURAL_ONLY",
        "denominator": 24,
        "asset_counts": counts,
        "anchor_assignment_sha256": expected["anchor_assignment_sha256"],
        "source_selection_seed_commitment_sha256":
            expected["source_selection_seed_commitment_sha256"],
        "pre_prediction_freeze_attested": False,
        "independent_oracle_verified": False,
        "behavior_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
