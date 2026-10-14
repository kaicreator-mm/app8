"""Fail-closed public GitHub freeze witness for the privileged HTTPS bridge.

Live GitHub REST + GraphQL checks are performed before EVERY provider
dispatch. They attest public commitment chronology only, not remote provider
telemetry, semantic truth, or privileged-operator deletion/replay resistance.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
import re
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import URLError, HTTPError

from app8.mla.ordered_host_ledger import OrderedMLAHostLedger, MLAChronologyBlocked

_REPO = "kaicreator-mm/app8"
_ISSUE = 166
_PREFIX = "V04_MLA_FREEZE_WITNESS_V1"
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_ACCOUNT = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}\Z")


class ExternalFreezeWitnessBlocked(MLAChronologyBlocked):
    """GitHub cannot establish the pre-output public commitment order."""


class _DenyRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def _request_json(url: str, token: str, *, graphql: dict | None = None):
    """Only two fixed GitHub endpoints. Never follow a redirect."""
    if not (url.startswith("https://api.github.com/repos/kaicreator-mm/app8/issues/")
            or url == "https://api.github.com/graphql"):
        raise ExternalFreezeWitnessBlocked("unapproved witness endpoint")
    raw = None
    if graphql is not None:
        raw = json.dumps(graphql, separators=(",", ":")).encode("utf-8")
    req = Request(url, data=raw, method="POST" if raw is not None else "GET",
                  headers={
                      "Authorization": "Bearer " + token,
                      "Accept": "application/vnd.github+json",
                      "X-GitHub-Api-Version": "2022-11-28",
                      "Content-Type": "application/json",
                  })
    try:
        with build_opener(_DenyRedirect()).open(req, timeout=15) as resp:
            if resp.status != 200:
                raise ExternalFreezeWitnessBlocked("GitHub verification returned non-200")
            data = resp.read(250_000)
            if len(data) >= 250_000:
                raise ExternalFreezeWitnessBlocked("oversized GitHub witness body")
    except (URLError, HTTPError, OSError, TimeoutError) as exc:
        raise ExternalFreezeWitnessBlocked("GitHub witness network unavailable") from exc
    try:
        return json.loads(data)
    except (ValueError, UnicodeError) as exc:
        raise ExternalFreezeWitnessBlocked("GitHub witness reply is not valid JSON") from exc


def _iso(value) -> datetime:
    if not isinstance(value, str):
        raise ExternalFreezeWitnessBlocked("GitHub server timestamp missing")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ExternalFreezeWitnessBlocked("GitHub timestamp malformed") from exc
    if dt.tzinfo is None:
        raise ExternalFreezeWitnessBlocked("GitHub timezone missing")
    return dt.astimezone(timezone.utc)


def freeze_witness_body(manifest: dict, first_freeze_mac: str) -> str:
    """Exact GitHub comment body to post BEFORE first provider dispatch."""
    if not _SHA.fullmatch(first_freeze_mac):
        raise ExternalFreezeWitnessBlocked("first freeze event MAC missing")
    if not _SHA.fullmatch(manifest.get("campaign_nonce", "")):
        raise ExternalFreezeWitnessBlocked("unique campaign nonce missing")
    msg = (json.dumps(manifest, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False) + "\n").encode()
    return "\n".join((
        _PREFIX,
        "STUDY=V04-MLA-1",
        "CAMPAIGN_NONCE=" + manifest["campaign_nonce"],
        "MANIFEST_SHA256=" + hashlib.sha256(msg).hexdigest(),
        "FIRST_FREEZE_MAC=" + first_freeze_mac,
        "R2_VERDICT_COMMENT_ID=" + str(manifest["r2_verdict_comment_id"]),
    )) + "\n"


def _strict_single_witness(*, token: str, target_comment_id: int, exact_body: str):
    """Fail if any second freeze witness for the same study remains visible."""
    root = f"https://api.github.com/repos/{_REPO}/issues/{_ISSUE}/comments"
    observed = []
    for page in range(1, 11):
        records = _request_json(f"{root}?per_page=100&page={page}", token)
        if not isinstance(records, list):
            raise ExternalFreezeWitnessBlocked("GitHub witness listing unavailable")
        for row in records:
            body = row.get("body") if isinstance(row, dict) else None
            if (isinstance(body, str)
                    and body.startswith(_PREFIX + "\nSTUDY=V04-MLA-1\n")):
                observed.append((row.get("id"), body))
        if len(records) < 100:
            break
    else:
        raise ExternalFreezeWitnessBlocked("cannot exhaustively inspect witnesses")
    if observed != [(target_comment_id, exact_body)]:
        raise ExternalFreezeWitnessBlocked("missing, edited or duplicate campaign witness")


def verify_github_freeze_witness(ledger: OrderedMLAHostLedger) -> dict:
    """Verify current real GitHub evidence. No injected transport input allowed.

    This only guards the production HTTPS entrypoint; never label it a proof
    that another privileged process could not bypass this wrapper.
    """
    if type(ledger) is not OrderedMLAHostLedger:
        raise ExternalFreezeWitnessBlocked("privileged host ledger required")
    comments = ledger._load()
    if len(comments) != 1 or comments[0]["kind"] != "FREEZE":
        # Subsequent provider calls have RESERVE/RESPONSE events. They still
        # require the same exact first freeze event and no other FREEZE.
        if not comments or comments[0]["kind"] != "FREEZE" or any(
            e["kind"] == "FREEZE" for e in comments[1:]):
            raise ExternalFreezeWitnessBlocked("first freeze missing or ambiguous")
    manifest = comments[0]["data"]
    nonce = manifest.get("campaign_nonce")
    review_id = manifest.get("r2_verdict_comment_id")
    comment_id_str = os.environ.get("APP8_MLA_GITHUB_WITNESS_COMMENT_ID", "")
    expected_login = os.environ.get("APP8_MLA_GITHUB_WITNESS_AUTHOR", "")
    reviewer_login = os.environ.get("APP8_MLA_GITHUB_REVIEWER_AUTHOR", "")
    token = os.environ.get("APP8_MLA_GITHUB_WITNESS_TOKEN", "")
    if (not comment_id_str.isascii() or not comment_id_str.isdigit()
            or not 1 <= len(comment_id_str) <= 18
            or not _ACCOUNT.fullmatch(expected_login)
            or not _ACCOUNT.fullmatch(reviewer_login)
            or reviewer_login == expected_login
            or not isinstance(token, str) or len(token) < 20
            or "\n" in token or "\r" in token):
        raise ExternalFreezeWitnessBlocked("privileged GitHub witness config absent")
    comment_id = int(comment_id_str)
    expected_body = freeze_witness_body(manifest, comments[0]["mac"])
    url = f"https://api.github.com/repos/{_REPO}/issues/comments/{comment_id}"
    comment = _request_json(url, token)
    if (not isinstance(comment, dict)
            or comment.get("id") != comment_id
            or comment.get("body") != expected_body
            or not isinstance(comment.get("user"), dict)
            or comment["user"].get("login") != expected_login
            or not isinstance(comment.get("node_id"), str)
            or not comment["node_id"]):
        raise ExternalFreezeWitnessBlocked("witness author, body or identity mismatch")
    created = _iso(comment.get("created_at"))
    if created != _iso(comment.get("updated_at")):
        raise ExternalFreezeWitnessBlocked("GitHub witness edited after creation")
    graph = _request_json("https://api.github.com/graphql", token, graphql={
        "query": ("query($id:ID!){node(id:$id){... on IssueComment{"
                  "id createdAt lastEditedAt author{login} "
                  "userContentEdits(first:1){totalCount}}}}"),
        "variables": {"id": comment["node_id"]},
    })
    node = graph.get("data", {}).get("node") if isinstance(graph, dict) else None
    if (not isinstance(node, dict) or node.get("id") != comment["node_id"]
            or _iso(node.get("createdAt")) != created
            or node.get("lastEditedAt") is not None
            or node.get("author", {}).get("login") != expected_login
            or node.get("userContentEdits", {}).get("totalCount") != 0
            or graph.get("errors")):
        raise ExternalFreezeWitnessBlocked("GitHub GraphQL edit history or author unverifiable")
    if (type(review_id) is not int or review_id <= 0
            or review_id == comment_id):
        raise ExternalFreezeWitnessBlocked("independent reviewer identity not pinned")
    review = _request_json(
        f"https://api.github.com/repos/{_REPO}/issues/comments/{review_id}", token)
    body = review.get("body") if isinstance(review, dict) else None
    if (not isinstance(body, str)
            or "VERDICT=PASS_FOR_PILOT_PROVISIONAL_ONLY" not in body.splitlines()
            or not isinstance(review.get("user"), dict)
            or review["user"].get("login") != reviewer_login
            or _iso(review.get("created_at")) > created):
        raise ExternalFreezeWitnessBlocked("independent PASS-for-provisional reviewer not witnessed")
    _strict_single_witness(
        token=token, target_comment_id=comment_id, exact_body=expected_body)
    return {
        "status": "GITHUB_UNEDITED_PUBLIC_FREEZE_ORDER_VERIFIED_ONLY",
        "witness_comment_id": comment_id,
        "r2_verdict_comment_id": review_id,
        "campaign_nonce_sha256": hashlib.sha256(bytes.fromhex(nonce)).hexdigest(),
        "github_server_timestamp": created.isoformat(),
        "external_public_commitment_observed_before_this_dispatch": True,
        "provider_identity_independently_attested": False,
        "prior_deleted_witnesses_excluded": False,
        "host_operator_bypass_excluded": False,
        "independent_behavior_oracle_verified": False,
        "formal_product_release_qualified": False,
    }
