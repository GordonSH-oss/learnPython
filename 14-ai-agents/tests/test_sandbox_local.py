from __future__ import annotations

import os
from pathlib import Path
import signal
import sys
import time

import pytest

from agent_core import (
    PredefinedCommand,
    PythonCode,
    SandboxPolicy,
    StopReason,
)
from agent_core.sandbox import local
from agent_core.sandbox.local import LocalProcessSandbox


ALLOWLIST = {
    "python": (sys.executable,),
}


def policy(workspace: Path, **kwargs: object) -> SandboxPolicy:
    return SandboxPolicy(workspace=workspace, **kwargs)


def test_runs_allowlisted_command(tmp_path: Path):
    result = LocalProcessSandbox(ALLOWLIST).run(
        PredefinedCommand("python", ("-c", "print('allowed')")),
        policy(tmp_path),
    )

    assert result.stdout == "allowed\n"
    assert result.stderr == ""
    assert result.returncode == 0
    assert result.reason is StopReason.COMPLETED


def test_denies_command_not_in_allowlist(tmp_path: Path):
    result = LocalProcessSandbox(ALLOWLIST).run(
        PredefinedCommand("not-approved"), policy(tmp_path)
    )

    assert result.reason is StopReason.POLICY_DENIED
    assert result.returncode is None


def test_runs_python_code_in_private_workspace(tmp_path: Path):
    result = LocalProcessSandbox().run(PythonCode("print('python code')"), policy(tmp_path))

    assert result.stdout == "python code\n"
    assert result.reason is StopReason.COMPLETED


def test_writes_declared_input_files(tmp_path: Path):
    result = LocalProcessSandbox().run(
        PythonCode("from pathlib import Path\nprint(Path('inputs/data.txt').read_bytes().decode())", {"inputs/data.txt": b"payload"}),
        policy(tmp_path),
    )

    assert result.stdout == "payload\n"
    assert result.reason is StopReason.COMPLETED


def test_declared_input_files_are_read_only(tmp_path: Path):
    source = (
        "from pathlib import Path\n"
        "path = Path('inputs/data.txt')\n"
        "try:\n"
        "    path.write_bytes(b'tampered')\n"
        "except OSError:\n"
        "    print('write-failed')\n"
        "print(path.read_bytes().decode())\n"
    )
    result = LocalProcessSandbox().run(
        PythonCode(source, {"inputs/data.txt": b"payload"}), policy(tmp_path)
    )

    assert result.reason is StopReason.COMPLETED
    if os.name == "nt":
        assert result.stdout in {"payload\n", "write-failed\ntampered\n"}
    else:
        assert result.stdout == "write-failed\npayload\n"


def test_does_not_inherit_host_secrets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HOST_ONLY_SECRET", "must-not-reach-child")

    result = LocalProcessSandbox().run(
        PythonCode("import os\nprint(os.getenv('HOST_ONLY_SECRET', 'missing'))"),
        policy(tmp_path),
    )

    assert result.stdout == "missing\n"


def test_uses_only_dedicated_workspace(tmp_path: Path):
    result = LocalProcessSandbox().run(
        PythonCode("from pathlib import Path\nprint(Path.cwd())"),
        policy(tmp_path),
    )

    workspace = Path(result.stdout.strip())
    assert workspace.is_relative_to(tmp_path)
    assert workspace != tmp_path
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("name", ["../escape", "/absolute/path"])
def test_rejects_invalid_input_paths_at_contract_boundary(name: str):
    with pytest.raises(ValueError):
        PythonCode("pass", {name: b"blocked"})


def test_preserves_nonzero_exit_code(tmp_path: Path):
    result = LocalProcessSandbox().run(PythonCode("raise SystemExit(7)"), policy(tmp_path))

    assert result.returncode == 7
    assert result.reason is StopReason.FAILED


def test_times_out_and_terminates_process_group(tmp_path: Path):
    result = LocalProcessSandbox().run(
        PythonCode("import time\ntime.sleep(10)"),
        policy(tmp_path, timeout_seconds=0.1),
    )

    assert result.reason is StopReason.TIMEOUT
    assert result.returncode is not None


def test_stops_at_output_limit(tmp_path: Path):
    result = LocalProcessSandbox().run(
        PythonCode("print('x' * 10000)"),
        policy(tmp_path, max_output_bytes=128),
    )

    assert result.reason is StopReason.OUTPUT_LIMIT
    assert len((result.stdout + result.stderr).encode()) <= 128


@pytest.mark.skipif(os.name == "nt", reason="requires Unix process groups")
def test_timeout_cleans_up_child_process(tmp_path: Path):
    marker = tmp_path / "child-survived"
    source = (
        "import pathlib, subprocess, sys, time\n"
        f"marker = {str(marker)!r}\n"
        "subprocess.Popen([sys.executable, '-c', "
        "'import pathlib, time; time.sleep(.4); pathlib.Path(' + repr(marker) + ').write_text(\\\"alive\\\")'])\n"
        "time.sleep(10)\n"
    )

    result = LocalProcessSandbox().run(
        PythonCode(source), policy(tmp_path, timeout_seconds=0.1, max_processes=None)
    )
    time.sleep(0.6)

    assert result.reason is StopReason.TIMEOUT
    assert not marker.exists()


@pytest.mark.skipif(sys.platform == "win32", reason="resource limits require Unix")
def test_cpu_limit_is_reported_and_enforced_when_available(tmp_path: Path):
    result = LocalProcessSandbox().run(
        PythonCode("while True: pass"),
        policy(tmp_path, timeout_seconds=5, max_cpu_seconds=1),
    )

    if result.policy_summary["enforced_limits"].get("cpu"):
        assert result.reason is StopReason.RESOURCE_LIMIT
    else:
        pytest.skip("RLIMIT_CPU unavailable on this platform")


@pytest.mark.skipif(sys.platform == "win32", reason="signal return codes require Unix")
def test_sigkill_is_reported_as_failure_even_when_cpu_limit_is_enforced(tmp_path: Path):
    result = LocalProcessSandbox().run(
        PythonCode("import os, signal\nos.kill(os.getpid(), signal.SIGKILL)"),
        policy(tmp_path, max_cpu_seconds=1),
    )

    if result.policy_summary["enforced_limits"].get("cpu"):
        assert result.returncode == -signal.SIGKILL
        assert result.reason is StopReason.FAILED
    else:
        pytest.skip("RLIMIT_CPU unavailable on this platform")




def test_setrlimit_failure_is_reported_as_not_enforced(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    if os.name == "nt" or local.resource is None:
        pytest.skip("requires Unix resource limits")
    def fail(*_args):
        raise OSError("blocked")
    monkeypatch.setattr(local.resource, "setrlimit", fail)
    result = LocalProcessSandbox().run(PythonCode("pass"), policy(tmp_path, max_cpu_seconds=1))
    assert result.policy_summary["enforced_limits"]["cpu"] is False
    assert "cpu" in result.policy_summary["unsupported_enforcement"]


def test_windows_termination_uses_taskkill_tree(monkeypatch: pytest.MonkeyPatch):
    calls = []
    monkeypatch.setattr(local.os, "name", "nt")
    monkeypatch.setattr(local.subprocess, "run", lambda *args, **kwargs: calls.append((args, kwargs)))
    process = type("Process", (), {"pid": 42, "wait": lambda self: None})()
    LocalProcessSandbox._terminate_group(process)
    assert calls[0][0][0] == ["taskkill", "/PID", "42", "/T", "/F"]
    assert calls[0][1]["shell"] is False


def test_policy_summary_does_not_claim_local_network_denial_is_enforced(tmp_path: Path):
    result = LocalProcessSandbox().run(PythonCode("pass"), policy(tmp_path))

    assert result.policy_summary["network"] == "deny"
    assert result.policy_summary["network_enforced"] is False
