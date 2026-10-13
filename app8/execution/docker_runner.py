"""Privileged real-host Docker runner: verified client, bounded execution, signed Evidence.

Trust boundary: this module is operator-provisioned trusted code. It is NOT
model-callable, accepts NO caller-supplied isolation booleans as authority, and
never marks anything EXPORT_READY. It only:

1. reuses docker_policy.prepare_docker_sandbox (#124) as the sole argv source;
2. verifies the exact Docker client artifact SHA256 and daemon OS mode before
   every single run (a pinned image digest is not a client identity);
3. executes at most one container at a time, streaming stdout/stderr with hard
   byte caps and an external wall watchdog, then reaps via ``docker rm -f`` and
   verifies zero leftover containers before any signing;
4. adjudicates frozen plan assertions deterministically (never an LLM);
5. signs the full canonical Evidence payload (attestation v2, #131) with an
   HMAC key provisioned from a private file OUTSIDE the repository.

A signature attests "this exact observation was produced by this runner on this
host", never "the product works". Raw logs and keys stay off-repo.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import threading
import time
from typing import Any

from app8.contracts import validate_contract
from app8.execution.docker_policy import (
    ContainerRequest,
    PreparedSandbox,
    SandboxPolicyError,
    prepare_docker_sandbox,
)

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_NONCE = re.compile(r"[0-9a-f]{32}\Z")
_EXIT_ASSERTION = re.compile(r"exit_code==(-?\d{1,9})\Z")
_HASH_ASSERTION = re.compile(r"(stdout_sha256|stderr_sha256)==([0-9a-f]{64})\Z")
_CONTAINS_ASSERTION = re.compile(r"(stdout_contains|stderr_contains):([^\x00]{1,512})\Z", re.DOTALL)

ATTESTATION_SCHEMA_VERSION = "app8-attested-evidence-v2"  # pinned to evidence.attestation
OBSERVER_KIND = "DETERMINISTIC_EXECUTION_ADAPTER"
ASSESSOR_KIND = "DETERMINISTIC_ASSERTION_ENGINE"
_REPO_ROOT = Path(__file__).resolve().parents[2]

_SIGNABLE_STATUSES = frozenset({"EXECUTED", "WALL_LIMIT_ENFORCED", "OUTPUT_LIMIT_ENFORCED"})


class RunnerBlocked(ValueError):
    """The privileged runner refused to execute or sign (fail closed)."""


class RunnerKeyError(ValueError):
    """Signing key missing, weak, world-readable or inside the repository."""


def _canonical(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def policy_source_sha256() -> str:
    """SHA256 of the exact sandbox policy module bytes this runner enforces."""
    return _sha256((Path(__file__).resolve().parent / "docker_policy.py").read_bytes())


def load_signing_key(path: str | os.PathLike[str] | None = None) -> bytes:
    """Load the runner HMAC key from a private file; NEVER from the repository.

    Path comes from the explicit argument or APP8_RUNNER_HMAC_KEY_FILE. Content
    is hex-decoded when it is one long hex line, otherwise used raw. The file
    must hold >=32 bytes, live outside the repo checkout, and be owner-only on
    POSIX hosts.
    """
    raw = str(path) if path is not None else os.environ.get("APP8_RUNNER_HMAC_KEY_FILE", "")
    if not raw.strip():
        raise RunnerKeyError("signing key file required (APP8_RUNNER_HMAC_KEY_FILE)")
    candidate = Path(raw).expanduser()
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise RunnerKeyError("signing key file unreadable") from exc
    if not resolved.is_file():
        raise RunnerKeyError("signing key path is not a file")
    try:
        if resolved.is_relative_to(_REPO_ROOT):
            raise RunnerKeyError("signing key must live outside the repository checkout")
    except ValueError as exc:  # different drives on Windows
        raise RunnerKeyError("signing key location cannot be verified") from exc
    if os.name == "posix" and stat.S_IMODE(resolved.stat().st_mode) & 0o077:
        raise RunnerKeyError("signing key file must be owner-only (chmod 600)")
    data = resolved.read_bytes().strip()
    if re.fullmatch(rb"[0-9a-fA-F]{64,}", data):
        data = bytes.fromhex(data.decode("ascii"))
    if len(data) < 32:
        raise RunnerKeyError("signing key must be at least 32 bytes")
    return data


@dataclass(frozen=True)
class RunnerConfig:
    """Operator-frozen runner identity and authority; no runtime user input.

    client_argv_head is the exact invocation head of the Docker client; its
    LAST element is the reviewed client artifact whose SHA256 is pinned in
    every ContainerRequest (e.g. ("/usr/bin/docker",)). Earlier elements, when
    present, are only the loader used by hermetic tests.
    allowlist holds the exact approved (image@sha256, absolute command) pairs.
    """

    runner_id: str
    policy_sha256: str
    client_argv_head: tuple[str, ...]
    environment_id: str
    allowlist: frozenset[tuple[str, str]]
    kill_grace_seconds: float = 5.0
    expected_server_version: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.runner_id, str) or not 1 <= len(self.runner_id) <= 128:
            raise RunnerBlocked("runner identity required")
        if not isinstance(self.policy_sha256, str) or not _SHA.fullmatch(self.policy_sha256):
            raise RunnerBlocked("sandbox policy SHA256 must be frozen")
        if (not isinstance(self.client_argv_head, tuple) or not self.client_argv_head or
                any(not isinstance(x, str) or not Path(x).is_absolute() for x in self.client_argv_head)):
            raise RunnerBlocked("Docker client argv head must be absolute paths")
        if not isinstance(self.environment_id, str) or not self.environment_id:
            raise RunnerBlocked("frozen environment identity required")
        if not isinstance(self.allowlist, frozenset):
            raise RunnerBlocked("allowlist must be a frozen set of (image, command)")
        for entry in self.allowlist:
            if (not isinstance(entry, tuple) or len(entry) != 2 or
                    not isinstance(entry[0], str) or not isinstance(entry[1], str) or
                    not entry[1].startswith("/")):
                raise RunnerBlocked("allowlist entries must be (image_ref, absolute command)")
        if (type(self.kill_grace_seconds) not in (int, float) or
                not 0.1 <= self.kill_grace_seconds <= 30):
            raise RunnerBlocked("kill grace must be within [0.1, 30] seconds")
        if self.expected_server_version is not None and not isinstance(self.expected_server_version, str):
            raise RunnerBlocked("server version pin must be text")


@dataclass(frozen=True)
class RunnerObservation:
    """What the runner actually saw; never what a caller hoped for."""

    status: str
    exit_code: int | None
    stdout: bytes
    stderr: bytes
    stdout_truncated: bool
    stderr_truncated: bool
    wall_ms: int
    request_sha256: str
    image_sha256: str
    invocation_sha256: str
    daemon_server_version: str
    containers_reaped_verified: bool


@dataclass(frozen=True)
class RunnerReceipt:
    """Signed result of one real execution plus the raw bounded streams."""

    evidence: dict[str, Any]
    attestation: dict[str, Any]
    observation: RunnerObservation
    stdout: bytes
    stderr: bytes


class RealDockerRunner:
    """Executes frozen sandbox plans on one real Docker Linux host and signs them."""

    def __init__(self, config: RunnerConfig, *, signing_key: bytes):
        if type(config) is not RunnerConfig:
            raise RunnerBlocked("typed RunnerConfig required")
        if not isinstance(signing_key, bytes) or len(signing_key) < 32:
            raise RunnerBlocked("runner signing key must be >=32 private bytes")
        self._config = config
        self._key = signing_key
        self._lock = threading.Lock()

    # ---- verified client / daemon identity, re-checked before every run ----

    def _client_command(self, *args: str) -> tuple[str, ...]:
        return (*self._config.client_argv_head, *args)

    def _verify_client_identity(self, expected_sha256: str) -> None:
        if not isinstance(expected_sha256, str) or not _SHA.fullmatch(expected_sha256):
            raise RunnerBlocked("exact Docker client SHA256 pin required")
        artifact = Path(self._config.client_argv_head[-1])
        try:
            if not artifact.is_file() or artifact.is_symlink():
                raise RunnerBlocked("Docker client artifact missing or a symlink")
            actual = _sha256(artifact.read_bytes())
        except OSError as exc:
            raise RunnerBlocked("Docker client artifact unreadable") from exc
        if actual != expected_sha256:
            raise RunnerBlocked("DOCKER_CLIENT_SHA256_MISMATCH")

    def _verify_daemon(self) -> str:
        try:
            probe = subprocess.run(
                self._client_command("info", "--format", "{{.OSType}}|{{.ServerVersion}}"),
                capture_output=True, timeout=30, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RunnerBlocked("Docker daemon probe failed") from exc
        if probe.returncode != 0:
            raise RunnerBlocked("Docker daemon unreachable")
        try:
            os_type, server = probe.stdout.decode("utf-8", "strict").strip().split("|", 1)
        except (ValueError, UnicodeDecodeError) as exc:
            raise RunnerBlocked("Docker daemon probe unparsable") from exc
        if os_type != "linux":
            raise RunnerBlocked("DAEMON_NOT_LINUX_CONTAINERS")
        if (self._config.expected_server_version is not None and
                server != self._config.expected_server_version):
            raise RunnerBlocked("DAEMON_VERSION_MISMATCH")
        return server

    # ---- container lifecycle (external to the frozen sandbox argv) ----

    def _containers_for_image(self, image_ref: str) -> list[str]:
        listing = subprocess.run(
            self._client_command("ps", "-aq", "--filter", f"ancestor={image_ref}"),
            capture_output=True, timeout=30, check=False)
        if listing.returncode != 0:
            raise RunnerBlocked("container listing failed; refusing to run blind")
        return [line for line in
                listing.stdout.decode("utf-8", "replace").splitlines() if line.strip()]

    def _force_remove(self, container_ids: list[str]) -> None:
        for cid in container_ids:
            subprocess.run(self._client_command("rm", "-f", cid),
                           capture_output=True, timeout=30, check=False)

    def _abort(self, proc: subprocess.Popen, image_ref: str) -> None:
        # Kill the container at the daemon (SIGKILL via rm -f) so the attached
        # CLI exits with the real code (137); only then fall back to killing CLI.
        try:
            self._force_remove(self._containers_for_image(image_ref))
        except RunnerBlocked:
            pass
        try:
            proc.wait(timeout=self._config.kill_grace_seconds)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                proc.wait(timeout=self._config.kill_grace_seconds)
            except subprocess.TimeoutExpired:
                pass

    # ---- bounded execution ----

    def execute(self, request: ContainerRequest) -> RunnerObservation:
        if type(request) is not ContainerRequest:
            raise RunnerBlocked("typed ContainerRequest required")
        try:
            prepared = prepare_docker_sandbox(request)
        except SandboxPolicyError as exc:
            raise RunnerBlocked(f"POLICY_REJECTED:{exc}") from exc
        if (request.image_ref, request.command) not in self._config.allowlist:
            raise RunnerBlocked("EXECUTION_NOT_ALLOWLISTED")
        with self._lock:  # exactly one sandboxed container of ours at a time
            return self._execute_locked(request, prepared)

    def _execute_locked(self, request: ContainerRequest,
                        prepared: PreparedSandbox) -> RunnerObservation:
        self._verify_client_identity(request.docker_cli_sha256)
        server = self._verify_daemon()
        if self._containers_for_image(request.image_ref):
            raise RunnerBlocked("PREEXISTING_CONTAINER_AMBIGUITY")
        invocation = {
            "argv": list(prepared.argv),
            "client_argv_head": list(self._config.client_argv_head),
            "docker_cli_sha256": request.docker_cli_sha256,
            "request_sha256": prepared.request_sha256,
        }
        invocation_sha = _sha256(_canonical(invocation))
        command = self._client_command(*prepared.argv[1:])
        started = time.monotonic()
        try:
            proc = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as exc:
            raise RunnerBlocked("sandboxed process spawn failed") from exc

        cap = request.max_output_bytes
        streams = {"stdout": bytearray(), "stderr": bytearray()}
        truncated = {"stdout": False, "stderr": False}
        stop = threading.Event()

        def pump(name: str, pipe: Any) -> None:
            try:
                while not stop.is_set():
                    chunk = pipe.read1(65536)
                    if not chunk:
                        return
                    buffer = streams[name]
                    room = cap - len(buffer)
                    if room > 0:
                        buffer.extend(chunk[:room])
                    if len(chunk) > room:
                        truncated[name] = True
                        stop.set()
                        return
            except (OSError, ValueError):
                return

        readers = [threading.Thread(target=pump, args=("stdout", proc.stdout), daemon=True),
                   threading.Thread(target=pump, args=("stderr", proc.stderr), daemon=True)]
        for reader in readers:
            reader.start()

        status = "EXECUTED"
        deadline = started + request.wall_seconds
        try:
            while proc.poll() is None:
                if stop.is_set():
                    status = "OUTPUT_LIMIT_ENFORCED"
                    self._abort(proc, request.image_ref)
                    break
                if time.monotonic() > deadline:
                    status = "WALL_LIMIT_ENFORCED"
                    self._abort(proc, request.image_ref)
                    break
                time.sleep(0.02)
            proc.wait(timeout=self._config.kill_grace_seconds)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()  # after SIGKILL/TerminateProcess the reap must complete
        finally:
            stop.set()
            for reader in readers:
                reader.join(timeout=self._config.kill_grace_seconds)
        wall_ms = int((time.monotonic() - started) * 1000)
        exit_code = proc.returncode
        if not isinstance(exit_code, int):
            self._force_remove(self._containers_for_image(request.image_ref))
            raise RunnerBlocked("EXIT_CODE_UNOBSERVED")
        leftovers = self._containers_for_image(request.image_ref)
        if leftovers:
            self._force_remove(leftovers)
            if self._containers_for_image(request.image_ref):
                raise RunnerBlocked("CONTAINER_REAP_UNVERIFIED")
        return RunnerObservation(
            status=status, exit_code=exit_code,
            stdout=bytes(streams["stdout"]), stderr=bytes(streams["stderr"]),
            stdout_truncated=truncated["stdout"], stderr_truncated=truncated["stderr"],
            wall_ms=wall_ms, request_sha256=prepared.request_sha256,
            image_sha256=prepared.image_sha256, invocation_sha256=invocation_sha,
            daemon_server_version=server, containers_reaped_verified=True)

    # ---- deterministic assertion adjudication (never an LLM) ----

    @staticmethod
    def _parse_assertion(assertion: str) -> tuple[str, str]:
        if not isinstance(assertion, str) or not 1 <= len(assertion) <= 1024:
            raise RunnerBlocked("assertion must be bounded text")
        match = _EXIT_ASSERTION.fullmatch(assertion)
        if match:
            return ("exit_code", match.group(1))
        match = _HASH_ASSERTION.fullmatch(assertion)
        if match:
            return (match.group(1), match.group(2))
        match = _CONTAINS_ASSERTION.fullmatch(assertion)
        if match:
            return (match.group(1), match.group(2))
        raise RunnerBlocked(f"UNKNOWN_ASSERTION_FORM:{assertion[:64]}")

    @classmethod
    def _evaluate_assertion(cls, assertion: str, observation: RunnerObservation) -> bool:
        kind, expected = cls._parse_assertion(assertion)
        if kind == "exit_code":
            return observation.exit_code == int(expected)
        if kind == "stdout_sha256":
            return _sha256(observation.stdout) == expected
        if kind == "stderr_sha256":
            return _sha256(observation.stderr) == expected
        stream = observation.stdout if kind == "stdout_contains" else observation.stderr
        try:
            return expected in stream.decode("utf-8", "strict")
        except UnicodeDecodeError:
            return False
        raise RunnerBlocked(f"UNKNOWN_ASSERTION_FORM:{assertion[:64]}")

    @classmethod
    def adjudicate(cls, assertions: list[str],
                   observation: RunnerObservation) -> tuple[str, tuple[str, ...]]:
        """Return (verdict, reason_codes) from the real observation only."""
        failed = [a for a in assertions if not cls._evaluate_assertion(a, observation)]
        enforced: list[str] = []
        if observation.status == "WALL_LIMIT_ENFORCED":
            enforced.append("WALL_LIMIT_ENFORCED")
        if (observation.status == "OUTPUT_LIMIT_ENFORCED" or
                observation.stdout_truncated or observation.stderr_truncated):
            enforced.append("OUTPUT_LIMIT_ENFORCED")
        # A killed or truncated execution is not a completed behavior probe.
        # Matching its termination exit code or truncated output must never
        # promote a capability; preserve the enforced boundary as BLOCKED.
        if enforced:
            return ("BLOCKED", ("EXECUTION_INCOMPLETE", *enforced))
        if failed:
            codes = ["ASSERTIONS_FAILED", *(f"FAILED:{a}" for a in failed)]
            return ("REFUTED", tuple(codes))
        return ("SUPPORTED", ("ASSERTIONS_PASSED",))

    # ---- Evidence v1 build + attestation v2 sign ----

    def sign_evidence(self, evidence: dict[str, Any], *, image_sha256: str) -> dict[str, Any]:
        """HMAC-sign the full canonical Evidence payload; no semantic PASS implied."""
        validate_contract("evidence", evidence)
        observation = evidence["observation"]
        if (observation["execution_status"] != "EXECUTED" or
                observation["observer"] != OBSERVER_KIND or
                type(observation["exit_code"]) is not int or
                evidence["assessment"]["assessor_kind"] != ASSESSOR_KIND):
            raise RunnerBlocked("only deterministic real executions are signed")
        if not isinstance(image_sha256, str) or not _SHA.fullmatch(image_sha256):
            raise RunnerBlocked("exact executed image SHA256 required")
        attestation = {
            "schema_version": ATTESTATION_SCHEMA_VERSION,
            "evidence_sha256": _sha256(_canonical(evidence)),
            "runner_id": self._config.runner_id,
            "policy_sha256": self._config.policy_sha256,
            "image_sha256": image_sha256,
            "nonce": secrets.token_hex(16),
        }
        if not _NONCE.fullmatch(attestation["nonce"]):
            raise RunnerBlocked("nonce generation failed")
        attestation["mac_sha256"] = hmac.new(
            self._key, _canonical(attestation), hashlib.sha256).hexdigest()
        return attestation

    def execute_attest(self, request: ContainerRequest, *,
                       claim_id: str, capability_id: str,
                       source: dict[str, Any], target: dict[str, Any],
                       fixture: dict[str, Any], plan: dict[str, Any]) -> RunnerReceipt:
        """Run one frozen plan for real, adjudicate, then sign the full Evidence."""
        try:
            prepared = prepare_docker_sandbox(request)
        except SandboxPolicyError as exc:
            raise RunnerBlocked(f"POLICY_REJECTED:{exc}") from exc
        if not isinstance(plan, dict):
            raise RunnerBlocked("frozen execution plan required")
        assertions = plan.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            raise RunnerBlocked("plan must carry a nonempty assertion list")
        for assertion in assertions:
            self._parse_assertion(assertion)  # unknown forms blocked BEFORE any run
        frozen = freeze_execution_plan(plan.get("binding_id"), assertions, request)
        if plan != frozen:
            raise RunnerBlocked("FROZEN_PLAN_REQUEST_HASH_MISMATCH")
        if target.get("environment_id") != self._config.environment_id:
            raise RunnerBlocked("ENVIRONMENT_MISMATCH")
        if (target.get("package_sha256") != prepared.image_sha256 or
                target.get("identity") != request.image_ref):
            raise RunnerBlocked("TARGET_NOT_THE_EXECUTED_IMAGE")
        observation = self.execute(request)
        if observation.status not in _SIGNABLE_STATUSES or not observation.containers_reaped_verified:
            raise RunnerBlocked("execution not signable")
        verdict, reason_codes = self.adjudicate(assertions, observation)
        stdout_sha = _sha256(observation.stdout)
        stderr_sha = _sha256(observation.stderr)
        budget = {"wall_seconds": request.wall_seconds,
                  "max_output_bytes": request.max_output_bytes,
                  "network_allowed": False, "mutation_allowed": False}
        manifest = {"invocation_sha256": observation.invocation_sha256,
                    "request_sha256": observation.request_sha256,
                    "image_sha256": observation.image_sha256,
                    "stdout_sha256": stdout_sha, "stderr_sha256": stderr_sha,
                    "artifacts": [stdout_sha, stderr_sha]}
        evidence = {
            "schema_version": "app8-evidence-v1",
            "evidence_id": f"ev:{secrets.token_hex(16)}",
            "claim_id": claim_id,
            "capability_id": capability_id,
            "source": dict(source),
            "target": dict(target),
            "fixture": dict(fixture),
            "plan": {"plan_sha256": plan.get("plan_sha256", ""),
                     "binding_id": plan.get("binding_id", ""),
                     "assertions": list(assertions), "budget": budget},
            "observation": {"observer": OBSERVER_KIND, "execution_status": "EXECUTED",
                            "invocation_sha256": observation.invocation_sha256,
                            "exit_code": observation.exit_code,
                            "stdout_sha256": stdout_sha, "stderr_sha256": stderr_sha,
                            "artifacts": [stdout_sha, stderr_sha],
                            "recorded_at": datetime.now(timezone.utc).isoformat(
                                timespec="milliseconds").replace("+00:00", "Z")},
            "assessment": {"verdict": verdict, "assessor_kind": ASSESSOR_KIND,
                           "reason_codes": list(reason_codes)},
            "replay": {"manifest_sha256": _sha256(_canonical(manifest)),
                       "artifact_location": "LOCAL_CONTENT_ADDRESSED"},
        }
        attestation = self.sign_evidence(evidence, image_sha256=observation.image_sha256)
        return RunnerReceipt(evidence, attestation, observation,
                             observation.stdout, observation.stderr)


def freeze_execution_plan(binding_id: str, assertions: list[str],
                          request: ContainerRequest) -> dict[str, Any]:
    """Freeze plan identity = SHA256 over the exact binding/assertions/budget."""
    if not isinstance(binding_id, str) or not binding_id:
        raise RunnerBlocked("plan binding identity required")
    budget = {"wall_seconds": request.wall_seconds,
              "max_output_bytes": request.max_output_bytes,
              "network_allowed": False, "mutation_allowed": False}
    # The plan identifies the actual immutable image, argv, Docker-client
    # pin, execution limits and sandbox policy generated for this request.
    # A caller cannot reuse a signed plan with modified command arguments.
    try:
        prepared = prepare_docker_sandbox(request)
    except SandboxPolicyError as exc:
        raise RunnerBlocked(f"POLICY_REJECTED:{exc}") from exc
    core = {"binding_id": binding_id, "assertions": list(assertions),
            "budget": budget, "request_sha256": prepared.request_sha256}
    return {"plan_sha256": _sha256(_canonical(core)), **core}
