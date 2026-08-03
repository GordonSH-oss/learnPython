from pathlib import Path
from typing import get_args, get_origin, Literal

import pytest

from agent_core import (
    ExecutionRequest,
    ExecutionResult,
    PredefinedCommand,
    PythonCode,
    Sandbox,
    SandboxPolicy,
    StopReason,
)


def test_request_dataclasses_normalize_and_preserve_inputs():
    command = PredefinedCommand("pytest", ["-q"])
    code = PythonCode("print('ok')", {"input.txt": b"data"})

    assert command.arguments == ("-q",)
    assert code.files == {"input.txt": b"data"}
    assert isinstance(command, ExecutionRequest)
    assert isinstance(code, ExecutionRequest)


def test_request_dataclasses_reject_invalid_command_name_and_arguments():
    with pytest.raises(ValueError):
        PredefinedCommand("")
    with pytest.raises(TypeError):
        PredefinedCommand("pytest", ["-q", 1])
    with pytest.raises(TypeError):
        PredefinedCommand(1)


def test_python_code_rejects_invalid_source_and_files():
    with pytest.raises(TypeError):
        PythonCode(1)
    with pytest.raises(ValueError):
        PythonCode("print('ok')", {"": b"data"})
    with pytest.raises(ValueError):
        PythonCode("print('ok')", {"../secret": b"data"})
    with pytest.raises(ValueError):
        PythonCode("print('ok')", {"/tmp/file": b"data"})
    with pytest.raises(TypeError):
        PythonCode("print('ok')", {"input.txt": "data"})
    with pytest.raises(TypeError):
        PythonCode("print('ok')", {1: b"data"})
def test_policy_is_frozen_and_validates_positive_limits(tmp_path: Path):
    policy = SandboxPolicy(tmp_path)

    assert policy.workspace == tmp_path
    assert policy.timeout_seconds == 5
    assert policy.max_output_bytes == 65536
    assert policy.network == "deny"
    with pytest.raises((AttributeError, TypeError)):
        policy.timeout_seconds = 1
    with pytest.raises(ValueError):
        SandboxPolicy(tmp_path, timeout_seconds=0)
    with pytest.raises(ValueError):
        SandboxPolicy(tmp_path, max_output_bytes=0)


def test_stop_reasons_are_stable_strings():
    assert {reason.value for reason in StopReason} == {
        "completed", "failed", "timeout", "output_limit", "resource_limit", "policy_denied",
    }


def test_execution_result_holds_policy_summary(tmp_path: Path):
    result = ExecutionResult("out", "err", 0, StopReason.COMPLETED, 0.25, {"network": "deny"})

    assert result.stdout == "out"
    assert result.returncode == 0
    assert result.reason is StopReason.COMPLETED
    assert result.policy_summary == {"network": "deny"}


def test_sandbox_is_runtime_checkable_protocol():
    class SandboxImplementation:
        def run(self, request: ExecutionRequest, policy: SandboxPolicy) -> ExecutionResult:
            raise NotImplementedError

    assert isinstance(SandboxImplementation(), Sandbox)
    assert issubclass(SandboxImplementation, Sandbox)


def test_public_exports_are_available_from_agent_core():
    import agent_core

    for name in (
        "PredefinedCommand", "PythonCode", "ExecutionRequest", "SandboxPolicy",
        "ExecutionResult", "StopReason", "Sandbox",
    ):
        assert name in agent_core.__all__
        assert hasattr(agent_core, name)


def test_network_type_exposes_supported_literals():
    assert get_args(Literal["deny", "allow"]) == ("deny", "allow")
