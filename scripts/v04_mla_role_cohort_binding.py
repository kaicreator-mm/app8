"""Source-bound four-asset batch transcript binding for V04-MLA-1.

This is a structural consistency gate for trusted orchestration input.
It does not attest provider invocation, chronological freeze, or oracle truth.
"""
from __future__ import annotations

from pathlib import Path

from app8.mla.blind_capture import BlindCaptureBlocked, verify_blind_capture
from scripts.v04_mla_pilot_reducer import ASSETS, ROOT, PilotBlocked, validate

_CAPTURE_FIELDS = frozenset({"freeze", "inputs", "outputs"})
_DIGEST_BY_ROLE = {
    "P": "model_prediction_sha256",
    "R": "reference_proposer_sha256",
    "X": "adversarial_challenger_sha256",
}


def bind_role_cohort(pilot_public: dict, captures: dict,
                     *, repo_root: Path = ROOT) -> dict:
    """Require four distinct P/R/X asset captures and bind all 24 case hashes.

    Batch transcripts are per asset; all six case slots for a given asset
    deliberately bind to the same role batch transcript digest.
    """
    counts, cases = validate(repo_root, pilot_public)
    if not isinstance(captures, dict) or set(captures) != set(ASSETS):
        raise PilotBlocked("exactly four asset-specific role captures required")
    output = {}
    context_digests = set()
    all_r_x_family_independent = True
    for asset in ASSETS:
        raw = captures[asset]
        if not isinstance(raw, dict) or set(raw) != _CAPTURE_FIELDS:
            raise PilotBlocked("trusted capture envelope fields are incomplete")
        try:
            report = verify_blind_capture(raw["freeze"], raw["inputs"],
                                          raw["outputs"])
        except (BlindCaptureBlocked, ValueError, TypeError) as exc:
            raise PilotBlocked("invalid P/R/X blind capture for " + asset) from exc
        context = raw["freeze"]["source_context_sha256"]
        if context in context_digests:
            raise PilotBlocked("asset source contexts cannot be reused")
        context_digests.add(context)
        expected = {role: report["roles"][role]["output_transcript_sha256"]
                    for role in _DIGEST_BY_ROLE}
        for item in cases:
            if item["asset"] != asset:
                continue
            for role, field in _DIGEST_BY_ROLE.items():
                if item[field] != expected[role]:
                    raise PilotBlocked(
                        "case transcript digest differs from verified asset/role batch")
        unique_models = report["reference_challenger_different_model_families"]
        all_r_x_family_independent &= unique_models
        output[asset] = {
            "source_context_sha256": context,
            "case_count": counts[asset],
            "role_output_sha256": expected,
            "reference_challenger_different_model_families": unique_models,
        }
    return {
        "schema_version": "v04-mla-role-cohort-structural-binding-v1",
        "study_id": "V04-MLA-1",
        "status": ("STRUCTURAL_BOUND_NOT_EXECUTION_PROOF" if all_r_x_family_independent
                   else "PROVISIONAL_CORRELATED_MODEL_FAMILY"),
        "case_denominator": len(cases),
        "assets": output,
        "trusted_provider_invocation_proven": False,
        "temporal_precommitment_proven": False,
        "provider_side_oracle_isolation_proven": False,
        "real_software_oracle_verified": False,
        "human_review_completed": False,
        "empirical_qualification_pass": False,
        "formal_product_release_qualified": False,
    }
