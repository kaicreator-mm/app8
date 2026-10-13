"""Bounded proposal snapshots for LLM-A discovery and LLM-B test planning."""
from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any

from app8.contracts import parse_json
from app8.discovery import SourceDocument

HASH = re.compile(r"[0-9a-f]{64}\Z")
HIDDEN = frozenset({"truth_class", "decisive_fixture", "hidden_truth", "private_gold", "gold_label", "ground_truth"})


class PlanError(ValueError):
    """Model output is untrusted, malformed, leaky or unbounded."""


def _exact(obj: Any, names: set[str], where: str) -> None:
    if not isinstance(obj, dict) or set(obj) != names:
        raise PlanError(f"{where}: exact field set mismatch")


def _text(value: Any, where: str) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise PlanError(f"{where}: nonempty bounded string required")


def _json(data: str | bytes | dict) -> dict:
    obj = parse_json(data) if isinstance(data, (str, bytes)) else data
    if not isinstance(obj, dict):
        raise PlanError("JSON object expected")
    return obj


def _canonical(data: dict) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def _no_hidden(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in HIDDEN:
                raise PlanError("private truth may not enter planning context")
            _no_hidden(item)
    elif isinstance(value, list):
        for item in value:
            _no_hidden(item)


def freeze_hypotheses(model_output: dict | str | bytes, source: SourceDocument) -> dict:
    obj = _json(model_output)
    _no_hidden(obj)
    _exact(obj, {"schema_version", "source_sha256", "source_revision", "hypotheses"}, "hypotheses")
    if obj["schema_version"] != "app8-hypotheses-v1":
        raise PlanError("hypothesis schema version mismatch")
    if obj["source_sha256"] != source.content_sha256 or obj["source_revision"] != source.revision:
        raise PlanError("hypotheses not bound to exact source")
    cases = obj["hypotheses"]
    if not isinstance(cases, list) or not 1 <= len(cases) <= 100:
        raise PlanError("bounded nonempty hypothesis list required")
    ids = set()
    for i, item in enumerate(cases):
        _exact(item, {"id", "user_job", "surface", "constraints", "source_anchor"}, f"case {i}")
        for key in ("id", "user_job", "surface", "source_anchor"):
            _text(item[key], f"case {i}.{key}")
        if item["id"] in ids:
            raise PlanError("duplicate hypothesis id")
        ids.add(item["id"])
        if not isinstance(item["constraints"], list) or len(item["constraints"]) > 30:
            raise PlanError("hypothesis constraints unbounded")
        for x in item["constraints"]:
            _text(x, "constraint")
    return {"schema_version":"app8-hypothesis-freeze-v1", "origin":"MODEL_PROPOSAL_ONLY",
            "source_sha256":source.content_sha256, "proposal_sha256":sha256(_canonical(obj)).hexdigest(),
            "source_revision":source.revision, "hypotheses":cases, "evidence_claimed":False}


def freeze_falsification_plan(model_output: dict | str | bytes, hypothesis_freeze: dict,
                               target_package_sha256: str) -> dict:
    obj = _json(model_output)
    _no_hidden(obj)
    _exact(obj, {"schema_version", "hypothesis_sha256", "target_sha256", "probes"}, "plan")
    if obj["schema_version"] != "app8-plan-v1":
        raise PlanError("plan schema version mismatch")
    if obj["hypothesis_sha256"] != hypothesis_freeze["proposal_sha256"]:
        raise PlanError("plan not bound to immutable hypotheses")
    if not HASH.fullmatch(target_package_sha256) or obj["target_sha256"] != target_package_sha256:
        raise PlanError("plan target identity mismatch")
    probes = obj["probes"]
    expected_ids = {x["id"] for x in hypothesis_freeze["hypotheses"]}
    if not isinstance(probes, list) or len(probes) != len(expected_ids):
        raise PlanError("every frozen hypothesis needs a plan")
    seen = set()
    for p in probes:
        _exact(p, {"hypothesis_id", "positive", "falsifying", "timeout_seconds", "network_allowed", "mutation_allowed"}, "probe")
        hid = p["hypothesis_id"]
        if hid not in expected_ids or hid in seen:
            raise PlanError("duplicate/unknown hypothesis plan")
        seen.add(hid)
        if type(p["timeout_seconds"]) is not int or not 1 <= p["timeout_seconds"] <= 300:
            raise PlanError("invalid execution time budget")
        if type(p["network_allowed"]) is not bool or type(p["mutation_allowed"]) is not bool:
            raise PlanError("explicit network/mutation permissions required")
        for name in ("positive", "falsifying"):
            steps = p[name]
            if not isinstance(steps, list) or not 1 <= len(steps) <= 5:
                raise PlanError(f"bounded nonempty {name} probes required")
            for step in steps:
                _text(step, "probe step")
    return {"schema_version":"app8-plan-freeze-v1", "plan_sha256":sha256(_canonical(obj)).hexdigest(),
            "hypothesis_sha256":obj["hypothesis_sha256"], "target_sha256":target_package_sha256,
            "origin":"MODEL_PROPOSAL_ONLY", "real_execution_observed":False, "probes":probes}
