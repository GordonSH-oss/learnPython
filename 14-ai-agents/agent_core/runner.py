from __future__ import annotations

import json
from typing import Protocol, Sequence

from .checkpoint import Checkpointer, InMemoryCheckpointer
from .tools import ApprovalPolicy, ToolDefinition, ToolRegistry
from .types import AgentResult, AgentState, Message, ModelResponse


class ModelClient(Protocol):
    def complete(self, messages: Sequence[Message], tools: Sequence[ToolDefinition]) -> ModelResponse: ...


class AgentRunner:
    def __init__(
        self,
        model: ModelClient,
        tools: ToolRegistry | None = None,
        checkpointer: Checkpointer | None = None,
        max_steps: int = 8,
        approve: ApprovalPolicy | None = None,
    ) -> None:
        self.model = model
        self.tools = tools or ToolRegistry()
        self.checkpointer = checkpointer or InMemoryCheckpointer()
        self.max_steps = max_steps
        self.approve = approve

    def run(self, prompt: str, session_id: str = "default", resume: bool = False) -> AgentResult:
        state = self.checkpointer.load(session_id) if resume else None
        state = state or AgentState(session_id=session_id)
        state.messages.append(Message("user", prompt))
        state.status = "running"
        seen_batches: set[tuple[tuple[str, str], ...]] = set()

        while state.step < self.max_steps:
            state.step += 1
            response = self.model.complete(state.messages, self.tools.definitions())
            if not response.tool_calls:
                state.messages.append(Message("assistant", response.content))
                state.status = "completed"
                self.checkpointer.save(state)
                return AgentResult(response.content, state, response.finish_reason)

            signature = tuple(
                (call.name, json.dumps(call.arguments, sort_keys=True, ensure_ascii=False))
                for call in response.tool_calls
            )
            if signature in seen_batches:
                state.status = "stopped"
                self.checkpointer.save(state)
                return AgentResult("", state, "repeated_tool_calls")
            seen_batches.add(signature)

            state.messages.append(Message("assistant", response.content or "调用工具"))
            for call in response.tool_calls:
                result = self.tools.execute(call, self.approve)
                state.tool_results.append(result)
                content = json.dumps(
                    {"output": result.output, "error": result.error}, ensure_ascii=False, default=str
                )
                state.messages.append(Message("tool", content, name=call.name, tool_call_id=call.id))
            self.checkpointer.save(state)

        state.status = "stopped"
        self.checkpointer.save(state)
        return AgentResult("", state, "max_steps")

