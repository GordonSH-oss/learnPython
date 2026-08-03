from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Protocol

from .types import Message


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


@dataclass(frozen=True)
class MemoryRecord:
    session_id: str
    key: str
    value: str
    kind: str = "semantic"
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.now(timezone.utc).isoformat())


class MemoryStore(Protocol):
    def put(self, record: MemoryRecord) -> None: ...
    def search(self, session_id: str, query: str, limit: int = 5) -> list[MemoryRecord]: ...
    def delete(self, session_id: str, key: str) -> bool: ...


class InMemoryStore:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], MemoryRecord] = {}

    def put(self, record: MemoryRecord) -> None:
        self._records[(record.session_id, record.key)] = record

    def search(self, session_id: str, query: str, limit: int = 5) -> list[MemoryRecord]:
        terms = _tokens(query)
        candidates = [r for (scope, _), r in self._records.items() if scope == session_id]
        scored = [
            (len(terms & _tokens(record.value)), record)
            for record in candidates
        ]
        return [record for score, record in sorted(scored, key=lambda item: item[0], reverse=True)[:limit] if score]

    def delete(self, session_id: str, key: str) -> bool:
        return self._records.pop((session_id, key), None) is not None

    def records(self) -> list[MemoryRecord]:
        return list(self._records.values())


class JsonMemoryStore(InMemoryStore):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path
        if path.exists():
            for item in json.loads(path.read_text(encoding="utf-8")):
                super().put(MemoryRecord(**item))

    def put(self, record: MemoryRecord) -> None:
        super().put(record)
        self._flush()

    def delete(self, session_id: str, key: str) -> bool:
        deleted = super().delete(session_id, key)
        if deleted:
            self._flush()
        return deleted

    def _flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([asdict(record) for record in self.records()], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def trim_messages(messages: list[Message], max_messages: int) -> list[Message]:
    if len(messages) <= max_messages:
        return list(messages)
    system = [message for message in messages if message.role == "system"][:1]
    tail_size = max(0, max_messages - len(system))
    tail = [message for message in messages if message.role != "system"][-tail_size:]
    return system + tail


def summarize_messages(messages: list[Message]) -> str:
    lines = [f"{message.role}: {message.content[:120]}" for message in messages]
    return " | ".join(lines)
