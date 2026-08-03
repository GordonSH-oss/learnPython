"""Optional adapter sketch; requires: pip install openai-agents and OPENAI_API_KEY."""

import os


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIP: set OPENAI_API_KEY to run this optional example")
        return
    try:
        from agents import Agent, Runner, function_tool
    except ImportError as exc:
        raise SystemExit("Install the optional dependency with: pip install openai-agents") from exc

    @function_tool
    def add(a: int, b: int) -> int:
        """Add two integers."""
        return a + b

    agent = Agent(name="calculator", instructions="Use the add tool when useful.", tools=[add])
    result = Runner.run_sync(agent, "What is 20 + 22?")
    print(result.final_output)


if __name__ == "__main__":
    main()
