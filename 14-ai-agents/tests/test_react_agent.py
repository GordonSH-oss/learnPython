import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from agent_core import AgentRunner, ModelResponse, ScriptedModel, ToolCall, ToolDefinition, ToolRegistry  # noqa: E402


def test_react_can_take_multiple_actions_after_observations():
    calls = []

    def lookup(query: str) -> str:
        calls.append(query)
        return "evidence"

    model = ScriptedModel([
        ModelResponse(tool_calls=(ToolCall("1", "lookup", {"query": "first"}),)),
        ModelResponse(tool_calls=(ToolCall("2", "lookup", {"query": "second"}),)),
        ModelResponse(content="综合两份资料后的答案"),
    ])
    tools = ToolRegistry()
    tools.register(ToolDefinition("lookup", "lookup", {"query": str}, lookup))
    result = AgentRunner(model, tools, max_steps=4).run("research", "multi-react")
    assert result.output == "综合两份资料后的答案"
    assert calls == ["first", "second"]
    assert result.state.step == 3


def test_react_turns_tool_failure_into_observation():
    def fail(query: str) -> str:
        raise LookupError(query)

    model = ScriptedModel([
        ModelResponse(tool_calls=(ToolCall("1", "lookup", {"query": "missing"}),)),
        ModelResponse(content="没有找到足够资料，无法确认。"),
    ])
    tools = ToolRegistry()
    tools.register(ToolDefinition("lookup", "lookup", {"query": str}, fail))
    result = AgentRunner(model, tools).run("research", "failed-react")
    assert result.output.startswith("没有找到")
    assert "LookupError" in result.state.tool_results[0].error


def test_react_loop_stops_on_repeated_action():
    call = ToolCall("new-id", "lookup", {"query": "same"})
    model = ScriptedModel([ModelResponse(tool_calls=(call,)), ModelResponse(tool_calls=(call,))])
    tools = ToolRegistry()
    tools.register(ToolDefinition("lookup", "lookup", {"query": str}, lambda query: "evidence"))
    result = AgentRunner(model, tools).run("research", "loop-react")
    assert result.stop_reason == "repeated_tool_calls"
