"""Dependency-free toy RAG pipeline.

Run:
    python 14-ai-agents/rag_pipeline.py
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")


@dataclass(frozen=True)
class Chunk:
    source: str
    text: str


def tokenize(text: str) -> Counter[str]:
    return Counter(token.lower() for token in TOKEN_RE.findall(text))


def score(query: str, chunk: Chunk) -> float:
    query_tokens = tokenize(query)
    chunk_tokens = tokenize(chunk.text)
    if not query_tokens:
        return 0.0
    overlap = sum((query_tokens & chunk_tokens).values())
    return overlap / sum(query_tokens.values())


def retrieve(query: str, chunks: list[Chunk], top_k: int = 2) -> list[tuple[Chunk, float]]:
    ranked = sorted(((chunk, score(query, chunk)) for chunk in chunks), key=lambda item: item[1], reverse=True)
    return [item for item in ranked[:top_k] if item[1] > 0]


def build_answer(query: str, matches: list[tuple[Chunk, float]]) -> str:
    if not matches:
        return "没有在本地资料中找到足够相关的内容。"
    citations = "\n".join(f"- {chunk.source}: {chunk.text}" for chunk, _ in matches)
    return f"问题：{query}\n\n可引用资料：\n{citations}\n\n回答：请基于以上资料组织最终答案。"


def main() -> None:
    chunks = [
        Chunk("09-networking/README.md", "urllib.request 需要手动编码 JSON 请求体并解码响应。"),
        Chunk("02-database/README.md", "Milvus 适合向量相似度搜索，SQLAlchemy 适合结构化数据。"),
        Chunk("10-error-handle/README.md", "HTTPError 的响应正文通常包含服务端返回的具体错误原因。"),
    ]
    query = "urllib 请求失败时如何排查错误正文？"
    matches = retrieve(query, chunks)
    print(build_answer(query, matches))


if __name__ == "__main__":
    main()
