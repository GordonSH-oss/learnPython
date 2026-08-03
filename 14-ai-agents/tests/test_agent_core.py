import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from agent_core import (  # noqa: E402
    AgentRunner,
    InMemoryCheckpointer,
    InMemoryStore,
    MemoryRecord,
    Message,
    ModelResponse,
    ScriptedModel,
    ToolCall,
    ToolDefinition,
    ToolRegistry,
    calculator,
    controlled_read,
)


def test_agent_loop_executes_tool_then_answers():
    model = ScriptedModel([
        ModelResponse(tool_calls=(ToolCall("1", "calculate", {"expression": "2 + 3"}),)),
        ModelResponse(content="结果是 5"),
    ])
    tools = ToolRegistry()
    tools.register(ToolDefinition("calculate", "calculate", {"expression": str}, calculator))
    result = AgentRunner(model, tools).run("2+3", "s1")
    assert result.output == "结果是 5"
    assert result.state.tool_results[0].output == 5.0
    assert result.stop_reason == "stop"


def test_unknown_and_invalid_tools_are_data_errors():
    registry = ToolRegistry()
    registry.register(ToolDefinition("calculate", "calculate", {"expression": str}, calculator))
    unknown = registry.execute(ToolCall("x", "missing", {}))
    invalid = registry.execute(ToolCall("y", "calculate", {"expression": 3}))
    assert "unknown tool" in unknown.error
    assert "must be str" in invalid.error


def test_tool_calls_are_idempotent_by_call_id():
    calls = []
    registry = ToolRegistry()
    registry.register(ToolDefinition("save", "save", {"value": str}, lambda value: calls.append(value) or "ok"))
    call = ToolCall("same", "save", {"value": "one"})
    assert registry.execute(call).output == "ok"
    cached = registry.execute(call)
    assert cached.cached and calls == ["one"]


def test_approval_and_path_sandbox(tmp_path):
    registry = ToolRegistry()
    registry.register(ToolDefinition("write", "write", {"value": str}, lambda value: value, requires_approval=True))
    assert registry.execute(ToolCall("1", "write", {"value": "x"})).error == "approval required"
    assert registry.execute(ToolCall("2", "write", {"value": "x"}), lambda _: True).ok
    (tmp_path / "ok.txt").write_text("safe", encoding="utf-8")
    assert controlled_read("ok.txt", tmp_path) == "safe"
    try:
        controlled_read("../secret", tmp_path)
    except PermissionError:
        pass
    else:
        raise AssertionError("sandbox escape was allowed")


def test_memory_is_scoped_and_can_delete():
    store = InMemoryStore()
    store.put(MemoryRecord("a", "language", "用户喜欢 Python"))
    store.put(MemoryRecord("b", "language", "用户喜欢 Rust"))
    assert store.search("a", "Python")[0].value.endswith("Python")
    assert store.search("a", "Rust") == []
    assert store.delete("a", "language")


def test_checkpoint_resume_and_max_steps():
    checkpoint = InMemoryCheckpointer()
    model = ScriptedModel([ModelResponse(tool_calls=(ToolCall("1", "calculate", {"expression": "1"}),))])
    tools = ToolRegistry()
    tools.register(ToolDefinition("calculate", "calculate", {"expression": str}, calculator))
    result = AgentRunner(model, tools, checkpoint, max_steps=1).run("go", "resume")
    assert result.stop_reason == "max_steps"
    assert checkpoint.load("resume").step == 1


def test_message_is_typed():
    assert Message("user", "hello").role == "user"
