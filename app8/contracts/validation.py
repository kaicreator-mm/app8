"""Fail-closed parser and schema validator. It never manufactures behavioral evidence."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from jsonschema import Draft202012Validator, FormatChecker

Kind = Literal["capability", "evidence"]
_SCHEMA_NAMES = {
    "capability": "capability-v1.schema.json",
    "evidence": "evidence-v1.schema.json",
}


class ContractError(ValueError):
    """Untrusted document or local contract is invalid."""


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ContractError(f"Duplicate JSON field: {key}")
        out[key] = value
    return out


def _reject_constant(value: str) -> None:
    raise ContractError(f"Nonfinite JSON number: {value}")


def parse_json(raw: bytes | str) -> Any:
    """UTF-8 JSON, disallow duplicate fields, NaN, Infinity and non-objects."""
    try:
        obj = json.loads(raw, object_pairs_hook=_unique_keys,
                         parse_constant=_reject_constant)
    except (ValueError, UnicodeDecodeError, TypeError) as exc:
        raise ContractError(f"Invalid JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise ContractError("Document root must be a JSON object")
    return obj


@lru_cache(maxsize=2)
def _validator(kind: Kind) -> Draft202012Validator:
    if kind not in _SCHEMA_NAMES:
        raise ContractError(f"Unknown contract type: {kind}")
    # Installed or checked-out repo: no HTTP schema references or remote lookups.
    path = (Path(__file__).resolve().parents[2] / "docs" / "architecture" /
            "v0.1-successor" / "contracts" / _SCHEMA_NAMES[kind])
    try:
        schema = parse_json(path.read_bytes())
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        # A missing schema is an explicit BLOCKED, not a permissive fallback.
        raise ContractError(f"Frozen local {kind} schema unavailable/invalid: {exc}") from exc
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_contract(kind: Kind, document: dict[str, Any] | bytes | str) -> dict[str, Any]:
    """Validate document structure and guard evidence-origin trust boundary.

    This is a structural ingress check, not proof that an asserted observation
    actually happened. T03 policy will calculate export readiness from stored
    observations; any user-supplied `export_ready=True` is untrusted.
    """
    obj = parse_json(document) if isinstance(document, (bytes, str)) else document
    if not isinstance(obj, dict):
        raise ContractError("Document root must be an object")
    errors = list(_validator(kind).iter_errors(obj))
    if errors:
        first = sorted(errors, key=lambda e: str(e.json_path))[0]
        raise ContractError(f"{kind} contract {first.json_path}: {first.message}")
    if kind == "evidence":
        status = obj["observation"]["execution_status"]
        verdict = obj["assessment"]["verdict"]
        observer = obj["observation"]["observer"]
        assessor = obj["assessment"]["assessor_kind"]
        if verdict == "SUPPORTED" and (status != "EXECUTED" or assessor == "MODEL_PROPOSAL_ONLY"):
            raise ContractError("N01/N02: unobserved or model-asserted support is not evidence")
        if status == "EXECUTED" and observer not in ("DETERMINISTIC_EXECUTION_ADAPTER", "MANUAL_OPERATOR_ATTESTED"):
            raise ContractError("N02: model output cannot certify real observation")
    return obj
