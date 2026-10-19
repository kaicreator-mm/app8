"""Privileged, bounded V04 P model request -> sealed response -> app8 compiler.

Only the already frozen trusted HTTPS dispatcher may make the actual model call.
No caller-supplied model text, transport, outcome, oracle, or Gold is accepted.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app8.mla.ordered_host_ledger import OrderedMLAHostLedger
from app8.mla.trusted_provider_dispatch import (
    dispatch_frozen_completion, frozen_invocation_digest,
)
from app8.storage import EvidenceStore
from scripts.v04_mla_pilot_reducer import ROOT, PilotBlocked
from scripts.v04_mla_app8_p_ingress import ingest_p_batch_via_app8


def dispatch_and_ingest_p(
    *, ledger: OrderedMLAHostLedger,
    sealed_store: EvidenceStore, asset: str,
    profile: dict, request_bytes: bytes, approved_origins: set[str],
    source_context_bytes: bytes, source_context_sha256: str,
    frozen_slots: list[dict], timeout_seconds: int = 60,
    repo_root: Path = ROOT,
) -> dict:
    """Use one frozen P reservation and compile its sealed P output.

    This cannot attest real provider identity independently: the host still
    needs external reviewer admission + public freeze witness + actual secret.
    """
    if type(ledger) is not OrderedMLAHostLedger or type(sealed_store) is not EvidenceStore:
        raise PilotBlocked("actual privileged host ledger and sealed store required")
    if (type(source_context_bytes) is not bytes
            or not 0 < len(source_context_bytes) <= 500_000
            or not isinstance(source_context_sha256, str)
            or hashlib.sha256(source_context_bytes).hexdigest() != source_context_sha256):
        raise PilotBlocked("source context must be byte-bound before billable P call")
    # Never permit the operator to supply synthetic model completions. Dispatch
    # itself revalidates all pre-output frozen GitHub witness and budget guards.
    digest = frozen_invocation_digest(
        profile, request_bytes, approved_origins=approved_origins)
    result = dispatch_frozen_completion(
        ledger=ledger, sealed_store=sealed_store, role="P", asset=asset,
        profile=profile, request_bytes=request_bytes,
        approved_origins=approved_origins, timeout_seconds=timeout_seconds)
    if (not isinstance(result, dict)
            or result.get("schema_version") != "v04-mla-https-dispatch-private-ref-v1"
            or result.get("role") != "P" or result.get("asset") != asset
            or result.get("request_envelope_sha256") != digest):
        raise PilotBlocked("P completion is not bound to trusted frozen dispatch")
    response_sha = result.get("response_sha256")
    if not isinstance(response_sha, str):
        raise PilotBlocked("P sealed response hash missing")
    # Content-addressed store checks returned actual bytes against the digest.
    raw = sealed_store.get_artifact(response_sha)
    if len(raw) > 2_000_000:
        raise PilotBlocked("P response exceeds bounded sealed size")
    try:
        doc = json.loads(raw)
    except (ValueError, UnicodeError, TypeError) as exc:
        raise PilotBlocked("stored P response is not JSON") from exc
    if (not isinstance(doc, dict)
            or doc.get("model") != profile["model_id"]
            or not isinstance(doc.get("choices"), list)
            or len(doc["choices"]) != 1
            or not isinstance(doc["choices"][0], dict)
            or doc["choices"][0].get("finish_reason") != "stop"
            or not isinstance(doc["choices"][0].get("message"), dict)
            or not isinstance(doc["choices"][0]["message"].get("content"), str)):
        raise PilotBlocked("stored P completion choice is noncanonical")
    content = doc["choices"][0]["message"]["content"]
    if not 0 < len(content.encode("utf-8")) <= 2_000_000:
        raise PilotBlocked("P output text missing or oversized")
    ingress = ingest_p_batch_via_app8(
        asset=asset,
        source_context_bytes=source_context_bytes,
        source_context_sha256=source_context_sha256,
        frozen_slots=frozen_slots, p_batch_bytes=content.encode("utf-8"),
        repo_root=repo_root,
    )
    return {
        "schema_version": "v04-mla-p-sealed-dispatch-app8-ingress-v1",
        "study_id": "V04-MLA-1",
        "asset": asset,
        "status": "HOST_P_RESPONSE_COMPILED_MODEL_PROPOSAL_ONLY",
        "request_envelope_sha256": digest,
        "response_sha256": response_sha,
        "p_batch_sha256": ingress["p_batch_sha256"],
        "app8_frozen_hypotheses_sha256": ingress["app8_frozen_hypotheses_sha256"],
        "host_recorded_dispatch_event_mac": result["response_event_mac"],
        "independent_remote_model_identity_verified": False,
        "independent_semantic_gold_verified": False,
        "real_behavior_oracle_verified": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
