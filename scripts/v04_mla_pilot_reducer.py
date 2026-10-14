#!/usr/bin/env python3
"""V04-MLA-1 pilot preflight and fixed human-selection reducer.

This is a PUBLIC STRUCTURAL gate, not an independent software oracle or scorer.
No LLM votes, candidate labels or unchecked observation digests become truth.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = Path("research/e10/stage-b/source_anchor_allowlist.json")
ALLOWLIST_BLOB = "5be0ed7674fcdfd7361a57fd4f29a6f9655c1df1"
SOURCE_BLOB = "4b3c9b62b1899653524f19a286924f942605210a"
ASSETS = ("FFmpeg", "pandas", "MinIO", "LibreOffice")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
CASE_RE = re.compile(r"V04-[A-Z0-9_-]{3,48}\Z")
ROOT_FIELDS = {"schema_version", "study_id", "source_pack_git_blob",
               "reference_origin", "frozen_before_model_outputs",
               "human_selection_seed_sha256", "cases"}
CASE_FIELDS = {"case_id", "asset", "source_anchor", "model_prediction_sha256",
               "reference_proposer_sha256", "adversarial_challenger_sha256",
               "source_verification_claim", "behavior_observation_sha256",
               "high_impact_unresolved", "oracle_visible_to_predictor",
               "model_consensus"}
SOURCE_FIELDS = {"path", "blob"}
MAX_CASES = 24
MAX_HUMAN_CARDS = 12


class PilotBlocked(ValueError):
    pass


def read_json(raw: bytes):
    def no_duplicates(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise PilotBlocked("duplicate JSON key")
            out[k] = v
        return out

    try:
        return json.loads(
            raw, object_pairs_hook=no_duplicates,
            parse_constant=lambda _: (_ for _ in ()).throw(PilotBlocked("nonfinite number"))
        )
    except (UnicodeDecodeError, ValueError) as exc:
        raise PilotBlocked("invalid strict JSON") from exc


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def is_sha256(value) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def validate(repo: Path, record: dict) -> tuple[dict, list[dict]]:
    """Deterministic source-linked cohort validation with public-only fields."""
    path = repo / ALLOWLIST
    if path.is_symlink() or not path.is_file():
        raise PilotBlocked("reviewed source allowlist is unavailable")
    source = path.read_bytes()
    if git_blob(source) != ALLOWLIST_BLOB:
        raise PilotBlocked("reviewed allowlist Git blob drift")
    allowlist = read_json(source)
    if (not isinstance(allowlist, dict)
            or allowlist.get("source_pack_blob") != SOURCE_BLOB
            or not isinstance(allowlist.get("assets"), dict)
            or set(allowlist["assets"]) != set(ASSETS)):
        raise PilotBlocked("reviewed source allowlist schema mismatch")
    if not isinstance(record, dict) or set(record) != ROOT_FIELDS:
        raise PilotBlocked("pilot root fields mismatch")
    if (record["schema_version"] != "v04-mla-pilot-public-v1"
            or record["study_id"] != "V04-MLA-1"
            or record["source_pack_git_blob"] != SOURCE_BLOB
            or record["reference_origin"] != "LLM_PROPOSED"
            or record["frozen_before_model_outputs"] is not True
            or not is_sha256(record["human_selection_seed_sha256"])):
        raise PilotBlocked("unfrozen or invalid public pilot identity")
    cases = record["cases"]
    if not isinstance(cases, list) or len(cases) != MAX_CASES:
        raise PilotBlocked("pilot cohort must contain exactly 24 case IDs")
    counts = {a: 0 for a in ASSETS}
    seen = set()
    for item in cases:
        if not isinstance(item, dict) or set(item) != CASE_FIELDS:
            raise PilotBlocked("case fields mismatch: private semantics forbidden")
        cid, asset = item["case_id"], item["asset"]
        if not isinstance(cid, str) or not CASE_RE.fullmatch(cid) or cid in seen:
            raise PilotBlocked("invalid or duplicate opaque case ID")
        seen.add(cid)
        if asset not in ASSETS:
            raise PilotBlocked("unknown asset")
        counts[asset] += 1
        anchor = item["source_anchor"]
        if not isinstance(anchor, dict) or set(anchor) != SOURCE_FIELDS:
            raise PilotBlocked("invalid source anchor")
        loc, blob = anchor["path"], anchor["blob"]
        if (not isinstance(loc, str) or not isinstance(blob, str)
                or not SHA1_RE.fullmatch(blob)
                or allowlist["assets"][asset].get(loc) != blob):
            raise PilotBlocked("case anchor absent from reviewed source pack")
        for key in ("model_prediction_sha256", "reference_proposer_sha256",
                    "adversarial_challenger_sha256"):
            if not is_sha256(item[key]):
                raise PilotBlocked("model transcript/config commitment missing")
        if (item["source_verification_claim"] != "CANDIDATE_ONLY"
                or item["oracle_visible_to_predictor"] is not False
                or type(item["model_consensus"]) is not bool
                or type(item["high_impact_unresolved"]) is not bool):
            raise PilotBlocked("model consensus or hidden oracle is misrepresented")
        obs = item["behavior_observation_sha256"]
        if obs is not None and not is_sha256(obs):
            raise PilotBlocked("malformed observation reference")
    if any(counts[a] != 6 for a in ASSETS):
        raise PilotBlocked("pilot must have exactly six cases per asset")
    return counts, cases


def assess(repo: Path, record: dict) -> dict:
    counts, cases = validate(repo, record)
    # Critical unresolved cases are always selected, regardless of model vote.
    mandatory = {c["case_id"] for c in cases if c["high_impact_unresolved"]}
    by_id = {c["case_id"]: c for c in cases}
    selection = set(mandatory)
    # Minimum one deterministic stratum sample per asset, prior seed is explicit.
    for asset in ASSETS:
        group = [c["case_id"] for c in cases if c["asset"] == asset]
        group.sort(key=lambda cid: (
            hashlib.sha256((record["human_selection_seed_sha256"] + ":" + cid).encode()).hexdigest(),
            cid))
        selection.add(group[0])
    over_budget = len(selection) > MAX_HUMAN_CARDS
    cards = sorted(selection)
    return {
        "schema_version": "v04-mla-pilot-public-result-v1",
        "study_id": "V04-MLA-1",
        "status": "BLOCKED_HUMAN_REVIEW_BUDGET" if over_budget
                  else "PROVISIONAL_REQUIRES_REAL_ORACLE_AND_HUMAN_REVIEW",
        "source_pack_git_blob": SOURCE_BLOB,
        "case_count": len(cases),
        "asset_counts": counts,
        "human_sample_case_ids": cards,
        "human_review_card_count": len(cards),
        "human_review_card_budget": MAX_HUMAN_CARDS,
        "model_agreement_is_truth": False,
        "observation_digests_verified": False,
        "human_review_completed": False,
        "behavioral_truth_verified": False,
        "eligible_for_capability_promotion": False,
        "formal_product_release_qualified": False,
        "note": "Public-only source/identity and fixed human-selection checks; "
                "unchecked observation SHA, model agreement and author statements are not evidence.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Public-only MLA pilot preflight, never an empirical scorer")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--pilot-public", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        raw = args.pilot_public.read_bytes()
        if len(raw) > 2_000_000:
            raise PilotBlocked("oversized public input")
        output = assess(args.repo_root, read_json(raw))
    except (PilotBlocked, OSError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output["status"])
    return 2 if output["status"].startswith("BLOCKED") else 0


if __name__ == "__main__":
    raise SystemExit(main())
