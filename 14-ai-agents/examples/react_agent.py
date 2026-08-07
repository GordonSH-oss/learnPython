"""A deterministic, offline ReAct-style Agent."""
from dataclasses import dataclass, field
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))

from agent_core import AgentRunner, ModelResponse, ScriptedModel, ToolCall, ToolDefinition, ToolRegistry  # noqa: E402


@dataclass
class ReactTrace:
    events: list[dict[str, str]] = field(default_factory=list)

    def record(self, kind: str, summary: str) -> None:
        self.events.append({"kind": kind, "summary": summary})


def search(query: str) -> str:
    if query == "Python release":
        return "Python 3.14 was released in 2025. source=release-notes"
    raise LookupError("no matching source")


def main() -> None:
    trace = ReactTrace()
    model = ScriptedModel([
        ModelResponse(content="先查找 Python release 资料", tool_calls=(ToolCall("search-1", "search", {"query": "Python release"}),)),
        ModelResponse(content="根据 release-notes，Python 3.14 于 2025 年发布。"),
    ])
    tools = ToolRegistry()
    tools.register(ToolDefinition("search", "搜索本地资料", {"query": str}, search))
    trace.record("decision", "需要外部证据，调用 search")
    result = AgentRunner(model, tools).run("Python 3.14 何时发布？", session_id="react-demo")
    trace.record("observation", str(result.state.tool_results[0].output))
    trace.record("final", result.output)
    print(result.output)
    for event in trace.events:
        print(f"{event['kind']}: {event['summary']}")


if __name__ == "__main__":
    main()
