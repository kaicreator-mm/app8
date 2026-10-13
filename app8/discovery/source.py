"""Read only byte-exact, allowlisted source files. Never infer a runtime capability."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

_TEXT_SUFFIXES = frozenset({".md", ".rst", ".txt", ".json", ".yaml", ".yml", ".py", ".go", ".rs", ".c", ".h", ".cpp", ".hpp", ".js", ".ts", ".xml", ".html", ".sh", ".ps1"})
_PIXEL_SUFFIXES = frozenset({".png", ".jpeg", ".jpg", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".ico", ".pdf"})
_SHA = re.compile(r"[0-9a-f]{64}\Z")


class SourceError(ValueError):
    """Source is not included in the explicitly frozen readable authority."""


@dataclass(frozen=True)
class SourceDocument:
    repository: str
    revision: str
    relative_path: str
    content_sha256: str
    text: str
    status: str = "SOURCE_ONLY_UNVERIFIED"


def discover_source(root: str | Path, relative_path: str, *, repository: str,
                    revision: str, expected_sha256: str, max_bytes: int = 2_000_000) -> SourceDocument:
    """Read explicitly pinned text and return provenance, never a semantic Gold label.

    Callers must supply reviewed expected_sha256 from an allowlist. Paths, files,
    binary content, pixel surfaces and unexpected size fail closed.
    """
    if not isinstance(repository, str) or not repository or not isinstance(revision, str) or not revision:
        raise SourceError("source repository and revision are mandatory")
    if not isinstance(relative_path, str) or not relative_path or "\\" in relative_path:
        raise SourceError("invalid relative source path")
    if not isinstance(expected_sha256, str) or not _SHA.fullmatch(expected_sha256):
        raise SourceError("exact source SHA-256 is mandatory")
    path_rel = Path(relative_path)
    if path_rel.is_absolute() or any(p in ("..", ".") for p in path_rel.parts):
        raise SourceError("out-of-root traversal is forbidden")
    suffix = path_rel.suffix.lower()
    if suffix in _PIXEL_SUFFIXES:
        raise SourceError("PIXEL_DERIVED_AUTOMATION_FORBIDDEN")
    if suffix not in _TEXT_SUFFIXES:
        raise SourceError("UNSUPPORTED_SOURCE_FORMAT")
    directory = Path(root).resolve(strict=True)
    candidate = directory / path_rel
    if candidate.is_symlink() or any(p.is_symlink() for p in list(candidate.parents)[:-1] if p != directory):
        raise SourceError("source symlinks forbidden")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(directory) or not resolved.is_file():
        raise SourceError("source escapes frozen root or is not a file")
    if not isinstance(max_bytes, int) or max_bytes <= 0:
        raise SourceError("invalid source-size budget")
    if resolved.stat().st_size > max_bytes:
        raise SourceError("source exceeds bounded read")
    with resolved.open("rb") as source:
        data = source.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise SourceError("source exceeds bounded read")
    digest = sha256(data).hexdigest()
    if digest != expected_sha256:
        raise SourceError("FROZEN_SOURCE_HASH_MISMATCH")
    try:
        text = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise SourceError("UNSUPPORTED_SOURCE_ENCODING") from exc
    if "\x00" in text:
        raise SourceError("UNSUPPORTED_BINARY_SOURCE")
    return SourceDocument(repository, revision, relative_path, digest, text)
