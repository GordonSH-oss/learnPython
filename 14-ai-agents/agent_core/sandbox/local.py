"""A bounded local-process executor for trusted development use."""

from __future__ import annotations

import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tempfile
import time
import json
from typing import Mapping, Sequence

try:
    import resource
except ImportError:  # pragma: no cover - platform dependent
    resource = None  # type: ignore[assignment]

from .types import ExecutionRequest, ExecutionResult, PredefinedCommand, PythonCode, SandboxPolicy, StopReason


class LocalProcessSandbox:
    """Run approved commands or Python snippets in a temporary child workspace.

    This is not a strong security boundary: local network denial and host-level
    isolation cannot be guaranteed by this implementation.
    """

    def __init__(self, command_allowlist: Mapping[str, Sequence[str]] | None = None) -> None:
        self._command_allowlist = {name: tuple(command) for name, command in (command_allowlist or {}).items()}

    def run(self, request: ExecutionRequest, policy: SandboxPolicy) -> ExecutionResult:
        started = time.monotonic()
        policy.workspace.mkdir(parents=True, exist_ok=True)
        enforced, unsupported = self._limit_support(policy)
        summary = self._policy_summary(policy, enforced, unsupported)
        with tempfile.TemporaryDirectory(dir=policy.workspace, prefix="sandbox-") as directory:
            workspace = Path(directory)
            command = self._command_for(request, workspace)
            if command is None:
                return ExecutionResult("", "command is not allowlisted", None, StopReason.POLICY_DENIED,
                                       time.monotonic() - started, summary)
            child_error_read, child_error_write = os.pipe() if os.name != "nt" else (None, None)
            try:
                process = subprocess.Popen(
                    command, cwd=workspace, env=self._environment(policy), stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False,
                    start_new_session=True,
                    pass_fds=(child_error_write,) if child_error_write is not None else (),
                    preexec_fn=self._preexec(policy, child_error_write) if child_error_write is not None else None,
                )
            finally:
                if child_error_write is not None:
                    os.close(child_error_write)
            child_errors = self._read_child_errors(child_error_read)
            if child_error_read is not None:
                os.close(child_error_read)
            if child_errors:
                failed = set(child_errors)
                enforced = {name: active and name not in failed for name, active in enforced.items()}
                unsupported = [*unsupported, *[name for name in child_errors if name not in unsupported]]
                summary = self._policy_summary(policy, enforced, unsupported)
            stdout, stderr, reason = self._collect(process, policy)
        if reason is None:
            reason = StopReason.COMPLETED if process.returncode == 0 else StopReason.FAILED
            if process.returncode is not None and process.returncode < 0 and enforced:
                reason = StopReason.RESOURCE_LIMIT
        return ExecutionResult(stdout, stderr, process.returncode, reason, time.monotonic() - started, summary)

    def _command_for(self, request: ExecutionRequest, workspace: Path) -> list[str] | None:
        if isinstance(request, PredefinedCommand):
            executable = self._command_allowlist.get(request.name)
            return [*executable, *request.arguments] if executable else None
        if not isinstance(request, PythonCode):
            raise TypeError("request must be a supported sandbox request")
        self._write_file(workspace, "program.py", request.source.encode("utf-8"))
        for relative_path, content in request.files.items():
            self._write_file(workspace, relative_path, content)
        return [sys.executable, "program.py"]

    @staticmethod
    def _write_file(workspace: Path, relative_path: str, content: bytes) -> None:
        destination = workspace.joinpath(relative_path)
        root = workspace.resolve()
        if not destination.parent.resolve().is_relative_to(root):
            raise ValueError("declared file path escapes sandbox workspace")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.is_symlink():
            raise ValueError("declared file path must not be a symbolic link")
        destination.write_bytes(content)

    @staticmethod
    def _environment(policy: SandboxPolicy) -> dict[str, str]:
        environment = {"PATH": os.defpath, "PYTHONIOENCODING": "utf-8"}
        environment.update(policy.environment)
        return environment

    @staticmethod
    def _collect(process: subprocess.Popen[bytes], policy: SandboxPolicy) -> tuple[str, str, StopReason | None]:
        assert process.stdout is not None and process.stderr is not None
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        buffers = {"stdout": bytearray(), "stderr": bytearray()}
        deadline = time.monotonic() + policy.timeout_seconds
        reason: StopReason | None = None
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                reason = StopReason.TIMEOUT
                break
            for key, _ in selector.select(remaining):
                chunk = os.read(key.fileobj.fileno(), 8192)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                buffers[key.data].extend(chunk)
                if sum(len(value) for value in buffers.values()) > policy.max_output_bytes:
                    reason = StopReason.OUTPUT_LIMIT
                    break
            if reason is not None:
                break
        selector.close()
        if reason is not None:
            LocalProcessSandbox._terminate_group(process)
        else:
            process.wait()
        stdout, stderr = LocalProcessSandbox._truncate_output(bytes(buffers["stdout"]), bytes(buffers["stderr"]), policy.max_output_bytes)
        return stdout.decode("utf-8", "replace"), stderr.decode("utf-8", "replace"), reason

    @staticmethod
    def _read_child_errors(fd: int | None) -> list[str]:
        if fd is None:
            return []
        data = bytearray()
        while True:
            chunk = os.read(fd, 4096)
            if not chunk:
                break
            data.extend(chunk)
        if not data:
            return []
        try:
            value = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return ["unknown"]
        return [str(name) for name in value] if isinstance(value, list) else ["unknown"]

    @staticmethod
    def _terminate_group(process: subprocess.Popen[bytes]) -> None:
        if os.name == "nt":
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    shell=False, check=False,
                )
            except OSError:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (AttributeError, ProcessLookupError, PermissionError):
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
        try:
            process.wait()
        except ProcessLookupError:
            pass

    @staticmethod
    def _truncate_output(stdout: bytes, stderr: bytes, maximum: int) -> tuple[bytes, bytes]:
        if len(stdout) >= maximum:
            return stdout[:maximum], b""
        return stdout, stderr[: maximum - len(stdout)]

    @staticmethod
    def _limit_support(policy: SandboxPolicy) -> tuple[dict[str, bool], list[str]]:
        requests = {"cpu": policy.max_cpu_seconds, "memory": policy.max_memory_bytes,
                    "open_files": 64, "processes": policy.max_processes}
        constants = {"cpu": "RLIMIT_CPU", "memory": "RLIMIT_AS", "open_files": "RLIMIT_NOFILE", "processes": "RLIMIT_NPROC"}
        enforced = {name: resource is not None and hasattr(resource, constants[name]) and value is not None
                    for name, value in requests.items()}
        unsupported = [name for name, active in enforced.items() if not active and requests[name] is not None]
        return enforced, unsupported

    @staticmethod
    def _preexec(policy: SandboxPolicy, error_fd: int):
        enforced, _ = LocalProcessSandbox._limit_support(policy)

        def apply_limits() -> None:
            assert resource is not None
            limits = {"cpu": ("RLIMIT_CPU", policy.max_cpu_seconds), "memory": ("RLIMIT_AS", policy.max_memory_bytes),
                      "open_files": ("RLIMIT_NOFILE", 64), "processes": ("RLIMIT_NPROC", policy.max_processes)}
            failed = []
            for name, (constant, value) in limits.items():
                if enforced[name]:
                    try:
                        resource.setrlimit(getattr(resource, constant), (value, value))
                    except (OSError, ValueError):
                        failed.append(name)
            if failed:
                os.write(error_fd, json.dumps(failed).encode("utf-8"))
            os.set_inheritable(error_fd, False)
            os.close(error_fd)
        return apply_limits

    @staticmethod
    def _policy_summary(policy: SandboxPolicy, enforced: Mapping[str, bool], unsupported: list[str]) -> dict[str, object]:
        return {"executor": "local_process", "network": policy.network, "network_enforced": False,
                "enforced_limits": dict(enforced), "unsupported_enforcement": unsupported,
                "timeout_seconds": policy.timeout_seconds, "max_output_bytes": policy.max_output_bytes}
