"""Offline capstone: retrieval as a tool, scoped memory, and citations."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from agent_core import (  # noqa: E402
    AgentRunner,
    InMemoryStore,
    MemoryRecord,
    ModelResponse,
    ScriptedModel,
    ToolCall,
    ToolDefinition,
    ToolRegistry,
)
from rag_pipeline import Chunk, retrieve  # noqa: E402


DOCUMENTS = [
    Chunk("guides/04-tools.md", "工具调用必须经过 schema 校验、权限检查和必要的人工审批。"),
    Chunk("guides/05-memory.md", "长期记忆保存用户事实和偏好，RAG 保存外部知识。"),
    Chunk("guides/08-state-and-durable-execution.md", "checkpoint 用于恢复执行状态，并不等于长期记忆。"),
]


def search_documents(query: str) -> str:
    matches = retrieve(query, DOCUMENTS, top_k=2)
    return json.dumps(
        [{"source": chunk.source, "text": chunk.text, "score": score} for chunk, score in matches],
        ensure_ascii=False,
    )


def build_research_agent() -> AgentRunner:
    model = ScriptedModel([
        ModelResponse(tool_calls=(ToolCall("search-1", "search_documents", {"query": "memory RAG 区别"}),)),
        ModelResponse(content="长期 memory 保存用户事实与偏好；RAG 提供外部知识。[guides/05-memory.md]"),
    ])
    tools = ToolRegistry()
    tools.register(
        ToolDefinition("search_documents", "检索本地课程资料并返回来源", {"query": str}, search_documents)
    )
    return AgentRunner(model, tools)


def main() -> None:
    memory = InMemoryStore()
    memory.put(MemoryRecord("learner-1", "answer_style", "用户偏好简洁并保留引用"))
    preference = memory.search("learner-1", "简洁 引用")[0].value
    result = build_research_agent().run(
        f"解释 memory 和 RAG 的区别。回答偏好：{preference}", session_id="research-1"
    )
    print(result.output)
    print(f"sources={result.state.tool_results[0].output}")


if __name__ == "__main__":
    main()
