"""Optional LangGraph sketch; requires: pip install langgraph."""

import os


def main() -> None:
    if not os.getenv("RUN_LANGGRAPH_EXAMPLE"):
        print("SKIP: set RUN_LANGGRAPH_EXAMPLE=1 to run this optional example")
        return
    try:
        from typing import TypedDict
        from langgraph.graph import END, StateGraph
    except ImportError as exc:
        raise SystemExit("Install the optional dependency with: pip install langgraph") from exc

    class State(TypedDict):
        question: str
        answer: str

    def answer(state: State) -> State:
        return {**state, "answer": f"离线节点收到：{state['question']}"}

    graph = StateGraph(State)
    graph.add_node("answer", answer)
    graph.set_entry_point("answer")
    graph.add_edge("answer", END)
    print(graph.compile().invoke({"question": "hello", "answer": ""}))


if __name__ == "__main__":
    main()
