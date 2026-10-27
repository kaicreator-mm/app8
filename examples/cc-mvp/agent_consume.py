#!/usr/bin/env python3
"""Operator-hosted CC04 Agent CLI entrypoint over persisted *real* signed Evidence.

This invokes the EXISTING app8.cli.consumer.run_agent_cli; it neither signs a
new observation nor authenticates an Agent caller. Independent Host/Agent
session authentication is an external CC04 gate, never this script's claim.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app8.cli.consumer import AgentConsumerBlocked, run_agent_cli
from app8.contracts import parse_json, validate_contract
from app8.evidence.attestation import AttestationGate
from app8.execution.docker_runner import (
    RealDockerRunner, RunnerConfig, load_signing_key, policy_source_sha256,
)
from app8.storage import EvidenceStore


class UseBlocked(ValueError):
    """The selected real Host receipt or frozen job is not available."""


def checked_selection(job: dict, admitted: dict, case_index: int) -> tuple[dict, dict]:
    """Allow only an exact previously-frozen operator task and Capability."""
    validate_contract("capability", admitted)
    if not isinstance(job, dict) or set(job) != {"capability", "docker", "cases"}:
        raise UseBlocked("expected original reviewed operator job")
    candidate = dict(admitted)
    candidate["evidence_refs"] = []
    if job["capability"] != candidate:
        raise UseBlocked("reviewed job changed since the signed Capability admission")
    config = job["docker"]
    if not isinstance(config, dict) or set(config) != {
        "client_path", "client_sha256", "runner_id", "environment_id"
    }:
        raise UseBlocked("operator Docker identity is missing")
    if config["environment_id"] != admitted["target"]["environment_id"]:
        raise UseBlocked("target environment is different from admission")
    if not isinstance(job["cases"], list) or type(case_index) is not int or not (
            1 <= case_index <= len(job["cases"])):
        raise UseBlocked("selected case is not in the frozen reviewed job")
    case = job["cases"][case_index - 1]
    if not isinstance(case, dict) or not isinstance(case.get("args"), list):
        raise UseBlocked("reviewed case arguments unavailable")
    if len(admitted["bindings"]) != 1 or admitted["bindings"][0]["kind"] != "CLI":
        raise UseBlocked("exactly one pinned CLI binding is required")
    return config, case


def consume(*, job_file: Path, private_dir: Path, case_index: int, session_id: str) -> dict:
    root = private_dir.resolve(strict=True)
    if not root.is_dir():
        raise UseBlocked("private signed Evidence directory not available")
    repo = Path(__file__).resolve().parents[2]
    if root == repo or root.is_relative_to(repo):
        raise UseBlocked("private Evidence cannot be stored inside the repository")
    job = parse_json(job_file.read_bytes())
    admitted = parse_json((root / "capability.json").read_bytes())
    sidecars = parse_json((root / "signed-attestations.json").read_bytes())
    config, case = checked_selection(job, admitted, case_index)
    key = load_signing_key()  # operator-owned, same key used at real Host admission
    client = Path(config["client_path"])
    if (not client.is_absolute() or not client.is_file() or client.is_symlink()
            or sha256(client.read_bytes()).hexdigest() != config["client_sha256"]):
        raise UseBlocked("operator Docker client is not the pinned binary")
    target = admitted["target"]
    binding = admitted["bindings"][0]
    runner_config = RunnerConfig(
        runner_id=config["runner_id"], policy_sha256=policy_source_sha256(),
        client_argv_head=(str(client),), environment_id=config["environment_id"],
        allowlist=frozenset({(target["identity"], binding["address"])}),
    )
    runner = RealDockerRunner(runner_config, signing_key=key)
    with EvidenceStore(root / "store") as store, AttestationGate(
        verification_key=key, runner_id=runner_config.runner_id,
        policy_sha256=runner_config.policy_sha256,
        image_sha256=target["package_sha256"],
        nonce_db=root / "accepted-nonces.sqlite3",
    ) as gate:
        result = run_agent_cli(
            admitted, store=store, gate=gate,
            signed_attestations=sidecars, runner=runner,
            binding_id=binding["binding_id"], docker_cli_sha256=config["client_sha256"],
            args=tuple(case["args"]), session_id=session_id,
        )
    payload = asdict(result)
    payload.update({
        "schema_version": "app8-cc04-agent-use-v1",
        "operator_case_index": case_index,
        "session_authentication": "EXTERNALLY_REQUIRED_NOT_PROVEN_BY_THIS_CLI",
        "release_qualified": False,
    })
    return payload


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--job", type=Path, required=True,
                   help="original private CC04 reviewed operator job JSON")
    p.add_argument("--private-dir", type=Path, required=True,
                   help="existing host_evidence.py private signed-ledger directory")
    p.add_argument("--case-index", type=int, default=1,
                   help="1-based index into original frozen operator cases")
    p.add_argument("--session-id", required=True,
                   help="caller/session label; independent Host Agent authentication is external")
    args = p.parse_args()
    try:
        result = consume(job_file=args.job, private_dir=args.private_dir,
                         case_index=args.case_index, session_id=args.session_id)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": f"{type(exc).__name__}:{exc}"}),
              file=sys.stderr)
        return 3
    print(json.dumps(result, sort_keys=True))
    return 0 if result["execution_status"] == "EXECUTED" and result["exit_code"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
