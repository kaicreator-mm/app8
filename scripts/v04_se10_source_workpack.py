#!/usr/bin/env python3
"""Generate an unlabelled SE10 source-anchor workpack. NOT semantic Gold."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST_PATH = Path("research/e10/stage-b/source_anchor_allowlist.json")
PACK_PATH = Path("docs/product/v0.1-successor/l1/SE10_SOURCE_PACK_MANIFEST.md")
EXPECTED_ALLOWLIST_BLOB = "5be0ed7674fcdfd7361a57fd4f29a6f9655c1df1"
EXPECTED_PACK_BLOB = "4b3c9b62b1899653524f19a286924f942605210a"
ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
COUNTS = {"FFmpeg":14, "pandas":21, "MinIO":18, "LibreOffice":23}


class FrozenInputError(ValueError):
    pass


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def reject_duplicate(pairs):
    values = {}
    for k, v in pairs:
        if k in values:
            raise FrozenInputError("duplicate JSON key")
        values[k] = v
    return values


def workpack(root: Path = ROOT) -> dict:
    """Never reads source contents, private Gold, reference labels or model output."""
    allow = root / ALLOWLIST_PATH
    manifest = root / PACK_PATH
    if allow.is_symlink() or manifest.is_symlink() or not allow.is_file() or not manifest.is_file():
        raise FrozenInputError("frozen input missing or symlinked")
    allow_raw, pack_raw = allow.read_bytes(), manifest.read_bytes()
    if blob_sha(allow_raw) != EXPECTED_ALLOWLIST_BLOB:
        raise FrozenInputError("source anchor allowlist exact Git blob mismatch")
    if blob_sha(pack_raw) != EXPECTED_PACK_BLOB:
        raise FrozenInputError("frozen source pack exact Git blob mismatch")
    try:
        doc = json.loads(allow_raw, object_pairs_hook=reject_duplicate,
                         parse_constant=lambda _: (_ for _ in ()).throw(FrozenInputError("nonfinite JSON")))
    except (UnicodeDecodeError, ValueError) as exc:
        raise FrozenInputError("invalid frozen source anchor allowlist") from exc
    if (not isinstance(doc, dict) or set(doc) != {"schema_version","source_pack_blob","assets"}
            or doc["schema_version"] != "se10-source-anchor-allowlist-v1"
            or doc["source_pack_blob"] != EXPECTED_PACK_BLOB
            or not isinstance(doc["assets"], dict) or set(doc["assets"]) != set(ASSETS)):
        raise FrozenInputError("allowlist source pack schema/identity mismatch")
    rows = []
    for asset in ASSETS:
        paths = doc["assets"][asset]
        if not isinstance(paths, dict) or len(paths) != COUNTS[asset]:
            raise FrozenInputError(f"{asset} frozen source anchor count mismatch")
        for path, sha in sorted(paths.items()):
            if (not isinstance(path, str) or not path or "\n" in path
                    or not isinstance(sha, str) or len(sha) != 40
                    or any(c not in "0123456789abcdef" for c in sha)):
                raise FrozenInputError(f"{asset} has malformed source path or blob")
            rows.append({"asset":asset,"source_path":path,"source_blob_sha1":sha})
    return {
        "schema_version":"app8-v04-se10-unlabelled-source-workpack-v1",
        "frozen_source_pack_git_blob":EXPECTED_PACK_BLOB,
        "frozen_anchor_allowlist_git_blob":EXPECTED_ALLOWLIST_BLOB,
        "source_anchor_count":76,
        "source_counts":COUNTS,
        "reference_target_per_asset":12,
        "anchors":rows,
        "semantic_gold_generated":False,
        "independent_gold_attestation_generated":False,
        "evaluated_prediction_generated":False,
        "se10_empirical_verdict":"NOT_RUN",
        "instruction":"Independent author: read frozen sources and create private semantic Gold outside Git; distinct reviewer must attest exact bytes. This index contains NO reference semantics or answers.",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Deterministic public source anchors, never semantic Gold")
    p.add_argument("--repo-root",type=Path,default=ROOT)
    p.add_argument("--out",type=Path,required=True)
    args = p.parse_args()
    try:
        data = workpack(args.repo_root)
    except (FrozenInputError, OSError) as exc:
        p.exit(2, f"BLOCKED: {exc}\n")
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True)+"\n",encoding="utf-8")
    print("SOURCE_ANCHORS=76 GOLD=NOT_GENERATED SE10=NOT_RUN")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
