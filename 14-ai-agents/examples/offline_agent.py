"""An entirely offline Agent loop. Run from the repository root."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))

from agent_core import AgentRunner, ModelResponse, ScriptedModel, ToolCall, ToolDefinition, ToolRegistry, calculator


def main() -> None:
    model = ScriptedModel([
        ModelResponse(tool_calls=(ToolCall("calc-1", "calculate", {"expression": "47 + 2"}),)),
        ModelResponse(content="答案：42"),
    ])
    tools = ToolRegistry()
    tools.register(ToolDefinition("calculate", "安全计算简单算式", {"expression": str}, calculator))
    result = AgentRunner(model, tools).run("40 加 2 等于多少？", session_id="demo")
    print(result.output)
    print(f"steps={result.state.step}, status={result.state.status}")


if __name__ == "__main__":
    main()
