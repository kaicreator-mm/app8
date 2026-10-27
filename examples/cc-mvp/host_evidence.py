#!/usr/bin/env python3
"""CC04 operator-only real evidence admission; NOT an Agent or release runner.

Reuse app8's verified Docker runner, signed Evidence ingress and complete-ledger
qualifier. No LLM calls, no fake receipts, no docker policy edits, no arbitrary
host subprocess. Final Agent caller authenticity and second-session reuse are
separately tested by a real Agent outside this script.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app8.contracts import parse_json, validate_contract
from app8.evidence.attestation import AttestationGate
from app8.evidence.ingress import import_signed_observation
from app8.execution.docker_policy import ContainerRequest
from app8.execution.docker_runner import (
    RealDockerRunner, RunnerConfig, freeze_execution_plan,
    load_signing_key, policy_source_sha256,
)
from app8.qualification import qualify_stored_capability
from app8.projections.render import digest
from app8.storage import EvidenceStore


class CC04Blocked(ValueError):
    """An operator admission prerequisite or live proof is missing."""


def validate_job(spec: dict) -> tuple[dict, list[dict]]:
    """Pure preflight; an operator's assertions never establish source authority."""
    if not isinstance(spec, dict) or set(spec) != {"capability", "docker", "cases"}:
        raise CC04Blocked("expected capability, docker and cases")
    cap = validate_contract("capability", spec["capability"])
    if cap["source"]["license_disposition"] != "REVIEWED_COMPATIBLE":
        raise CC04Blocked("independently reviewed license disposition required")
    if cap["target"]["mapping_relation"] != "SAME":
        raise CC04Blocked("independently verified source/target SAME required")
    if cap["evidence_refs"]:
        raise CC04Blocked("new run requires a candidate without evidence refs")
    bindings = cap["bindings"]
    if (len(bindings) != 1 or bindings[0]["kind"] != "CLI"
            or bindings[0]["side_effects"]):
        raise CC04Blocked("one scoped non-mutating CLI binding required")
    d = spec["docker"]
    if not isinstance(d, dict) or set(d) != {
        "client_path", "client_sha256", "runner_id", "environment_id"
    }:
        raise CC04Blocked("exact Docker client and runner identity required")
    if (not isinstance(d["client_path"], str) or
            not Path(d["client_path"]).is_absolute() or
            not isinstance(d["client_sha256"], str) or len(d["client_sha256"]) != 64 or
            any(c not in "0123456789abcdef" for c in d["client_sha256"]) or
            d["environment_id"] != cap["target"]["environment_id"]):
        raise CC04Blocked("Docker client pin or environment mismatch")
    cases = spec["cases"]
    if not isinstance(cases, list) or not 1 <= len(cases) <= 4:
        raise CC04Blocked("one to four bounded behavior cases required")
    for case in cases:
        if (not isinstance(case, dict) or
                set(case) != {"claim_id", "args", "assertions", "fixture"} or
                not isinstance(case["claim_id"], str) or
                not case["claim_id"].startswith("claim:") or
                not isinstance(case["args"], list) or
                any(not isinstance(x, str) for x in case["args"]) or
                not isinstance(case["assertions"], list) or
                not case["assertions"] or
                any(not isinstance(x, str) for x in case["assertions"]) or
                not isinstance(case["fixture"], dict) or
                set(case["fixture"]) != {
                    "content_sha256", "input_description", "reset_procedure"
                }):
            raise CC04Blocked("invalid frozen case envelope")
    return cap, cases


def freeze_cases(cap: dict, docker: dict, cases: list[dict]) -> list[tuple[ContainerRequest, dict]]:
    """Validate ALL frozen requests before the first Docker invocation.

    A malformed later case must not leave a partially executed private ledger.
    This reuses the runner's existing assertion parser and request policy.
    """
    binding = cap["bindings"][0]
    prepared = []
    for case in cases:
        req = ContainerRequest(
            image_ref=cap["target"]["identity"], command=binding["address"],
            args=tuple(case["args"]), docker_cli_sha256=docker["client_sha256"],
        )
        frozen = freeze_execution_plan(binding["binding_id"], case["assertions"], req)
        prepared.append((req, frozen))
    return prepared


def _write_private(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def run(spec: dict, private_dir: Path) -> dict:
    cap, cases = validate_job(spec)
    repo = Path(__file__).resolve().parents[2]
    root = private_dir.resolve()
    if root == repo or root.is_relative_to(repo):
        raise CC04Blocked("private Evidence must be outside repository")
    if root.exists() and any(root.iterdir()):
        raise CC04Blocked("use an empty private directory per evidence admission")
    d = spec["docker"]
    prepared_cases = freeze_cases(cap, d, cases)  # no Host action before all cases pass
    cli = Path(d["client_path"])
    if not cli.is_file() or cli.is_symlink():
        raise CC04Blocked("approved Docker client binary missing or symlinked")
    if sha256(cli.read_bytes()).hexdigest() != d["client_sha256"]:
        raise CC04Blocked("Docker client SHA256 mismatch")
    key = load_signing_key()  # existing external APP8_RUNNER_HMAC_KEY_FILE
    root.mkdir(parents=True, exist_ok=True)
    image = cap["target"]["identity"]
    image_sha = cap["target"]["package_sha256"]
    binding = cap["bindings"][0]
    runner_cfg = RunnerConfig(
        runner_id=d["runner_id"],
        policy_sha256=policy_source_sha256(),
        client_argv_head=(d["client_path"],),
        environment_id=d["environment_id"],
        allowlist=frozenset({(image, binding["address"])}),
    )
    runner = RealDockerRunner(runner_cfg, signing_key=key)
    source = {k: cap["source"][k] for k in ("repository", "revision", "content_sha256")}
    signed = {}
    evidence_ids = []
    records = []
    with EvidenceStore(root / "store") as store, AttestationGate(
        verification_key=key, runner_id=runner_cfg.runner_id,
        policy_sha256=runner_cfg.policy_sha256, image_sha256=image_sha,
        nonce_db=root / "accepted-nonces.sqlite3",
    ) as gate:
        for index, (case, prepared) in enumerate(zip(cases, prepared_cases), 1):
            req, frozen = prepared
            receipt = runner.execute_attest(
                req, claim_id=case["claim_id"],
                capability_id=cap["capability_id"], source=source,
                target=cap["target"], fixture=case["fixture"], plan=frozen,
            )
            # A refutation must be retained, never silently discarded.
            store.put_artifact(receipt.stdout)
            store.put_artifact(receipt.stderr)
            imported = import_signed_observation(
                store, gate, receipt.evidence, receipt.attestation)
            eid = receipt.evidence["evidence_id"]
            evidence_ids.append(eid)
            signed[eid] = receipt.attestation
            records.append({
                "case": index, "evidence_id": eid,
                "evidence_sha256": imported.evidence_sha256,
                "plan_sha256": frozen["plan_sha256"],
                "verdict": receipt.evidence["assessment"]["verdict"],
                "runner_status": receipt.observation.status,
                "exit_code": receipt.observation.exit_code,
                "stdout_sha256": receipt.evidence["observation"]["stdout_sha256"],
                "stderr_sha256": receipt.evidence["observation"]["stderr_sha256"],
            })
        cap["evidence_refs"] = evidence_ids
        qualification = qualify_stored_capability(
            cap, store=store, attestation_gate=gate,
            signed_attestations=signed,
        )
        _write_private(root / "capability.json", cap)
        _write_private(root / "signed-attestations.json", signed)
        report = {
            "schema_version": "app8-cc04-host-receipt-v1",
            "capability_id": cap["capability_id"],
            "capability_revision": cap["revision"],
            "semantic_sha256": digest(cap["semantic"]),
            "source_sha256": cap["source"]["content_sha256"],
            "target_sha256": image_sha,
            "target_identity": image,
            "environment_id": runner_cfg.environment_id,
            "binding_id": binding["binding_id"],
            "qualification": qualification.status,
            "evidence_snapshot_sha256": qualification.evidence_snapshot_sha256,
            "evidence": records,
            "license_source_review": "OPERATOR_ASSERTED_REQUIRES_INDEPENDENT_CONFIRMATION",
            "source_target_review": "OPERATOR_ASSERTED_REQUIRES_INDEPENDENT_CONFIRMATION",
            "agent_first_use": "NOT_RUN",
            "agent_second_use": "NOT_RUN",
            "mvp_release": "NOT_QUALIFIED",
        }
        _write_private(root / "host-report.json", report)
        return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", type=Path, required=True)
    parser.add_argument("--private-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        spec = parse_json(args.job.read_bytes())
        result = run(spec, args.private_dir)
    except Exception as exc:
        print(f"CC04_BLOCKED:{type(exc).__name__}:{exc}", file=sys.stderr)
        return 3
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["qualification"] == "SCOPED_EXPORT_READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
