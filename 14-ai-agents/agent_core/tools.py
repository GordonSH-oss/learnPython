from __future__ import annotations

from dataclasses import dataclass, field
import inspect
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from .types import ToolCall, ToolResult


ToolHandler = Callable[..., Any]
ApprovalPolicy = Callable[[ToolCall], bool]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: Mapping[str, type]
    handler: ToolHandler = field(repr=False, compare=False)
    requires_approval: bool = False
    idempotent: bool = True

    def schema(self) -> dict[str, Any]:
        type_names = {str: "string", int: "integer", float: "number", bool: "boolean"}
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    key: {"type": type_names.get(value, "string")}
                    for key, value in self.parameters.items()
                },
                "required": list(self.parameters),
                "additionalProperties": False,
            },
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self._results: dict[str, ToolResult] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def definitions(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def execute(self, call: ToolCall, approve: ApprovalPolicy | None = None) -> ToolResult:
        if call.id in self._results:
            result = self._results[call.id]
            return ToolResult(result.call_id, result.name, result.output, result.error, cached=True)

        tool = self._tools.get(call.name)
        if tool is None:
            return ToolResult(call.id, call.name, error=f"unknown tool: {call.name}")

        error = self._validate(tool, call.arguments)
        if error:
            return ToolResult(call.id, call.name, error=error)
        if tool.requires_approval and (approve is None or not approve(call)):
            return ToolResult(call.id, call.name, error="approval required")

        try:
            output = tool.handler(**call.arguments)
            if inspect.isawaitable(output):
                raise TypeError("async tools require an async runner")
            result = ToolResult(call.id, call.name, output=output)
        except Exception as exc:  # Tool errors are data returned to the model.
            result = ToolResult(call.id, call.name, error=f"{type(exc).__name__}: {exc}")

        if tool.idempotent or result.ok:
            self._results[call.id] = result
        return result

    @staticmethod
    def _validate(tool: ToolDefinition, arguments: Mapping[str, Any]) -> str | None:
        missing = set(tool.parameters) - set(arguments)
        extra = set(arguments) - set(tool.parameters)
        if missing:
            return f"missing arguments: {', '.join(sorted(missing))}"
        if extra:
            return f"unexpected arguments: {', '.join(sorted(extra))}"
        for name, expected in tool.parameters.items():
            if not isinstance(arguments[name], expected):
                return f"argument {name!r} must be {expected.__name__}"
        return None


def calculator(expression: str) -> float:
    allowed = set("0123456789.+-*/() %")
    if not expression or any(char not in allowed for char in expression):
        raise ValueError("expression contains unsupported characters")
    return float(eval(expression, {"__builtins__": {}}, {}))


def controlled_read(path: str, root: Path) -> str:
    requested = (root / path).resolve()
    safe_root = root.resolve()
    if requested != safe_root and safe_root not in requested.parents:
        raise PermissionError("path escapes the allowed root")
    return requested.read_text(encoding="utf-8")


def json_output(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)

