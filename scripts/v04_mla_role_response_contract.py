"""Offline output-format contract gate for candidate P/R/X role batches.

Validates the exact bytes a model would return BEFORE any privileged dispatch
or sealing: strict machine-parseable JSON, exact batch identity, and the
source_anchor rendered as the frozen {path,blob} OBJECT. The v4 pilot sealed
72/72 case rows with string anchors, so every sealed batch failed the typed
ingress and no P batch reached the app8 compiler (issue #166 Step H). This
gate exists so the next round fails in rehearsal, not after payment.

Structural only: no network, no oracle, no truth, no promotion authority.
"""
from __future__ import annotations

import hashlib
import json

from scripts.v04_mla_pilot_reducer import ASSETS, PilotBlocked, read_json
from scripts.v04_mla_role_case_payloads import CASE_KEYS, KINDS, ROOT_KEYS

ROLES = ("P", "R", "X")
CASES_PER_BATCH = 6
MAX_PROPOSAL_CHARS = 2000
MAX_CONSTRAINTS = 8
MAX_CONSTRAINT_CHARS = 400
MAX_CONTENT_BYTES = 2_000_000


def _canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_response_contract(*, role: str, asset: str, content_bytes: bytes,
                               frozen_slots: list[dict],
                               source_context_sha256: str) -> dict:
    """Rehearse the typed batch contract against exact candidate content bytes.

    Fail-closed on every deviation. Returns digests and safe metadata only;
    never model prose, source text, oracle or promotion claims.
    """
    if role not in ROLES or asset not in ASSETS:
        raise PilotBlocked("unknown study role or asset")
    if type(content_bytes) is not bytes or not 0 < len(content_bytes) <= MAX_CONTENT_BYTES:
        raise PilotBlocked("candidate response content missing or oversized")
    if (content_bytes.lstrip().startswith(b"```")
            or content_bytes.rstrip().endswith(b"```")):
        raise PilotBlocked(
            "response content is not strict machine-parseable JSON: markdown "
            "code fence or wrapper detected (v4 R-role sealed-output defect)")
    batch = read_json(content_bytes)
    if not isinstance(batch, dict):
        raise PilotBlocked("response content is not a JSON object")
    if (set(batch) != ROOT_KEYS
            or batch["schema_version"] != "v04-mla-role-batch-v1"
            or batch["study_id"] != "V04-MLA-1"
            or batch["asset"] != asset or batch["role"] != role
            or batch["source_context_sha256"] != source_context_sha256):
        raise PilotBlocked("batch identity or visibility scope mismatch")
    if not isinstance(frozen_slots, list) or len(frozen_slots) != CASES_PER_BATCH:
        raise PilotBlocked("frozen six-slot cohort required")
    slots = {}
    for slot in frozen_slots:
        if (not isinstance(slot, dict) or set(slot) != {"case_id", "source_anchor"}
                or not isinstance(slot["source_anchor"], dict)
                or set(slot["source_anchor"]) != {"path", "blob"}):
            raise PilotBlocked("frozen slot shape invalid")
        if slot["case_id"] in slots:
            raise PilotBlocked("duplicate frozen case id")
        slots[slot["case_id"]] = slot["source_anchor"]
    rows = batch["cases"]
    if not isinstance(rows, list) or len(rows) != CASES_PER_BATCH:
        raise PilotBlocked("exactly six typed cases per role batch required")
    digests, seen = {}, set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != CASE_KEYS:
            raise PilotBlocked("case fields mismatch: private truth fields forbidden")
        cid = row["case_id"]
        if not isinstance(cid, str) or cid not in slots or cid in seen:
            raise PilotBlocked("duplicate, orphan or substituted case id")
        seen.add(cid)
        anchor = row["source_anchor"]
        if isinstance(anchor, str):
            raise PilotBlocked(
                "source_anchor rendered as string; the frozen {path,blob} "
                "object form is required (v4 pilot defect)")
        if anchor != slots[cid]:
            raise PilotBlocked("source anchor differs from frozen slot")
        if row["origin"] != "LLM_PROPOSED" or row["kind"] != KINDS[role]:
            raise PilotBlocked("candidate origin or hypothesis kind mismatch")
        proposal = row["proposal"]
        if (not isinstance(proposal, str) or not proposal.strip()
                or "\x00" in proposal):
            raise PilotBlocked("proposal missing or empty")
        if len(proposal) > MAX_PROPOSAL_CHARS:
            raise PilotBlocked(
                "proposal exceeds the 2000-character app8 ingress bound")
        constraints = row["constraints"]
        if (not isinstance(constraints, list) or len(constraints) > MAX_CONSTRAINTS
                or any(not isinstance(c, str) or not c.strip() or "\x00" in c
                       or len(c) > MAX_CONSTRAINT_CHARS for c in constraints)):
            raise PilotBlocked("invalid bounded candidate constraints")
        digests[cid] = _sha(_canonical(row))
    if seen != set(slots):
        raise PilotBlocked("missing case inside the response batch")
    return {
        "schema_version": "v04-mla-role-response-contract-v1",
        "study_id": "V04-MLA-1",
        "asset": asset,
        "role": role,
        "status": "RESPONSE_CONTRACT_STRUCTURAL_PASS_ONLY",
        "case_count": len(rows),
        "response_content_sha256": _sha(content_bytes),
        "case_payload_sha256": dict(sorted(digests.items())),
        "strict_json_enforced": True,
        "source_anchor_object_form_enforced": True,
        "trusted_provider_invocation_proven": False,
        "independent_semantic_gold_verified": False,
        "real_behavior_oracle_verified": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
