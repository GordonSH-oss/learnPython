from __future__ import annotations

from collections import deque
from typing import Iterable, Sequence

from .tools import ToolDefinition
from .types import Message, ModelResponse


class ScriptedModel:
    """Return deterministic responses so Agent behavior can be tested offline."""

    def __init__(self, responses: Iterable[ModelResponse]) -> None:
        self.responses = deque(responses)
        self.calls: list[list[Message]] = []

    def complete(self, messages: Sequence[Message], tools: Sequence[ToolDefinition]) -> ModelResponse:
        self.calls.append(list(messages))
        if not self.responses:
            raise RuntimeError("scripted model has no response left")
        return self.responses.popleft()

