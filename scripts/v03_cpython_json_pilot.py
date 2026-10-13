"""Single, operator-authorized, real CPython JSON Capability pilot.

NEVER import this module as a model-callable tool. A trusted Build Host operator
must freeze Docker client/image/config, review CPython license, provision a private
key and supply a separate private ledger location. No results are pre-asserted.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import secrets
import sys

from app8.evidence.attestation import AttestationGate
from app8.evidence.ingress import import_signed_observation
from app8.execution.docker_policy import ContainerRequest
from app8.execution.docker_runner import (
    RealDockerRunner, RunnerBlocked, RunnerConfig, freeze_execution_plan,
    load_signing_key, policy_source_sha256,
)
from app8.qualification import qualify_stored_capability
from app8.storage import EvidenceStore

IMAGE = ("library/python@sha256:"
         "5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b")
COMMAND = "/usr/local/bin/python"
BINDING = "binding:cpython-json-normalize"
GOOD_SCRIPT = (
    "import json;print(json.dumps(json.loads('{\"b\":2,\"a\":1}'),"
    "sort_keys=True,separators=(',',':')))"
)
BAD_SCRIPT = "import json;json.loads('{invalid')"
MEASURE_SCRIPT = (
    "import hashlib,json,pathlib,sys;"
    "p=pathlib.Path(json.__file__);"
    "print(json.dumps({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),"
    "'version':sys.version.split()[0]},sort_keys=True,separators=(',',':')))"
)
_CASES = {
    "P01": (GOOD_SCRIPT, ("exit_code==0", 'stdout_contains:{"a":1,"b":2}'),
            "cap:cpython-json-normalize"),
    "N01": (BAD_SCRIPT, ("exit_code==1", "stderr_contains:JSONDecodeError"),
            "cap:cpython-json-malformed-boundary"),
    "F01": (GOOD_SCRIPT, ("exit_code==0", "stdout_contains:never-produced-sentinel-9fa4"),
            "cap:cpython-json-false-assertion"),
}
_SHA = frozenset("0123456789abcdef")


class PilotBlocked(ValueError):
    """A real-host pilot gate has not been met."""


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _strict_sha(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= _SHA


@dataclass(frozen=True)
class PilotSettings:
    docker_client: str
    docker_client_sha256: str
    environment_id: str
    expected_server_version: str
    ledger_root: Path
    key_file: Path | None = None
    approved_source_sha256: str | None = None
    license_review_reference: str | None = None

    def validate(self, *, execute: bool) -> None:
        if not Path(self.docker_client).is_absolute() or not _strict_sha(self.docker_client_sha256):
            raise PilotBlocked("PINNED_DOCKER_CLIENT_REQUIRED")
        if not self.environment_id or not self.expected_server_version:
            raise PilotBlocked("FROZEN_ENVIRONMENT_AND_SERVER_VERSION_REQUIRED")
        if execute:
            if not _strict_sha(self.approved_source_sha256):
                raise PilotBlocked("OPERATOR_APPROVED_SOURCE_SHA256_REQUIRED")
            if (not isinstance(self.license_review_reference, str) or
                    len(self.license_review_reference.strip()) < 8):
                raise PilotBlocked("REVIEWED_CPYTHON_LICENSE_PROVENANCE_REQUIRED")
            if self.key_file is None:
                raise PilotBlocked("PRIVATE_HMAC_KEY_FILE_REQUIRED")


def source_probe_request(settings: PilotSettings) -> ContainerRequest:
    return ContainerRequest(
        IMAGE, COMMAND, ("-I", "-c", MEASURE_SCRIPT),
        settings.docker_client_sha256, wall_seconds=15,
        max_output_bytes=4096,
    )


def case_request(settings: PilotSettings, case: str) -> ContainerRequest:
    if case not in _CASES:
        raise PilotBlocked("UNKNOWN_FROZEN_CASE")
    script, _, _ = _CASES[case]
    return ContainerRequest(
        IMAGE, COMMAND, ("-I", "-c", script),
        settings.docker_client_sha256, wall_seconds=15,
        max_output_bytes=8192,
    )


def make_runner(settings: PilotSettings, *, inspect_only: bool) -> RealDockerRunner:
    key = secrets.token_bytes(32) if inspect_only else load_signing_key(settings.key_file)
    config = RunnerConfig(
        runner_id="app8-v03-cpython-json-pilot",
        policy_sha256=policy_source_sha256(),
        client_argv_head=(settings.docker_client,),
        environment_id=settings.environment_id,
        expected_server_version=settings.expected_server_version,
        allowlist=frozenset({(IMAGE, COMMAND)}),
    )
    return RealDockerRunner(config, signing_key=key)


def inspect_source(runner: RealDockerRunner, settings: PilotSettings) -> dict:
    observation = runner.execute(source_probe_request(settings))
    if (observation.status != "EXECUTED" or observation.exit_code != 0 or
            observation.stdout_truncated or observation.stderr_truncated):
        raise PilotBlocked("REAL_SOURCE_PROBE_NOT_COMPLETE")
    try:
        measure = json.loads(observation.stdout.decode("utf-8", "strict"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise PilotBlocked("REAL_SOURCE_PROBE_NOT_JSON") from exc
    if (not isinstance(measure, dict) or set(measure) != {"path", "sha256", "version"}
            or not _strict_sha(measure["sha256"])
            or not isinstance(measure["path"], str)
            or not measure["path"].startswith("/")
            or not isinstance(measure["version"], str) or not measure["version"]):
        raise PilotBlocked("REAL_SOURCE_PROBE_IDENTITY_INVALID")
    return measure


def make_capability(source: dict, target: dict, case: str,
                    evidence_ids: list[str]) -> dict:
    """Pure frozen semantic projection from an operator-reviewed observed claim."""
    if case not in _CASES:
        raise PilotBlocked("UNKNOWN_FROZEN_CASE")
    _, _, cid = _CASES[case]
    sem_name = {
        "P01": "Parse and sort valid JSON object",
        "N01": "Report malformed JSON parse error",
        "F01": "Adversarial false positive assertion control",
    }[case]
    return {
        "schema_version": "app8-capability-v1",
        "capability_id": cid, "revision": 1,
        "semantic": {
            "name": sem_name, "purpose": sem_name, "user_job": sem_name,
            "inputs": ["operator-frozen JSON fixture"], "outputs": ["stdout or stderr"],
            "variants": [], "constraints": ["exact image digest", "no network"],
            "negative_boundaries": ["unreviewed source", "mismatched target"],
            "failure_modes": ["malformed JSON", "failed assertion"],
            "side_effects": [],
        },
        "source": dict(source, license_disposition="REVIEWED_COMPATIBLE"),
        "target": dict(target),
        "bindings": [{
            "binding_id": BINDING, "kind": "CLI", "address": COMMAND,
            "preconditions": ["operator-approved request", "frozen image digest"],
            "side_effects": [],
        }],
        "evidence_refs": list(evidence_ids),
        "readiness": {
            "lifecycle_state": "HYPOTHESIZED", "export_ready": False,
            "derived_by_policy": True, "policy_revision": "v03-scoped-pilot",
            "reason_codes": ["RECOMPUTE_FROM_STORED_ATTESTED_EVIDENCE"],
        },
        "projection_refs": [],
    }


def execute_pilot(runner: RealDockerRunner, settings: PilotSettings, measurement: dict) -> dict:
    """Execute three disjoint claims; never hide a signed negative result."""
    if measurement["sha256"] != settings.approved_source_sha256:
        raise PilotBlocked("MEASURED_SOURCE_SHA256_NOT_OPERATOR_APPROVED")
    source = {
        "repository": "python/cpython",
        "revision": f"python-{measurement['version']}@{IMAGE.rsplit(':', 1)[-1]}:{measurement['path']}",
        "content_sha256": measurement["sha256"],
    }
    target = {
        "identity": IMAGE, "package_sha256": IMAGE.rsplit(":", 1)[-1],
        "environment_id": settings.environment_id, "mapping_relation": "SAME",
    }
    fixture = {
        "content_sha256": _digest(json.dumps(
            {"design": "v03-cpython-json-pilot", "image": IMAGE},
            sort_keys=True, separators=(",", ":")).encode()),
        "input_description": "operator-reviewed fixed JSON code arguments",
        "reset_procedure": "ephemeral Docker --rm read-only and tmpfs",
    }

    # No Evidence is marked trusted until the real runner signs it and a
    # service-owned durable nonce ledger + EvidenceStore accept it.
    root = settings.ledger_root.resolve()
    if root.is_relative_to(Path.cwd().resolve()):
        raise PilotBlocked("PRIVATE_LEDGER_MUST_BE_OUTSIDE_WORKTREE")
    # Do not reuse an older signed ledger: the v0.3 qualification service
    # correctly requires *all* Evidence refs, including earlier refutations.
    # Each replay/host run needs an isolated private store and nonce ledger.
    if ((root / "evidence" / "evidence.sqlite3").exists() or
            (root / "nonces.sqlite3").exists()):
        raise PilotBlocked("FRESH_PRIVATE_LEDGER_REQUIRED")
    root.mkdir(parents=True, exist_ok=True)
    key = load_signing_key(settings.key_file)
    sidecars = {}
    outcomes = {}
    with EvidenceStore(root / "evidence") as store, AttestationGate(
        verification_key=key,
        runner_id="app8-v03-cpython-json-pilot",
        policy_sha256=policy_source_sha256(),
        image_sha256=target["package_sha256"],
        nonce_db=root / "nonces.sqlite3",
    ) as gate:
        receipts = {}
        for case in ("P01", "N01", "F01"):
            request = case_request(settings, case)
            assertions = list(_CASES[case][1])
            plan = freeze_execution_plan(BINDING, assertions, request)
            receipt = runner.execute_attest(
                request, claim_id=f"claim:v03-{case.lower()}",
                capability_id=_CASES[case][2], source=source, target=target,
                fixture=fixture, plan=plan,
            )
            ev = receipt.evidence
            if ev["observation"]["execution_status"] != "EXECUTED":
                raise PilotBlocked(f"{case}:EXECUTION_NOT_COMPLETE")
            for stream, digest in ((receipt.stdout, ev["observation"]["stdout_sha256"]),
                                   (receipt.stderr, ev["observation"]["stderr_sha256"])):
                if store.put_artifact(stream) != digest:
                    raise PilotBlocked(f"{case}:STREAM_ARTIFACT_DIGEST_MISMATCH")
            import_signed_observation(store, gate, ev, receipt.attestation)
            sidecars[ev["evidence_id"]] = receipt.attestation
            receipts[case] = ev
            outcomes[case] = {
                "verdict": ev["assessment"]["verdict"],
                "reason_codes": ev["assessment"]["reason_codes"],
                "evidence_sha256": _digest((json.dumps(ev, sort_keys=True,
                                  separators=(",", ":"), ensure_ascii=False) + "\n").encode()),
                "evidence_id": ev["evidence_id"],
                "nonce": receipt.attestation["nonce"],
            }

        # Drift test may not launch a container; an attempted wrong target must
        # fail before calling execute().
        req = case_request(settings, "P01")
        frozen = freeze_execution_plan(BINDING, list(_CASES["P01"][1]), req)
        wrong_target = dict(target, package_sha256="f" * 64)
        try:
            runner.execute_attest(
                req, claim_id="claim:v03-b01",
                capability_id=_CASES["P01"][2], source=source,
                target=wrong_target, fixture=fixture, plan=frozen,
            )
        except RunnerBlocked:
            outcomes["B01"] = {"verdict": "BLOCKED_PRE_SPAWN"}
        else:
            raise PilotBlocked("B01_TARGET_DRIFT_NOT_BLOCKED")

        if outcomes["P01"]["verdict"] != "SUPPORTED":
            raise PilotBlocked("P01_NOT_SUPPORTED")
        if outcomes["N01"]["verdict"] != "SUPPORTED":
            raise PilotBlocked("N01_ERROR_BEHAVIOR_NOT_OBSERVED")
        if outcomes["F01"]["verdict"] != "REFUTED":
            raise PilotBlocked("F01_FALSE_ASSERTION_NOT_REFUTED")

        qualifications = {}
        for case in ("P01", "N01", "F01"):
            ev = receipts[case]
            cap = make_capability(source, target, case, [ev["evidence_id"]])
            q = qualify_stored_capability(
                cap, store=store, attestation_gate=gate,
                signed_attestations=sidecars,
            )
            qualifications[case] = {
                "status": q.status, "export_ready": q.readiness.export_ready,
                "evidence_count": q.evidence_count,
                "evidence_snapshot_sha256": q.evidence_snapshot_sha256,
                "projection_sha256": {
                    name: projection["projection_sha256"]
                    for name, projection in q.projections.items()
                },
            }
        if (qualifications["P01"]["status"] != "SCOPED_EXPORT_READY" or
                qualifications["N01"]["status"] != "SCOPED_EXPORT_READY" or
                qualifications["F01"]["export_ready"]):
            raise PilotBlocked("SCOPED_QUALIFICATION_GATE_FAILED")

    return {
        "status": "SCOPED_CPYTHON_JSON_PILOT_PASS",
        "source": source, "target": target,
        "license_review_reference": settings.license_review_reference,
        "cases": outcomes, "qualifications": qualifications,
        "real_host_result": True, "se10_se11_general_effectiveness": "UNPROVEN",
        "formal_release_qualified": False,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Privileged CPython JSON real-host pilot, not a product release")
    p.add_argument("action", choices=("inspect", "execute"))
    p.add_argument("--docker-client", required=True)
    p.add_argument("--docker-client-sha256", required=True)
    p.add_argument("--environment-id", required=True)
    p.add_argument("--server-version", required=True)
    p.add_argument("--ledger-root", required=True)
    p.add_argument("--key-file")
    p.add_argument("--source-sha256")
    p.add_argument("--license-review-reference")
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    settings = PilotSettings(
        docker_client=args.docker_client,
        docker_client_sha256=args.docker_client_sha256,
        environment_id=args.environment_id,
        expected_server_version=args.server_version,
        ledger_root=Path(args.ledger_root),
        key_file=Path(args.key_file) if args.key_file else None,
        approved_source_sha256=args.source_sha256,
        license_review_reference=args.license_review_reference,
    )
    try:
        settings.validate(execute=args.action == "execute")
        runner = make_runner(settings, inspect_only=args.action == "inspect")
        measure = inspect_source(runner, settings)
        if args.action == "inspect":
            report = {"status": "SOURCE_INSPECTED_NOT_EVIDENCE",
                      "image": IMAGE, "source": measure, "release_qualified": False}
        else:
            report = execute_pilot(runner, settings, measure)
        Path(args.out).write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return 0
    except (PilotBlocked, RunnerBlocked, ValueError, OSError) as exc:
        Path(args.out).write_text(json.dumps({"status": "BLOCKED", "reason": str(exc),
                                              "release_qualified": False}) + "\n", encoding="utf-8")
        return 2


if __name__ == "__main__":
    sys.exit(main())
