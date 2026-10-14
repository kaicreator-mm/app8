"""Trusted-host entrypoint for real HTTPS model invocation after frozen reservation.

Transport TLS and a host allowlist are operational measures, NOT external
provider attestation. A fake client in tests cannot certify a real model call.
No J calls: dynamic disagreement authorization needs a separate trusted gate.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import time
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

from app8.mla.ordered_host_ledger import OrderedMLAHostLedger
from app8.storage import EvidenceStore

_MAX_REQUEST = 500_000
_MAX_RESPONSE = 2_000_000
_KEY_ENV = re.compile(r"APP8_MLA_PROVIDER_[A-Z0-9_]{1,50}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_PROFILE_KEYS = frozenset({
    "origin", "path", "provider", "model_family", "model_id",
    "api_key_env", "billing_currency",
    "input_cost_microunits_per_million_tokens",
    "output_cost_microunits_per_million_tokens",
})
_ROLES = ("P", "R", "X")


class ProviderDispatchBlocked(ValueError):
    """Model call is missing a locked input, bounded budget or safe destination."""


def _canonical(obj: dict) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _validate_profile(profile: dict, approved_origins: set[str]) -> str:
    if not isinstance(profile, dict) or set(profile) != _PROFILE_KEYS:
        raise ProviderDispatchBlocked("complete frozen provider profile required")
    if not isinstance(approved_origins, set) or not approved_origins:
        raise ProviderDispatchBlocked("privileged approved HTTPS origins required")
    for key in ("origin", "path", "provider", "model_family",
                "model_id", "api_key_env", "billing_currency"):
        if not isinstance(profile[key], str) or not profile[key].strip():
            raise ProviderDispatchBlocked("invalid provider identity")
    origin = profile["origin"]
    parsed = urlsplit(origin)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ProviderDispatchBlocked("invalid HTTPS port") from exc
    host = parsed.hostname
    if (parsed.scheme != "https" or parsed.username or parsed.password
            or parsed.path or parsed.query or parsed.fragment
            or not host or "." not in host or port not in (None, 443)
            or host.endswith((".local", ".internal"))
            or origin not in approved_origins):
        raise ProviderDispatchBlocked("provider HTTPS origin not allowlisted")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ProviderDispatchBlocked("IP-literal provider endpoint forbidden")
    path = profile["path"]
    if (not path.startswith("/") or not path.endswith("/chat/completions")
            or "//" in path or "?" in path or "#" in path
            or ".." in path or "\\" in path or len(path) > 180):
        raise ProviderDispatchBlocked("invalid completion API path")
    if (not _KEY_ENV.fullmatch(profile["api_key_env"])
            or not re.fullmatch(r"[A-Z]{3}", profile["billing_currency"])):
        raise ProviderDispatchBlocked("invalid secret handle or budget currency")
    for key in ("input_cost_microunits_per_million_tokens",
                "output_cost_microunits_per_million_tokens"):
        if type(profile[key]) is not int or profile[key] < 0 or profile[key] > 10**12:
            raise ProviderDispatchBlocked("invalid fixed numeric pricing policy")
    return origin + path


def frozen_invocation_digest(profile: dict, request_bytes: bytes,
                             *, approved_origins: set[str]) -> str:
    """Freeze endpoint/model/pricing plus exact outbound body, never API key."""
    _validate_profile(profile, approved_origins)
    if (type(request_bytes) is not bytes
            or len(request_bytes) == 0 or len(request_bytes) > _MAX_REQUEST):
        raise ProviderDispatchBlocked("invalid or unbounded request bytes")
    try:
        body = json.loads(request_bytes)
    except (ValueError, UnicodeError) as exc:
        raise ProviderDispatchBlocked("model request is not valid JSON") from exc
    if (not isinstance(body, dict) or body.get("model") != profile["model_id"]
            or not isinstance(body.get("messages"), list)
            or not body["messages"]):
        raise ProviderDispatchBlocked("request model or messages mismatch")
    envelope = {
        "schema_version": "v04-mla-frozen-https-request-v1",
        "profile": profile,
        "body_sha256": hashlib.sha256(request_bytes).hexdigest(),
    }
    return hashlib.sha256(_canonical(envelope)).hexdigest()


class _DenyRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


class TrustedHTTPSCompletionClient:
    """Concrete production transport: urllib TLS verification, no redirects."""

    def send(self, url: str, request_bytes: bytes, api_key: str,
             timeout_seconds: int) -> bytes:
        req = Request(url, data=request_bytes, method="POST", headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        opener = build_opener(_DenyRedirect())
        with opener.open(req, timeout=timeout_seconds) as response:
            if response.status != 200:
                raise ProviderDispatchBlocked("provider returned non-200")
            data = response.read(_MAX_RESPONSE + 1)
        if len(data) > _MAX_RESPONSE:
            raise ProviderDispatchBlocked("provider response exceeds sealed size cap")
        return data


def _usage(raw: bytes, model: str, profile: dict, wall_ms: int) -> dict:
    if type(raw) is not bytes or not raw or len(raw) > _MAX_RESPONSE:
        raise ProviderDispatchBlocked("invalid bounded completion response")
    try:
        doc = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise ProviderDispatchBlocked("provider JSON response invalid") from exc
    if (not isinstance(doc, dict) or doc.get("model") != model
            or not isinstance(doc.get("choices"), list)
            or not doc["choices"] or not isinstance(doc["choices"][0], dict)
            or doc["choices"][0].get("finish_reason") != "stop"
            or not isinstance(doc["choices"][0].get("message"), dict)
            or not isinstance(doc["choices"][0]["message"].get("content"), str)
            or not doc["choices"][0]["message"]["content"].strip()):
        raise ProviderDispatchBlocked("missing, truncated or different-model answer")
    u = doc.get("usage")
    if not isinstance(u, dict):
        raise ProviderDispatchBlocked("provider token usage missing")
    inp, out = u.get("prompt_tokens"), u.get("completion_tokens")
    if (type(inp) is not int or type(out) is not int
            or inp < 0 or out < 0 or type(wall_ms) is not int or wall_ms < 0):
        raise ProviderDispatchBlocked("unreliable provider usage")
    # Ceil to integer micro-units for the explicitly frozen price table.
    numer = (
        inp * profile["input_cost_microunits_per_million_tokens"]
        + out * profile["output_cost_microunits_per_million_tokens"]
    )
    estimate = (numer + 999_999) // 1_000_000
    return {"input_tokens": inp, "output_tokens": out,
            "cost_microunits": estimate, "wall_ms": wall_ms}


def dispatch_frozen_completion(*, ledger: OrderedMLAHostLedger,
                               sealed_store: EvidenceStore, role: str,
                               asset: str, profile: dict, request_bytes: bytes,
                               approved_origins: set[str],
                               timeout_seconds: int = 60,
                               transport: TrustedHTTPSCompletionClient | None = None) -> dict:
    """Privileged single request; preserve all raw bytes off-repository.

    An unresolved reservation remains if a network call or usage check fails.
    Never retry under a new request/sample; operator must resolve incident.
    """
    if (type(ledger) is not OrderedMLAHostLedger
            or type(sealed_store) is not EvidenceStore
            or role not in _ROLES or type(timeout_seconds) is not int
            or not 1 <= timeout_seconds <= 120):
        raise ProviderDispatchBlocked("trusted host ledger/store/base role required")
    url = _validate_profile(profile, approved_origins)
    digest = frozen_invocation_digest(profile, request_bytes,
                                      approved_origins=approved_origins)
    if profile["billing_currency"] != ledger.frozen_billing_currency():
        raise ProviderDispatchBlocked("provider price currency differs from frozen spending ledger")
    secret = os.environ.get(profile["api_key_env"], "")
    if not secret or "\n" in secret or "\r" in secret:
        raise ProviderDispatchBlocked("provider credential unavailable or invalid")
    # Ensure actual request is retained in a private content addressed store
    # before atomically taking a spending reservation.
    if sealed_store.put_artifact(request_bytes) != hashlib.sha256(request_bytes).hexdigest():
        raise ProviderDispatchBlocked("sealed request integrity mismatch")
    reserved = ledger.reserve(role=role, asset=asset, case_id=None,
                              request_sha256=digest)
    client = transport if transport is not None else TrustedHTTPSCompletionClient()
    start = time.monotonic_ns()
    try:
        raw = client.send(url, request_bytes, secret, timeout_seconds)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        # Intentionally no retry; fail closed with an outstanding reservation.
        raise ProviderDispatchBlocked("HTTPS transport failed; unresolved reservation") from exc
    elapsed = (time.monotonic_ns() - start + 999_999) // 1_000_000
    if type(raw) is not bytes:
        raise ProviderDispatchBlocked("invalid HTTP response bytes")
    response_hash = sealed_store.put_artifact(raw)
    consumption = _usage(raw, profile["model_id"], profile, elapsed)
    record = ledger.record_response(reserve_seq=reserved["seq"],
                                    response_sha256=response_hash, usage=consumption)
    return {
        "schema_version": "v04-mla-https-dispatch-private-ref-v1",
        "status": "HOST_TRANSPORT_RESULT_RECORDED_NOT_INDEPENDENTLY_ATTESTED",
        "role": role, "asset": asset,
        "request_envelope_sha256": digest,
        "response_sha256": response_hash,
        "reservation_event_mac": reserved["event_mac"],
        "response_event_mac": record["event_mac"],
        "estimated_cost_microunits": consumption["cost_microunits"],
        "billing_currency": profile["billing_currency"],
        "trusted_remote_provider_identity_independently_verified": False,
        "external_pre_prediction_time_witness_verified": False,
        "human_gold_verified": False,
        "independent_behavior_oracle_verified": False,
        "capability_promotion_allowed": False,
        "formal_product_release_qualified": False,
    }
