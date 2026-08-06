"""A hardened Docker-backed sandbox executor."""

from __future__ import annotations

import os
from pathlib import Path
import selectors
import subprocess
import tempfile
import time
import uuid
from typing import Mapping, Sequence

from .types import (
    ExecutionRequest,
    ExecutionResult,
    PredefinedCommand,
    PythonCode,
    SandboxPolicy,
    StopReason,
)

_CONTAINER_WORKSPACE = "/workspace"
_CONTAINER_USER = "65532:65532"


def build_docker_args(
    request: ExecutionRequest,
    policy: SandboxPolicy,
    workspace: Path,
    *,
    image: str,
    docker_binary: str = "docker",
    command_allowlist: Mapping[str, Sequence[str]] | None = None,
    allow_network: bool = False,
    container_name: str | None = None,
) -> list[str]:
    """Build deterministic Docker argv without invoking a shell."""
    if not image or image.startswith("-"):
        raise ValueError("image must not be empty or start with '-'")
    if policy.network == "allow" and not allow_network:
        raise ValueError("network access requires explicit DockerSandbox opt-in")

    command = _container_command(request, command_allowlist or {})
    args = [docker_binary, "run", "--rm"]
    if container_name is not None:
        args.append(f"--name={container_name}")
    if policy.network == "deny":
        args.append("--network=none")
    args.extend(
        [
            "--read-only",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            f"--user={_CONTAINER_USER}",
            "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=16m",
        ]
    )
    if policy.max_memory_bytes is not None:
        args.append(f"--memory={policy.max_memory_bytes}")
    if policy.max_cpu_seconds is not None:
        args.append("--cpus=1")
    if policy.max_processes is not None:
        args.append(f"--pids-limit={policy.max_processes}")
    args.extend(
        [
            f"--mount=type=bind,src={workspace},dst={_CONTAINER_WORKSPACE},readonly",
            f"--workdir={_CONTAINER_WORKSPACE}",
        ]
    )
    for name, value in sorted(policy.environment.items()):
        args.append(f"--env={name}={value}")
    args.extend(["--entrypoint=", image, *command])
    return args


def _container_command(
    request: ExecutionRequest, command_allowlist: Mapping[str, Sequence[str]]
) -> list[str]:
    if isinstance(request, PredefinedCommand):
        executable = command_allowlist.get(request.name)
        if not executable:
            raise ValueError("command is not allowlisted")
        return [*executable, *request.arguments]
    if isinstance(request, PythonCode):
        if any(Path(path).as_posix() == "program.py" for path in request.files):
            raise ValueError("declared file path must not resolve to program.py")
        return ["python", "program.py"]
    raise TypeError("request must be a supported sandbox request")


class DockerSandbox:
    """Run sandbox requests in an isolated Docker container."""

    def __init__(
        self,
        image: str,
        docker_binary: str = "docker",
        command_allowlist: Mapping[str, Sequence[str]] | None = None,
        *,
        allow_network: bool = False,
    ) -> None:
        if not image or image.startswith("-"):
            raise ValueError("image must not be empty or start with '-'")
        if not docker_binary:
            raise ValueError("docker_binary must not be empty")
        self._image = image
        self._docker_binary = docker_binary
        self._command_allowlist = {
            name: tuple(command)
            for name, command in (command_allowlist or {}).items()
        }
        self._allow_network = allow_network

    def run(self, request: ExecutionRequest, policy: SandboxPolicy) -> ExecutionResult:
        started = time.monotonic()
        summary = self._policy_summary(policy)
        if policy.network == "allow" and not self._allow_network:
            return ExecutionResult(
                "", "network access requires explicit DockerSandbox opt-in", None,
                StopReason.POLICY_DENIED, time.monotonic() - started, summary,
            )

        policy.workspace.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=policy.workspace, prefix="docker-sandbox-") as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir(mode=0o777)
            workspace.chmod(0o777)
            container_name = f"python-sandbox-{uuid.uuid4().hex}"
            try:
                self._prepare_request(request, workspace)
                args = build_docker_args(
                    request,
                    policy,
                    workspace,
                    image=self._image,
                    docker_binary=self._docker_binary,
                    command_allowlist=self._command_allowlist,
                    allow_network=self._allow_network,
                    container_name=container_name,
                )
            except ValueError as error:
                return ExecutionResult(
                    "", str(error), None, StopReason.POLICY_DENIED,
                    time.monotonic() - started, summary,
                )

            try:
                process = subprocess.Popen(
                    args,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=False,
                    env=self._client_environment(),
                )
                stdout, stderr, reason = self._collect(process, policy, container_name)
                returncode = None if reason in {StopReason.TIMEOUT, StopReason.OUTPUT_LIMIT} else process.returncode
                if reason is None:
                    reason = StopReason.COMPLETED if returncode == 0 else StopReason.FAILED
            except OSError as error:
                return ExecutionResult("", str(error), None, StopReason.FAILED,
                                       time.monotonic() - started, summary)
            finally:
                self._remove_container(container_name)

        stdout, stderr, _ = self._truncate_output(
            bytes(stdout), bytes(stderr), policy.max_output_bytes
        )
        return ExecutionResult(
            stdout.decode("utf-8", "replace"),
            stderr.decode("utf-8", "replace"),
            returncode,
            reason,
            time.monotonic() - started,
            summary,
        )

    @staticmethod
    def _prepare_request(request: ExecutionRequest, workspace: Path) -> None:
        if not isinstance(request, PythonCode):
            return
        if "program.py" in request.files:
            raise ValueError("declared file path must not be program.py")
        DockerSandbox._write_file(workspace, "program.py", request.source.encode("utf-8"))
        for relative_path, content in request.files.items():
            DockerSandbox._write_file(workspace, relative_path, content)
        # The non-root container user needs read access but not host-side ownership.
        for path in workspace.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)

    @staticmethod
    def _write_file(workspace: Path, relative_path: str, content: bytes) -> None:
        destination = workspace / relative_path
        root = workspace.resolve()
        if not destination.parent.resolve().is_relative_to(root):
            raise ValueError("declared file path escapes sandbox workspace")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.is_symlink():
            raise ValueError("declared file path must not be a symbolic link")
        destination.write_bytes(content)

    def _collect(
        self,
        process: subprocess.Popen[bytes],
        policy: SandboxPolicy,
        container_name: str,
    ) -> tuple[bytes, bytes, StopReason | None]:
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
                available = policy.max_output_bytes - sum(len(value) for value in buffers.values())
                if len(chunk) > available:
                    buffers[key.data].extend(chunk[:available])
                    reason = StopReason.OUTPUT_LIMIT
                    break
                buffers[key.data].extend(chunk)
            if reason is not None:
                break
        selector.close()
        if reason is not None:
            self._remove_container(container_name)
            self._terminate_client(process)
        else:
            process.wait()
        return bytes(buffers["stdout"]), bytes(buffers["stderr"]), reason

    @staticmethod
    def _terminate_client(process: subprocess.Popen[bytes]) -> None:
        try:
            process.kill()
        except (AttributeError, ProcessLookupError):
            pass
        try:
            process.wait(timeout=2)
        except (AttributeError, ProcessLookupError, subprocess.TimeoutExpired):
            pass

    def _remove_container(self, container_name: str) -> None:
        try:
            subprocess.run(
                [self._docker_binary, "rm", "-f", container_name],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=2, shell=False, check=False, env=self._client_environment(),
            )
        except (OSError, subprocess.SubprocessError):
            pass

    @staticmethod
    def _client_environment() -> dict[str, str]:
        allowed = ("PATH", "DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_CONFIG")
        return {name: os.environ[name] for name in allowed if name in os.environ}

    @staticmethod
    def _truncate_output(stdout: bytes, stderr: bytes, maximum: int) -> tuple[bytes, bytes, bool]:
        truncated = len(stdout) + len(stderr) > maximum
        if len(stdout) >= maximum:
            return stdout[:maximum], b"", truncated
        return stdout, stderr[: maximum - len(stdout)], truncated

    def _policy_summary(self, policy: SandboxPolicy) -> dict[str, object]:
        return {
            "executor": "docker",
            "image": self._image,
            "network": policy.network,
            "network_enforced": policy.network == "deny",
            "read_only_root": True,
            "non_root_user": True,
            "capabilities_dropped": "ALL",
            "no_new_privileges": True,
            "workspace_mount_only": True,
            "limits": {
                "memory_bytes": policy.max_memory_bytes,
                "cpu_quota": 1 if policy.max_cpu_seconds is not None else None,
                "cpu_seconds": "not enforced as Docker cumulative CPU time; cpus is a quota",
                "processes": policy.max_processes,
                "timeout_seconds": policy.timeout_seconds,
                "output_bytes": policy.max_output_bytes,
            },
        }
