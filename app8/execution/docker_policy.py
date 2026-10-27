"""Build a restrictive Docker command; NEVER launch it or certify host isolation.

A returned plan is untrusted configuration until the real-host runner verifies
Docker CLI identity, container daemon controls, wall time and output limits.
No image tag, host mount, Docker socket, network or elevated permissions may
be added through this builder.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import PurePosixPath
import re

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_IMAGE = re.compile(r"[a-z0-9][a-z0-9._-]*(?:/[a-z0-9][a-z0-9._-]*)+@sha256:([0-9a-f]{64})\Z")
_LOCAL_IMAGE_ID = re.compile(r"sha256:([0-9a-f]{64})\Z")  # Host-local content address, not RepoDigest
_FORBIDDEN_COMMANDS = frozenset({"/bin/sh", "/bin/bash", "/usr/bin/bash", "/bin/dash", "/usr/bin/env"})


class SandboxPolicyError(ValueError):
    """Unsafe, ambiguous or unpinned sandbox request."""


@dataclass(frozen=True)
class ContainerRequest:
    image_ref: str
    command: str
    args: tuple[str, ...] = ()
    docker_cli_sha256: str = ""
    wall_seconds: int = 30
    max_output_bytes: int = 65536
    memory_mib: int = 256
    pids_limit: int = 64
    cpu_milli: int = 500


@dataclass(frozen=True)
class PreparedSandbox:
    argv: tuple[str, ...]
    request_sha256: str
    image_sha256: str
    docker_cli_sha256_expected: str
    wall_seconds_runner_must_enforce: int
    max_output_bytes_runner_must_enforce: int
    status: str = "NOT_RUN"
    host_isolation_verified: bool = False


def _strict_int(number: object, minimum: int, maximum: int, field: str) -> None:
    if type(number) is not int or not minimum <= number <= maximum:
        raise SandboxPolicyError(f"{field}: bounded integer required")


def prepare_docker_sandbox(request: ContainerRequest) -> PreparedSandbox:
    """Prepare fixed Docker argv for a *separately verified* Docker Linux host.

    This function intentionally has NO subprocess execution path. A real-host
    runner must verify CLI binary SHA256 and sandbox escape/limit tests first.
    """
    if not isinstance(request, ContainerRequest):
        raise SandboxPolicyError("typed ContainerRequest required")
    if not isinstance(request.image_ref, str):
        raise SandboxPolicyError("image must be text")
    # Immutable registry RepoDigest OR the exact content-addressed Docker
    # image ID present on this approved Host. Never accept a tag, a pseudo
    # repo@config-ID alias, a truncated ID, or a remote fetch.
    m = _IMAGE.fullmatch(request.image_ref) or _LOCAL_IMAGE_ID.fullmatch(request.image_ref)
    if m is None:
        raise SandboxPolicyError(
            "image must be registry/path@sha256:<64hex> or local sha256:<64hex>; tags forbidden"
        )
    if not isinstance(request.docker_cli_sha256, str) or not _DIGEST.fullmatch(request.docker_cli_sha256):
        raise SandboxPolicyError("exact Docker CLI SHA256 must be frozen")
    if not isinstance(request.command, str) or not request.command.startswith("/"):
        raise SandboxPolicyError("absolute in-container command path required")
    command = PurePosixPath(request.command)
    if (".." in request.command.split("/") or "\x00" in request.command or
            "\n" in request.command or request.command in _FORBIDDEN_COMMANDS or
            str(command) != request.command or len(request.command) > 256):
        raise SandboxPolicyError("unapproved or ambiguous in-container command")
    if (not isinstance(request.args, tuple) or len(request.args) > 64 or
            any(not isinstance(arg, str) or len(arg) > 4096 or "\x00" in arg
                for arg in request.args)):
        raise SandboxPolicyError("bounded argument tuple required")
    _strict_int(request.wall_seconds, 1, 300, "wall_seconds")
    _strict_int(request.max_output_bytes, 1, 1_048_576, "max_output_bytes")
    _strict_int(request.memory_mib, 64, 2048, "memory_mib")
    _strict_int(request.pids_limit, 1, 128, "pids_limit")
    _strict_int(request.cpu_milli, 100, 2000, "cpu_milli")

    # No bind mounts, Docker socket, privileged flags, env injection, host PID,
    # host networking or docker daemon endpoint overrides are accepted here.
    argv = (
        "docker", "run", "--rm", "--pull=never", "--network=none",
        "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges=true",
        "--pids-limit", str(request.pids_limit),
        "--memory", f"{request.memory_mib}m",
        "--memory-swap", f"{request.memory_mib}m",
        "--cpus", f"{request.cpu_milli / 1000:g}",
        "--user", "65534:65534", "--ipc=none", "--no-healthcheck",
        "--tmpfs", "/tmp:rw,nosuid,noexec,nodev,size=16m,mode=1777",
        "--workdir", "/tmp",
        request.image_ref, request.command, *request.args,
    )
    signed = {
        "docker_cli_sha256_expected": request.docker_cli_sha256,
        "image": request.image_ref, "command": request.command,
        "args": request.args, "wall_seconds": request.wall_seconds,
        "max_output_bytes": request.max_output_bytes,
        "memory_mib": request.memory_mib, "pids_limit": request.pids_limit,
        "cpu_milli": request.cpu_milli,
    }
    request_hash = sha256(json.dumps(signed, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()
    return PreparedSandbox(argv, request_hash, m.group(1), request.docker_cli_sha256,
                           request.wall_seconds, request.max_output_bytes)
