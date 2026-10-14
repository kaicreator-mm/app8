"""Provider-neutral blind P/R/X transcript boundary; no provider calls or truth.

Caller MUST supply a trusted, pre-execution frozen configuration and the
exact prompt envelopes actually submitted by its privileged orchestration.
A self-reported hash/role cannot prove provider-side isolation.
"""
from __future__ import annotations

import hashlib
import json
import re

from scripts.v04_mla_pilot_reducer import SOURCE_BLOB

ROLES = ("P", "R", "X")
CONFIG_FIELDS = {"model_family", "provider", "model_version",
                 "prompt_sha256", "sampling_sha256", "input_sha256"}
ROOT_FIELDS = {"schema_version", "study_id", "source_pack_git_blob",
               "frozen_before_first_response", "source_context_sha256", "roles"}
INPUT_FIELDS = {"source_pack_git_blob", "source_context_sha256",
                "task_instruction_sha256", "visibility_scope"}
VIS = {"P": "P_SOURCE_ONLY", "R": "R_REFERENCE_SOURCE_ONLY",
       "X": "X_CHALLENGER_SOURCE_ONLY"}
SHA = re.compile(r"[0-9a-f]{64}\Z")


class BlindCaptureBlocked(ValueError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(raw: bytes):
    def nodup(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise BlindCaptureBlocked("duplicate context key")
            result[k] = v
        return result
    try:
        return json.loads(raw, object_pairs_hook=nodup,
                          parse_constant=lambda _: (_ for _ in ()).throw(BlindCaptureBlocked("nonfinite")))
    except (ValueError, UnicodeDecodeError) as exc:
        raise BlindCaptureBlocked("invalid prompt metadata envelope") from exc


def _valid_sha(value):
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def verify_blind_capture(freeze: dict, inputs: dict[str, bytes],
                         outputs: dict[str, bytes]) -> dict:
    """Check precommitted exact byte inputs and return safe transcript digests.

    A result is only a STRUCTURAL_CAPTURE, not independent model invocation,
    model-produced human Gold, trustworthy oracle, or study PASS.
    """
    if not isinstance(freeze, dict) or set(freeze) != ROOT_FIELDS:
        raise BlindCaptureBlocked("exact immutable freeze fields required")
    if (freeze["schema_version"] != "v04-mla-blind-freeze-v1"
            or freeze["study_id"] != "V04-MLA-1"
            or freeze["source_pack_git_blob"] != SOURCE_BLOB
            or freeze["frozen_before_first_response"] is not True
            or not _valid_sha(freeze["source_context_sha256"])
            or not isinstance(freeze["roles"], dict)
            or set(freeze["roles"]) != set(ROLES)):
        raise BlindCaptureBlocked("invalid frozen P/R/X study identity")
    if (not isinstance(inputs, dict) or set(inputs) != set(ROLES)
            or not isinstance(outputs, dict) or set(outputs) != set(ROLES)):
        raise BlindCaptureBlocked("all P/R/X inputs and captured outputs required")
    families = {}
    report = {}
    for role in ROLES:
        config = freeze["roles"][role]
        if not isinstance(config, dict) or set(config) != CONFIG_FIELDS:
            raise BlindCaptureBlocked("exact role configuration required")
        if any(not isinstance(config[k], str) or not config[k].strip()
               for k in ("model_family", "provider", "model_version")):
            raise BlindCaptureBlocked("model identity missing")
        if any(not _valid_sha(config[k])
               for k in ("prompt_sha256", "sampling_sha256", "input_sha256")):
            raise BlindCaptureBlocked("model prompt/sampling/input must be SHA-bound")
        families[role] = config["model_family"].strip().casefold()
        pin, output = inputs[role], outputs[role]
        if (not isinstance(pin, bytes) or not isinstance(output, bytes)
                or not (0 < len(pin) <= 500_000)
                or not (0 < len(output) <= 2_000_000)):
            raise BlindCaptureBlocked("missing/oversized actual input or output transcript")
        if _sha(pin) != config["input_sha256"]:
            raise BlindCaptureBlocked("captured role input differs from frozen bytes")
        ctx = _read_json(pin)
        if (not isinstance(ctx, dict) or set(ctx) != INPUT_FIELDS
                or ctx["source_pack_git_blob"] != SOURCE_BLOB
                or ctx["source_context_sha256"] != freeze["source_context_sha256"]
                or not _valid_sha(ctx["task_instruction_sha256"])
                or ctx["visibility_scope"] != VIS[role]):
            raise BlindCaptureBlocked("non-allowlisted role input or oracle exposure")
        report[role] = {
            "model_family": config["model_family"],
            "provider": config["provider"],
            "model_version": config["model_version"],
            "input_sha256": config["input_sha256"],
            "output_transcript_sha256": _sha(output),
        }
    independent_reference_and_challenge = families["R"] != families["X"]
    return {
        "schema_version": "v04-mla-blind-capture-structural-v1",
        "study_id": "V04-MLA-1",
        "roles": report,
        "reference_challenger_different_model_families":
            independent_reference_and_challenge,
        "status": "STRUCTURAL_CAPTURE_ONLY" if independent_reference_and_challenge
                  else "PROVISIONAL_CORRELATED_MODEL_FAMILY",
        "trusted_provider_invocation_proven": False,
        "provider_side_oracle_isolation_proven": False,
        "real_software_oracle_verified": False,
        "human_review_completed": False,
        "empirical_qualification_pass": False,
        "formal_product_release_qualified": False,
    }
