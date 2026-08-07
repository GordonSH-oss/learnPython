from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.path.insert(0, str(Path(__file__).parents[2] / "examples"))

from agent_core import (  # noqa: E402
    InMemoryStore,
    LocalProcessSandbox,
    MemoryRecord,
    PredefinedCommand,
    PythonCode,
    SandboxPolicy,
    StopReason,
    ToolCall,
)
from examples.research_agent import _scope, build_research_agent, execute_code  # noqa: E402


ALLOWLIST = {"python": (sys.executable,)}


def test_tenant_and_session_workspace_scopes_do_not_cross(tmp_path: Path):
    sandbox = LocalProcessSandbox()
    first = json.loads(execute_code(
        "from pathlib import Path\nprint(Path.cwd())",
        tenant_id="tenant-a", session_id="session-1", workspace_root=tmp_path, sandbox=sandbox,
    ))
    second = json.loads(execute_code(
        "from pathlib import Path\nprint(Path.cwd())",
        tenant_id="tenant-b", session_id="session-1", workspace_root=tmp_path, sandbox=sandbox,
    ))
    third = json.loads(execute_code(
        "from pathlib import Path\nprint(Path.cwd())",
        tenant_id="tenant-a", session_id="session-2", workspace_root=tmp_path, sandbox=sandbox,
    ))

    assert first["scope"] == "tenant-a:session-1"
    assert second["scope"] == "tenant-b:session-1"
    assert third["scope"] == "tenant-a:session-2"
    assert len({first["stdout"], second["stdout"], third["stdout"]}) == 3
    assert Path(first["stdout"].strip()).is_relative_to(tmp_path / "tenant-a" / "session-1")


def test_memory_isolation_matches_tenant_and_session_scope():
    memory = InMemoryStore()
    memory.put(MemoryRecord("tenant-a:session-1", "fact", "alpha secret"))
    memory.put(MemoryRecord("tenant-b:session-1", "fact", "beta secret"))

    assert [record.value for record in memory.search("tenant-a:session-1", "alpha")] == ["alpha secret"]
    assert memory.search("tenant-a:session-1", "beta") == []
    assert memory.search("tenant-a:session-2", "alpha") == []


def test_generated_code_cannot_read_host_secret(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CAPSTONE_HOST_SECRET", "must-not-reach-child")
    result = json.loads(execute_code(
        "import os\nprint(os.getenv('CAPSTONE_HOST_SECRET', 'missing'))",
        tenant_id="tenant-a", session_id="session-1", workspace_root=tmp_path,
        sandbox=LocalProcessSandbox(),
    ))

    assert result["reason"] == StopReason.COMPLETED.value
    assert result["stdout"] == "missing\n"
    assert "must-not-reach-child" not in json.dumps(result)


def test_predefined_command_allowlist_denies_unapproved_command(tmp_path: Path):
    result = LocalProcessSandbox(ALLOWLIST).run(
        PredefinedCommand("sh", ("-c", "echo should-not-run")), SandboxPolicy(tmp_path)
    )
    assert result.reason is StopReason.POLICY_DENIED
    assert result.returncode is None
    assert "should-not-run" not in result.stdout


@pytest.mark.parametrize("path", ["../escape.txt", "/tmp/escape.txt", "nested/../../escape.txt"])
def test_traversal_is_denied_at_typed_request_boundary(path: str):
    with pytest.raises(ValueError):
        PythonCode("pass", {path: b"blocked"})


def test_timeout_and_output_limit_are_deterministic(tmp_path: Path):
    timeout = LocalProcessSandbox().run(
        PythonCode("import time\ntime.sleep(10)"),
        SandboxPolicy(tmp_path, timeout_seconds=0.05),
    )
    output = LocalProcessSandbox().run(
        PythonCode("print('x' * 10000)"),
        SandboxPolicy(tmp_path, max_output_bytes=64),
    )

    assert timeout.reason is StopReason.TIMEOUT
    assert output.reason is StopReason.OUTPUT_LIMIT
    assert len((output.stdout + output.stderr).encode()) <= 64


def test_execute_code_requires_typed_scope_identifiers(tmp_path: Path):
    invalid_pairs = (
        ("../other", "s"),
        ("..", "s"),
        ("tenant:a", "s"),
        ("a", "session:b"),
    )
    for tenant_id, session_id in invalid_pairs:
        with pytest.raises(ValueError):
            execute_code(
                "pass", tenant_id=tenant_id, session_id=session_id,
                workspace_root=tmp_path, sandbox=LocalProcessSandbox(),
            )


def test_scope_encoding_cannot_collide_across_identifier_pairs():
    assert _scope("tenant-a", "session") != _scope("tenant", "a-session")


def test_research_agent_wires_approval_policy(tmp_path: Path):
    approvals = []
    runner = build_research_agent(
        workspace_root=tmp_path,
        approve=lambda call: approvals.append(call.name) or True,
    )

    result = runner.tools.execute(
        ToolCall("code-1", "execute_code", {"source": "print('approved')"}),
        runner.approve,
    )

    assert result.ok
    assert approvals == ["execute_code"]
    assert json.loads(result.output)["stdout"] == "approved\n"
