"""No shell or model text execution; never claim host isolation without proof."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from typing import Sequence

HASH = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class Invocation:
    executable: str
    argv: tuple[str, ...]
    expected_executable_sha256: str
    working_directory: str
    timeout_seconds: int = 10
    max_output_bytes: int = 65536
    network_allowed: bool = False
    mutation_allowed: bool = False
    network_isolation_verified: bool = False
    filesystem_isolation_verified: bool = False


@dataclass(frozen=True)
class Observation:
    status: str
    reason: str
    invocation_sha256: str
    executable_sha256: str | None
    exit_code: int | None
    stdout_sha256: str | None
    stderr_sha256: str | None
    output_truncated: bool


def _hash(data: bytes) -> str:
    return sha256(data).hexdigest()


def run_invocation(req: Invocation) -> Observation:
    """Execute only a reviewed exact binary under explicitly declared policy.

    Caller supplies argv, never raw LLM plan prose. This is a subprocess
    adapter, NOT a network/filesystem OS sandbox. Restricted requests FAIL
    CLOSED unless the caller has verified a separately provisioned sandbox.
    """
    desc = {"executable": req.executable, "argv": req.argv,
            "target_sha256": req.expected_executable_sha256,
            "cwd": req.working_directory, "timeout": req.timeout_seconds,
            "max_output_bytes": req.max_output_bytes, "network_allowed": req.network_allowed,
            "mutation_allowed": req.mutation_allowed}
    digest = _hash(json.dumps(desc, sort_keys=True, separators=(",", ":")).encode())

    def blocked(reason: str, executable_digest: str | None = None) -> Observation:
        return Observation("BLOCKED", reason, digest, executable_digest, None, None, None, False)

    if type(req.timeout_seconds) is not int or not 1 <= req.timeout_seconds <= 300:
        return blocked("BAD_TIME_BUDGET")
    if type(req.max_output_bytes) is not int or not 1 <= req.max_output_bytes <= 16_777_216:
        return blocked("BAD_OUTPUT_BUDGET")
    if not isinstance(req.argv, tuple) or len(req.argv) > 64 or any(
        not isinstance(x, str) or "\x00" in x or len(x) > 4096 for x in req.argv
    ):
        return blocked("BAD_ARGV")
    if not req.network_allowed and not req.network_isolation_verified:
        return blocked("NETWORK_ISOLATION_NOT_VERIFIED")
    if not req.mutation_allowed and not req.filesystem_isolation_verified:
        return blocked("FILESYSTEM_ISOLATION_NOT_VERIFIED")
    if not isinstance(req.expected_executable_sha256, str) or not HASH.fullmatch(req.expected_executable_sha256):
        return blocked("BAD_TARGET_HASH")
    exe = Path(req.executable)
    cwd = Path(req.working_directory)
    if not exe.is_absolute() or exe.is_symlink() or not exe.is_file():
        return blocked("INVALID_TARGET_EXECUTABLE")
    if not cwd.is_absolute() or not cwd.is_dir():
        return blocked("INVALID_WORKING_DIRECTORY")
    try:
        raw = exe.read_bytes()
    except OSError:
        return blocked("TARGET_UNREADABLE")
    actual = _hash(raw)
    if actual != req.expected_executable_sha256:
        return blocked("EXECUTABLE_HASH_MISMATCH", actual)
    try:
        result = subprocess.run((str(exe), *req.argv), cwd=str(cwd), env={},
                                shell=False, timeout=req.timeout_seconds,
                                capture_output=True, check=False)
    except subprocess.TimeoutExpired:
        return blocked("TIMEOUT", actual)
    except OSError:
        return blocked("SPAWN_FAILED", actual)
    if len(result.stdout) > req.max_output_bytes or len(result.stderr) > req.max_output_bytes:
        return Observation("BLOCKED", "OUTPUT_BUDGET_EXCEEDED", digest, actual,
                           result.returncode, _hash(result.stdout), _hash(result.stderr), True)
    return Observation("EXECUTED", "OBSERVATION_ONLY_NOT_EVIDENCE", digest, actual,
                       result.returncode, _hash(result.stdout), _hash(result.stderr), False)
