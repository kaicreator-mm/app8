"""Reuses SE14 BM25-Okapi k1=1.2, b=0.75; no relevance PASS implied."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import unicodedata
from typing import Any, Iterable

from app8.readiness import Readiness

K1 = 1.2
B = 0.75


def tokenize(value: str) -> list[str]:
    text = unicodedata.normalize("NFKC", value).lower()
    parts: list[str] = []
    current: list[str] = []
    for char in text:
        if unicodedata.category(char)[0] in ("L", "N"):
            current.append(char)
        elif current:
            parts.append("".join(current))
            current = []
    if current:
        parts.append("".join(current))
    return parts


@dataclass(frozen=True)
class SearchResult:
    capability_id: str
    revision: int
    score: float
    export_ready: bool
    lifecycle_state: str
    source_revision: str
    target_identity: str


class CapabilityIndex:
    """In-memory baseline; metadata includes computed readiness, not LLM claims."""

    def __init__(self, records: Iterable[tuple[dict[str, Any], Readiness]]):
        self.docs: list[tuple[dict[str, Any], Readiness, Counter[str], int]] = []
        seen: set[tuple[str, int]] = set()
        for cap, status in records:
            cid, rev = cap["capability_id"], cap["revision"]
            if (cid, rev) in seen:
                raise ValueError("duplicate Capability revision in search index")
            seen.add((cid, rev))
            semantic = cap["semantic"]
            # Preserve observable negative boundaries and errors, never use private labels.
            fields = [semantic["name"], semantic["purpose"], semantic["user_job"]]
            for key in ("variants", "constraints", "negative_boundaries", "failure_modes"):
                fields.extend(semantic[key])
            tokens = tokenize(" ".join(fields))
            self.docs.append((cap, status, Counter(tokens), len(tokens)))
        if len(self.docs) > 100000:
            raise ValueError("index item budget exceeded")

    def search(self, query: str, *, top_k: int = 5, only_export_ready: bool = False) -> list[SearchResult]:
        if not isinstance(query, str) or not query.strip():
            return []
        if type(top_k) is not int or not 1 <= top_k <= 100:
            raise ValueError("top_k out of bounds")
        docs = [d for d in self.docs if not only_export_ready or d[1].export_ready]
        if not docs:
            return []
        n = len(docs)
        avg_len = sum(row[3] for row in docs) / n
        df: Counter[str] = Counter(token for _, _, tf, _ in docs for token in tf)
        q = sorted(set(tokenize(query)))
        if not q:
            return []
        ranked: list[SearchResult] = []
        for cap, status, tf, length in docs:
            score = 0.0
            for token in q:
                freq = tf[token]
                if not freq:
                    continue
                idf = math.log1p((n - df[token] + 0.5) / (df[token] + 0.5))
                norm = freq + K1 * (1 - B + B * length / avg_len) if avg_len else freq + K1
                score += idf * (freq * (K1 + 1)) / norm
            if score == 0:
                continue
            ranked.append(SearchResult(
                cap["capability_id"], cap["revision"], score,
                status.export_ready, status.lifecycle_state,
                cap["source"]["revision"], cap["target"]["identity"],
            ))
        ranked.sort(key=lambda row: (-row.score, row.capability_id, row.revision))
        return ranked[:top_k]
