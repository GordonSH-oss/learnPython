"""A dependency-free skeleton for the final AI knowledge-base project.

Run:
    python 16-capstone-project/app_skeleton.py
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    body: str


class InMemoryRepository:
    def __init__(self, documents: list[Document]) -> None:
        self._documents = documents

    def list_documents(self) -> list[Document]:
        return list(self._documents)


class KeywordRetriever:
    def __init__(self, repository: InMemoryRepository) -> None:
        self._repository = repository

    def retrieve(self, query: str) -> list[Document]:
        query_chars = set(query)
        scored = []
        for doc in self._repository.list_documents():
            score = len(query_chars & set(doc.title + doc.body))
            scored.append((score, doc))
        return [doc for score, doc in sorted(scored, reverse=True, key=lambda item: item[0]) if score > 0][:2]


class FakeLLMClient:
    def answer(self, question: str, context: list[Document]) -> str:
        titles = "、".join(doc.title for doc in context)
        return f"基于 {titles}，可以回答：{question}"


def ask(question: str, retriever: KeywordRetriever, llm: FakeLLMClient) -> dict[str, object]:
    context = retriever.retrieve(question)
    return {
        "question": question,
        "answer": llm.answer(question, context),
        "sources": [doc.doc_id for doc in context],
    }


def main() -> None:
    repository = InMemoryRepository(
        [
            Document("net-1", "网络请求", "HTTP 请求包含 URL、method、headers、body 和 response。"),
            Document("err-1", "错误处理", "HTTPError 的 body 有助于定位服务端错误。"),
        ]
    )
    result = ask("HTTP 请求失败怎么排查？", KeywordRetriever(repository), FakeLLMClient())
    print(result)


if __name__ == "__main__":
    main()
