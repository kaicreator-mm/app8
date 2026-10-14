"""Typed per-case P/R/X asset-batch payload structural ingress.

Does not establish provider transport, truthful semantics, Gold, executable
oracle or promotion authority. Raw model prose is NEVER put in public reports.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.v04_mla_pilot_reducer import ASSETS, ROOT, PilotBlocked, read_json
from scripts.v04_mla_role_cohort_binding import bind_role_cohort

ROLES = ("P", "R", "X")
KINDS = {
    "P": "P_CAPABILITY_PREDICTION",
    "R": "R_SEMANTIC_REFERENCE_PROPOSAL",
    "X": "X_ADVERSARIAL_COUNTERHYPOTHESIS",
}
ROOT_KEYS = frozenset({
    "schema_version", "study_id", "asset", "role", "source_context_sha256", "cases",
})
CASE_KEYS = frozenset({
    "case_id", "source_anchor", "origin", "kind", "proposal", "constraints",
})


def _bounded_text(value: object, maximum: int) -> bool:
    return (isinstance(value, str) and 0 < len(value.strip()) <= maximum
            and "\x00" not in value)


def validate_role_case_payloads(pilot_public: dict, captures: dict,
                                *, repo_root: Path = ROOT) -> dict:
    """Require six unique, source-bound candidate payloads for each P/R/X batch.

    Reuse already validated output digests and role input scope. Missing,
    duplicate, crossed-asset/role, unexpected oracle/private verdict fields
    or source substitution fail closed. Returned output has only metadata.
    """
    binding = bind_role_cohort(pilot_public, captures, repo_root=repo_root)
    case_by_asset = {
        asset: {c["case_id"]: c for c in pilot_public["cases"]
                if c["asset"] == asset}
        for asset in ASSETS
    }
    digests = {}
    for asset in ASSETS:
        expected = case_by_asset[asset]
        digests[asset] = {}
        for role in ROLES:
            raw = captures[asset]["outputs"][role]
            try:
                payload = read_json(raw)
            except (PilotBlocked, TypeError, ValueError) as exc:
                raise PilotBlocked("invalid P/R/X typed case JSON") from exc
            if (not isinstance(payload, dict) or set(payload) != ROOT_KEYS
                    or payload["schema_version"] != "v04-mla-role-batch-v1"
                    or payload["study_id"] != "V04-MLA-1"
                    or payload["asset"] != asset
                    or payload["role"] != role
                    or payload["source_context_sha256"]
                       != captures[asset]["freeze"]["source_context_sha256"]):
                raise PilotBlocked("wrong role/asset/visibility bound batch")
            rows = payload["cases"]
            if not isinstance(rows, list) or len(rows) != 6:
                raise PilotBlocked("six nonreplaceable cases per role/asset required")
            seen = set()
            output = {}
            for row in rows:
                if not isinstance(row, dict) or set(row) != CASE_KEYS:
                    raise PilotBlocked("role case unexpected or private truth fields")
                cid = row["case_id"]
                if not isinstance(cid, str) or cid not in expected or cid in seen:
                    raise PilotBlocked("duplicate, orphan or crossed-role case")
                seen.add(cid)
                if (row["source_anchor"] != expected[cid]["source_anchor"]
                        or row["origin"] != "LLM_PROPOSED"
                        or row["kind"] != KINDS[role]):
                    raise PilotBlocked("source/role/candidate origin mismatch")
                if not _bounded_text(row["proposal"], 2400):
                    raise PilotBlocked("missing or oversized untrusted proposal")
                constraints = row["constraints"]
                if (not isinstance(constraints, list) or len(constraints) > 8
                        or any(not _bounded_text(c, 400) for c in constraints)):
                    raise PilotBlocked("invalid bounded candidate constraints")
                # Only hash text; do not put model prose, hypothetical hidden
                # truths, source content or real-world fixture values in Git.
                canonical = (json.dumps(row, sort_keys=True, separators=(",", ":"),
                                        ensure_ascii=False, allow_nan=False)
                             + "\n").encode("utf-8")
                output[cid] = hashlib.sha256(canonical).hexdigest()
            if seen != set(expected):
                raise PilotBlocked("missing case inside a model batch")
            digests[asset][role] = {
                "case_payload_sha256": dict(sorted(output.items())),
                "case_count": len(rows),
                "batch_transcript_sha256":
                    binding["assets"][asset]["role_output_sha256"][role],
            }
    return {
        "schema_version": "v04-mla-typed-role-case-candidates-v1",
        "study_id": "V04-MLA-1",
        "status": "STRUCTURAL_CANDIDATES_NO_ORACLE",
        "case_denominator": 24,
        "asset_count": len(ASSETS),
        "role_count": len(ROLES),
        "role_case_payloads": digests,
        "role_cohort_status": binding["status"],
        "provider_transport_and_time_freeze_verified": False,
        "user_job_precommitment_verified": False,
        "independent_reference_gold_verified": False,
        "decisive_oracle_verified": False,
        "human_review_verified": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
