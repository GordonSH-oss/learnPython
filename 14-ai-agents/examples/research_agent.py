"""Offline capstone: retrieval, scoped memory, and sandboxed code execution."""
from pathlib import Path
import json
import sys
import tempfile

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from agent_core import (  # noqa: E402
    AgentRunner,
    InMemoryStore,
    LocalProcessSandbox,
    MemoryRecord,
    ModelResponse,
    PythonCode,
    Sandbox,
    SandboxPolicy,
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


def _scope(tenant_id: str, session_id: str) -> str:
    if not tenant_id or not session_id or any(value in tenant_id + session_id for value in "/\\"):
        raise ValueError("tenant and session identifiers must be non-empty path-safe values")
    return f"{tenant_id}:{session_id}"


def execute_code(
    source: str,
    *,
    tenant_id: str,
    session_id: str,
    workspace_root: Path,
    sandbox: Sandbox,
) -> str:
    """Execute typed code through the configured sandbox and return safe metadata."""
    scope = _scope(tenant_id, session_id)
    result = sandbox.run(
        PythonCode(source),
        SandboxPolicy(workspace=workspace_root / tenant_id / session_id),
    )
    return json.dumps(
        {
            "scope": scope,
            "executor": result.policy_summary.get("executor"),
            "reason": result.reason.value,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        },
        ensure_ascii=False,
    )


def build_research_agent(
    tenant_id: str = "tenant-1",
    session_id: str = "research-1",
    *,
    workspace_root: Path | None = None,
    memory: InMemoryStore | None = None,
    sandbox: Sandbox | None = None,
) -> AgentRunner:
    """Build the offline agent with isolated memory and execution scopes."""
    workspace_root = workspace_root or Path(tempfile.gettempdir()) / "research-agent-workspaces"
    memory = memory or InMemoryStore()
    sandbox = sandbox or LocalProcessSandbox()
    _scope(tenant_id, session_id)

    model = ScriptedModel([
        ModelResponse(tool_calls=(ToolCall("search-1", "search_documents", {"query": "memory RAG 区别"}),)),
        ModelResponse(content="长期 memory 保存用户事实与偏好；RAG 提供外部知识。[guides/05-memory.md]"),
    ])
    tools = ToolRegistry()
    tools.register(
        ToolDefinition("search_documents", "检索本地课程资料并返回来源", {"query": str}, search_documents)
    )
    tools.register(
        ToolDefinition(
            "execute_code",
            "通过租户和会话隔离的 sandbox 执行 Python 代码",
            {"source": str},
            lambda source: execute_code(
                source, tenant_id=tenant_id, session_id=session_id,
                workspace_root=workspace_root, sandbox=sandbox,
            ),
            requires_approval=True,
        )
    )
    return AgentRunner(model, tools)


def main() -> None:
    memory = InMemoryStore()
    scope = _scope("tenant-1", "research-1")
    memory.put(MemoryRecord(scope, "answer_style", "用户偏好简洁并保留引用"))
    preference = memory.search(scope, "简洁 引用")[0].value
    result = build_research_agent(memory=memory).run(
        f"解释 memory 和 RAG 的区别。回答偏好：{preference}", session_id="research-1"
    )
    print(result.output)
    print(f"sources={result.state.tool_results[0].output}")


if __name__ == "__main__":
    main()
