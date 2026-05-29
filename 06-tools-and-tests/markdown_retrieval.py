"""Small Markdown retrieval helpers used by the learning examples.

The functions are intentionally dependency-free so they can run before the
project has a formal dependency manager.
"""

from __future__ import annotations

import re
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")


def load_docs(path: str | Path) -> list[str]:
    """Load a Markdown file and split it into searchable heading sections."""

    source = Path(path).read_text(encoding="utf-8")
    docs: list[str] = []
    current: list[str] = []

    def flush() -> None:
        if not current:
            return
        chunk = "\n".join(current).strip()
        lines = [line for line in chunk.splitlines() if line.strip()]
        has_body = any(not line.lstrip().startswith("#") for line in lines)
        if has_body:
            docs.append(chunk)

    for line in source.splitlines():
        if HEADING_RE.match(line):
            flush()
            current = [line]
        elif current:
            current.append(line)

    flush()
    return docs


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


def lexical_overlap_score(query: str, document: str) -> float:
    """Return a simple lexical score for combining with vector similarity."""

    query_tokens = _tokens(query)
    if not query_tokens:
        return 0.0

    document_tokens = _tokens(document)
    overlap = len(query_tokens & document_tokens) / len(query_tokens)

    compact_query = re.sub(r"\s+", "", query)
    compact_document = re.sub(r"\s+", "", document)
    exact_bonus = 0.0
    for size in range(min(6, len(compact_query)), 1, -1):
        for start in range(0, len(compact_query) - size + 1):
            phrase = compact_query[start : start + size]
            if phrase in compact_document:
                exact_bonus = size / max(len(compact_query), 1)
                break
        if exact_bonus:
            break

    return min(1.0, overlap + exact_bonus)


def hybrid_score(semantic_score: float, lexical_score: float) -> float:
    """Blend vector similarity with lexical overlap."""

    return semantic_score * 0.85 + lexical_score * 0.15
