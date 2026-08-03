from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Protocol

from .types import AgentState, Message, ToolResult


class Checkpointer(Protocol):
    def save(self, state: AgentState) -> None: ...
    def load(self, session_id: str) -> AgentState | None: ...


class InMemoryCheckpointer:
    def __init__(self) -> None:
        self.states: dict[str, AgentState] = {}

    def save(self, state: AgentState) -> None:
        self.states[state.session_id] = _copy_state(state)

    def load(self, session_id: str) -> AgentState | None:
        state = self.states.get(session_id)
        return _copy_state(state) if state else None


class JsonCheckpointer:
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def save(self, state: AgentState) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / f"{state.session_id}.json"
        path.write_text(json.dumps(asdict(state), ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, session_id: str) -> AgentState | None:
        path = self.directory / f"{session_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        data["messages"] = [Message(**item) for item in data["messages"]]
        data["tool_results"] = [ToolResult(**item) for item in data["tool_results"]]
        return AgentState(**data)


def _copy_state(state: AgentState) -> AgentState:
    return AgentState(
        session_id=state.session_id,
        messages=list(state.messages),
        step=state.step,
        status=state.status,
        tool_results=list(state.tool_results),
        metadata=dict(state.metadata),
    )

