#!/usr/bin/env python3
"""Real-host qualification for the privileged Docker runner (issue #133).

Runs the runner against a REAL Docker Linux daemon on the pinned image, signs
Evidence v2 with an operator-provisioned key, ingests through the trusted
attestation gate into a real append-only EvidenceStore, and exercises the
negative matrix (allowlist/policy/CLI-pin blocks, tamper, replay, forgery,
wrong key, unauthorized EXPORT_READY, model self-certification).

NEVER auto-run in CI. Requires:
  - APP8_RUNNER_HMAC_KEY_FILE: private key file OUTSIDE the repo (>=32 bytes)
  - a real Docker daemon in Linux-container mode with the pinned image present
    (the runner never pulls: --pull=never is policy)
  - --evidence-dir outside the repository (raw bounded logs stay private)

Exit 0 only if every positive AND negative check passed on this host.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app8.contracts import ContractError, validate_contract
from app8.evidence.attestation import AttestationError, AttestationGate
from app8.evidence.ingress import import_signed_observation
from app8.execution.docker_policy import ContainerRequest
from app8.execution.docker_runner import (RealDockerRunner, RunnerBlocked, RunnerConfig,
                                          freeze_execution_plan, load_signing_key,
                                          policy_source_sha256)
from app8.readiness import evaluate_readiness
from app8.storage import EvidenceStore

IMAGE = "library/python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b"
IMAGE_DIGEST = IMAGE.rsplit(":", 1)[1]
PYTHON = "/usr/local/bin/python"
BINDING = "binding:real-runner-qualification"
CAPABILITY_ID = "cap:real-runner-python-smoke"

PROFILES = {
    "desktop": {"client": "C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe",
                "runner_id": "app8-real-runner-desktop",
                "environment_id": "docker-desktop-linux-x86_64"},
    "wsl": {"client": "/usr/bin/docker",
            "runner_id": "app8-real-runner-wsl",
            "environment_id": "docker-wsl2-ubuntu-linux-x86_64"},
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(doc) -> bytes:
    return (json.dumps(doc, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


class Harness:
    def __init__(self, profile: str, evidence_dir: Path):
        self.profile = profile
        self.cfg = PROFILES[profile]
        self.dir = evidence_dir
        self.dir.mkdir(parents=True, exist_ok=True)
        self.events = self.dir / f"events-{profile}.ndjson"
        self.results: list[dict] = []
        self.started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def log(self, step: str, status: str, **detail) -> None:
        row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "profile": self.profile, "step": step, "status": status, **detail}
        with open(self.events, "a", encoding="utf-8", newline="\n") as out:
            out.write(json.dumps(row, sort_keys=True) + "\n")
        self.results.append(row)
        print(f"[{status}] {step}" + (f" — {detail['note']}" if "note" in detail else ""))

    def client_sha256(self) -> str:
        return _sha256(Path(self.cfg["client"]).read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, choices=sorted(PROFILES))
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--repo-sha", default="",
                        help="operator-pinned git SHA; required where worktree .git "
                             "uses foreign-OS paths (e.g. WSL reading a Windows worktree)")
    args = parser.parse_args()

    harness = Harness(args.profile, Path(args.evidence_dir))
    repo = Path(__file__).resolve().parents[1]
    if args.repo_sha:
        import re
        if not re.fullmatch(r"[0-9a-f]{40}", args.repo_sha):
            print("BLOCKED: --repo-sha must be a 40-hex git SHA", file=sys.stderr)
            return 3
        repo_sha = args.repo_sha
    else:
        repo_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                                  capture_output=True, text=True, check=True).stdout.strip()
    policy_sha = policy_source_sha256()
    key = load_signing_key()  # APP8_RUNNER_HMAC_KEY_FILE, outside repo, owner-only
    cli_sha = harness.client_sha256()

    harness.log("freeze", "INFO", repo_sha=repo_sha, policy_sha256=policy_sha,
                docker_cli_sha256=cli_sha, image=IMAGE)

    shared_before = subprocess.run(
        [harness.cfg["client"], "ps", "--format", "{{.Names}}"],
        capture_output=True, text=True, check=False).stdout.split()
    inspect = subprocess.run([harness.cfg["client"], "image", "inspect", IMAGE],
                             capture_output=True, check=False)
    if inspect.returncode != 0:
        harness.log("image_present", "BLOCKED", note="pinned image absent; operator pre-pulls")
        return 3
    harness.log("image_present", "PASS")

    config = RunnerConfig(runner_id=harness.cfg["runner_id"], policy_sha256=policy_sha,
                          client_argv_head=(harness.cfg["client"],),
                          environment_id=harness.cfg["environment_id"],
                          allowlist=frozenset({(IMAGE, PYTHON)}))
    runner = RealDockerRunner(config, signing_key=key)
    store = EvidenceStore(harness.dir / f"store-{args.profile}")
    gate = AttestationGate(verification_key=key, runner_id=config.runner_id,
                           policy_sha256=policy_sha, image_sha256=IMAGE_DIGEST,
                           nonce_db=harness.dir / f"nonces-{args.profile}.sqlite3")

    source = {"repository": "kaicreator-mm/app8", "revision": repo_sha,
              "content_sha256": policy_sha}
    target = {"identity": IMAGE, "package_sha256": IMAGE_DIGEST,
              "environment_id": harness.cfg["environment_id"], "mapping_relation": "SAME"}

    failures = 0

    def check(step: str, fn) -> object:
        nonlocal failures
        try:
            outcome = fn()
        except Exception as exc:  # noqa: BLE001 - harness records, never swallows
            harness.log(step, "FAIL", error=f"{type(exc).__name__}:{exc}"[:300])
            failures += 1
            return None
        return outcome

    def expect_blocked(step: str, fn) -> None:
        nonlocal failures
        try:
            fn()
        except (RunnerBlocked, AttestationError, ContractError) as exc:
            harness.log(step, "PASS", note=f"denied:{type(exc).__name__}")
            return
        except Exception as exc:  # noqa: BLE001
            harness.log(step, "FAIL", error=f"wrong-error:{type(exc).__name__}:{exc}"[:300])
            failures += 1
            return
        harness.log(step, "FAIL", note="action was NOT denied")
        failures += 1

    def run_case(name: str, program_args, assertions, wall=60, cap=65536):
        nonlocal failures
        program = " ".join(program_args)
        fixture = {"content_sha256": _sha256(program.encode()),
                   "input_description": f"python argv: {program[:120]}",
                   "reset_procedure": "--rm tmpfs-only ephemeral container; nothing persists"}
        request = ContainerRequest(IMAGE, PYTHON, tuple(program_args), cli_sha, wall, cap)
        plan = freeze_execution_plan(BINDING, assertions, request)
        receipt = check(f"run:{name}",
                        lambda: runner.execute_attest(request, claim_id=f"claim:{name}",
                                                      capability_id=CAPABILITY_ID,
                                                      source=source, target=target,
                                                      fixture=fixture, plan=plan))
        if receipt is None:
            return None
        ev = receipt.evidence
        obs = receipt.observation
        stored_ok = (store.put_artifact(receipt.stdout) == ev["observation"]["stdout_sha256"]
                     and store.put_artifact(receipt.stderr) == ev["observation"]["stderr_sha256"])
        import_signed_observation(store, gate, ev, receipt.attestation)
        harness.log(f"run:{name}", "PASS", verdict=ev["assessment"]["verdict"],
                    exit_code=obs.exit_code, runner_status=obs.status, wall_ms=obs.wall_ms,
                    evidence_id=ev["evidence_id"], artifacts_verified=stored_ok,
                    stdout_sha256=ev["observation"]["stdout_sha256"])
        if not stored_ok:
            harness.log(f"run:{name}:artifacts", "FAIL", note="artifact digest mismatch")
            failures += 1
        return receipt

    # ---- real executions ----
    smoke = run_case("smoke", ["--version"], ["exit_code==0", "stdout_contains:Python 3.12"])
    capable = run_case("capability", ["-c", "print('app8-cap-ok')"],
                       ["exit_code==0", "stdout_contains:app8-cap-ok"])
    refuted = run_case("error", ["-c", "import sys;sys.exit(3)"], ["exit_code==0"])
    if refuted is not None and refuted.evidence["assessment"]["verdict"] != "REFUTED":
        harness.log("error-refuted", "FAIL", note="expected REFUTED")
        failures += 1
    wall = run_case("wall-limit", ["-c", "import time;time.sleep(120)"], ["exit_code==0"], wall=10)
    if wall is not None:
        codes = wall.evidence["assessment"]["reason_codes"]
        if wall.observation.status != "WALL_LIMIT_ENFORCED" or "WALL_LIMIT_ENFORCED" not in codes:
            harness.log("wall-enforced", "FAIL", note="wall limit not enforced/recorded")
            failures += 1
        else:
            harness.log("wall-enforced", "PASS",
                        note=f"exit_code={wall.observation.exit_code} wall_ms={wall.observation.wall_ms}")
    flood = run_case("output-cap", ["-c", "import sys;sys.stdout.buffer.write(b'A'*1048576)"],
                     ["exit_code==0"], cap=65536)
    if flood is not None:
        if (flood.observation.status != "OUTPUT_LIMIT_ENFORCED"
                or len(flood.observation.stdout) != 65536):
            harness.log("output-cap-enforced", "FAIL",
                        note=f"len={len(flood.observation.stdout)}")
            failures += 1
        else:
            harness.log("output-cap-enforced", "PASS", note="truncated at exactly 65536 bytes")

    # ---- runner-side negative matrix (nothing may spawn) ----
    expect_blocked("deny:unallowlisted-command",
                   lambda: runner.execute(ContainerRequest(IMAGE, "/bin/ls", (), cli_sha, 10, 65536)))
    expect_blocked("deny:unpinned-image",
                   lambda: runner.execute(ContainerRequest(
                       "library/python@sha256:" + "0" * 64, PYTHON, (), cli_sha, 10, 65536)))
    expect_blocked("deny:cli-pin-mismatch",
                   lambda: runner.execute(ContainerRequest(IMAGE, PYTHON, (), "0" * 64, 10, 65536)))
    expect_blocked("deny:shell-command",
                   lambda: runner.execute(ContainerRequest(IMAGE, "/bin/sh", (), cli_sha, 10, 65536)))

    # ---- trust-chain negative matrix on the real store ----
    if capable is not None:
        ev, att = capable.evidence, capable.attestation
        tampered = json.loads(json.dumps(ev))
        tampered["observation"]["stdout_sha256"] = "1" * 64
        expect_blocked("deny:tampered-evidence",
                       lambda: import_signed_observation(store, gate, tampered, att))
        expect_blocked("deny:replay",
                       lambda: import_signed_observation(store, gate, ev, att))
        expect_blocked("deny:forged-mac",
                       lambda: import_signed_observation(
                           store, gate, ev, dict(att, mac_sha256="f" * 64)))
        evil = AttestationGate(verification_key=b"z" * 32, runner_id=config.runner_id,
                               policy_sha256=policy_sha, image_sha256=IMAGE_DIGEST,
                               nonce_db=harness.dir / f"evil-{args.profile}.sqlite3")
        expect_blocked("deny:wrong-key",
                       lambda: import_signed_observation(store, evil, ev, att))
        evil.close()

        model_ev = json.loads(json.dumps(ev))
        model_ev["assessment"]["assessor_kind"] = "MODEL_PROPOSAL_ONLY"
        import hmac as _hmac
        model_att = {"schema_version": "app8-attested-evidence-v2",
                     "evidence_sha256": _sha256(_canonical(model_ev)),
                     "runner_id": config.runner_id, "policy_sha256": policy_sha,
                     "image_sha256": IMAGE_DIGEST, "nonce": "1" * 32}
        model_att["mac_sha256"] = _hmac.new(key, _canonical(model_att),
                                            hashlib.sha256).hexdigest()
        expect_blocked("deny:model-self-certification",
                       lambda: import_signed_observation(store, gate, model_ev, model_att))

        capability = {
            "schema_version": "app8-capability-v1", "capability_id": CAPABILITY_ID, "revision": 1,
            "semantic": {"name": "sandboxed python smoke", "purpose": "real-runner qualification",
                         "user_job": "execute pinned python in sandbox and observe",
                         "inputs": [], "outputs": ["bounded stdout"], "variants": [],
                         "constraints": ["no network", "no host mounts", "read-only rootfs"],
                         "negative_boundaries": ["no product-effectiveness claim"],
                         "failure_modes": ["nonzero exit", "wall/output limit"],
                         "side_effects": []},
            "source": {**source, "license_disposition": "UNKNOWN"}, "target": target,
            "bindings": [{"binding_id": BINDING, "kind": "CLI",
                          "address": "docker run <pinned image>", "preconditions": [],
                          "side_effects": []}],
            "evidence_refs": [ev["evidence_id"]],
            "readiness": {"lifecycle_state": "HYPOTHESIZED", "export_ready": False,
                          "derived_by_policy": True, "policy_revision": "t03-v1",
                          "reason_codes": ["REAL_EXECUTION_NOT_RUN"]},
            "projection_refs": []}
        validate_contract("capability", capability)

        def projection_ok(cap) -> bool:
            validate_contract("capability", cap)
            return cap["target"] == ev["target"] and ev["evidence_id"] in cap["evidence_refs"]

        denied = evaluate_readiness(capability, [ev], projection_verifier=projection_ok)
        if denied.export_ready:
            harness.log("readiness:unauthenticated-denied", "FAIL", note="bare JSON exported")
            failures += 1
        else:
            harness.log("readiness:unauthenticated-denied", "PASS",
                        note=",".join(denied.reason_codes))
        ready = evaluate_readiness(capability, [ev], projection_verifier=projection_ok,
                                   attestation_gate=gate,
                                   signed_attestations={ev["evidence_id"]: att})
        if ready.export_ready and ready.lifecycle_state == "EXPORT_READY":
            harness.log("readiness:scoped-export-ready", "PASS",
                        note="scoped to synthetic smoke capability only; no product claim")
        else:
            harness.log("readiness:scoped-export-ready", "FAIL",
                        note=",".join(ready.reason_codes))
            failures += 1

    # ---- environment integrity: no leftover containers, shared services intact ----
    leftover = subprocess.run([harness.cfg["client"], "ps", "-aq", "--filter",
                               f"ancestor={IMAGE}"], capture_output=True, text=True,
                              check=False).stdout.split()
    shared_after = subprocess.run([harness.cfg["client"], "ps", "--format", "{{.Names}}"],
                                  capture_output=True, text=True, check=False).stdout.split()
    if leftover:
        harness.log("zero-leftover-containers", "FAIL", note=f"leftover:{leftover}")
        failures += 1
    else:
        harness.log("zero-leftover-containers", "PASS")
    missing = sorted(set(shared_before) - set(shared_after))
    if missing:
        harness.log("shared-services-intact", "FAIL", note=f"missing:{missing}")
        failures += 1
    else:
        harness.log("shared-services-intact", "PASS")

    summary = {"schema_version": "app8-real-runner-qualification-v1", "profile": args.profile,
               "started_utc": harness.started, "repo_sha": repo_sha,
               "policy_sha256": policy_sha, "docker_cli_sha256": cli_sha, "image": IMAGE,
               "checks": harness.results,
               "verdict": "PASS" if failures == 0 else "FAIL", "failures": failures}
    (harness.dir / f"summary-{args.profile}.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"VERDICT={summary['verdict']} profile={args.profile} failures={failures}")
    gate.close()
    store.close()
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
