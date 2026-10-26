"""One scoped Agent-facing CLI consumer over the existing trusted Docker runner.

This module is the bridge, not a new command executor or authorization service.
The CC04 journey must independently establish real Agent caller/session identity.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Mapping

from app8.evidence.attestation import AttestationGate
from app8.execution.docker_policy import ContainerRequest
from app8.execution.docker_runner import RealDockerRunner
from app8.qualification.service import qualify_stored_capability
from app8.storage import EvidenceStore


class AgentConsumerBlocked(ValueError):
    """No qualified scoped Capability / approved target tool is available."""


@dataclass(frozen=True)
class AgentToolResult:
    capability_id: str
    revision: int
    binding_id: str
    evidence_snapshot_sha256: str
    source_sha256: str
    target_sha256: str
    session_id: str
    invocation_sha256: str
    execution_status: str
    exit_code: int | None
    stdout_sha256: str
    stderr_sha256: str
    output_class: str = "REAL_RUNNER_OBSERVATION_NOT_PRODUCT_RELEASE"


def run_agent_cli(
    capability: dict[str, Any],
    *,
    store: EvidenceStore,
    gate: AttestationGate,
    signed_attestations: Mapping[str, dict[str, Any]],
    runner: RealDockerRunner,
    binding_id: str,
    docker_cli_sha256: str,
    args: tuple[str, ...],
    session_id: str,
) -> AgentToolResult:
    """Requalify full ledger on *every* real invocation, then use trusted runner.

    Agent caller/session is supplied by the host and must be independently
    authenticated by CC04; this module does NOT certify caller authenticity.
    No caller path/target override, arbitrary subprocess or model permission.
    """
    if (type(store) is not EvidenceStore or type(gate) is not AttestationGate
            or type(runner) is not RealDockerRunner):
        raise AgentConsumerBlocked("trusted store, attestation gate and runner required")
    if not isinstance(session_id, str) or not 1 <= len(session_id) <= 128 or any(ord(c) < 33 for c in session_id):
        raise AgentConsumerBlocked("bounded trusted session identity required")
    if not isinstance(binding_id, str) or not binding_id:
        raise AgentConsumerBlocked("exact binding ID required")
    qualified = qualify_stored_capability(
        capability, store=store, attestation_gate=gate, signed_attestations=signed_attestations
    )
    if qualified.status != "SCOPED_EXPORT_READY" or not qualified.readiness.export_ready:
        raise AgentConsumerBlocked("Capability not qualified for scoped consumption")
    bindings = [b for b in capability["bindings"]
                if b["kind"] == "CLI" and b["binding_id"] == binding_id]
    if len(bindings) != 1:
        raise AgentConsumerBlocked("requested pinned CLI binding not available")
    if any(b["side_effects"] for b in bindings):
        raise AgentConsumerBlocked("mutating CLI bindings excluded from MVP consumer")
    target = capability["target"]
    image_ref = target["identity"]
    if not isinstance(image_ref, str) or not image_ref.endswith("@sha256:" + target["package_sha256"]):
        raise AgentConsumerBlocked("target is not exact pinned OCI artifact")
    if runner._config.environment_id != target["environment_id"]:
        raise AgentConsumerBlocked("trusted runner environment mismatch")
    req = ContainerRequest(image_ref=image_ref,
                           command=bindings[0]["address"],
                           args=args, docker_cli_sha256=docker_cli_sha256)
    observation = runner.execute(req)
    result = AgentToolResult(
        capability_id=capability["capability_id"],
        revision=capability["revision"],
        binding_id=binding_id,
        evidence_snapshot_sha256=qualified.evidence_snapshot_sha256,
        source_sha256=capability["source"]["content_sha256"],
        target_sha256=target["package_sha256"],
        session_id=session_id,
        invocation_sha256=observation.invocation_sha256,
        execution_status=observation.status,
        exit_code=observation.exit_code,
        stdout_sha256=sha256(observation.stdout).hexdigest(),
        stderr_sha256=sha256(observation.stderr).hexdigest(),
    )
    store.append_event(capability["capability_id"], "AGENT_CLI_OBSERVED", vars(result))
    return result
