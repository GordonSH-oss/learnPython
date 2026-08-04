from __future__ import annotations

import os
from pathlib import Path
import shutil
import selectors
import subprocess
import sys
import time

import pytest

from agent_core import DockerSandbox, PredefinedCommand, PythonCode, SandboxPolicy, StopReason
from agent_core.sandbox.docker import build_docker_args


IMAGE = "python:3.12-alpine"
ALLOWLIST = {"python": ("python",)}


def policy(workspace: Path, **kwargs: object) -> SandboxPolicy:
    return SandboxPolicy(workspace=workspace, **kwargs)


def test_build_docker_args_applies_isolation_and_resource_limits(tmp_path: Path):
    workspace = tmp_path / "sandbox-workspace"
    request = PythonCode("print('ok')")
    sandbox_policy = policy(
        tmp_path,
        max_memory_bytes=123456789,
        max_cpu_seconds=3,
        max_processes=7,
    )

    args = build_docker_args(request, sandbox_policy, workspace, image=IMAGE)

    assert args[:2] == ["docker", "run"]
    assert "--network=none" in args
    assert "--read-only" in args
    assert "--cap-drop=ALL" in args
    assert "--security-opt=no-new-privileges" in args
    assert "--user=65532:65532" in args
    assert "--memory=123456789" in args
    assert "--cpus=1" in args
    assert "--pids-limit=7" in args
    assert f"--mount=type=bind,src={workspace},dst=/workspace" in args
    assert "--workdir=/workspace" in args
    assert args[-4:] == ["--entrypoint=", IMAGE, "python", "program.py"]
    joined = " ".join(args)
    assert "/var/run/docker.sock" not in joined
    assert str(Path.cwd()) not in joined
    assert "HOME=" not in joined


def test_build_docker_args_is_deterministic_and_passes_only_policy_environment(tmp_path: Path):
    workspace = tmp_path / "workspace"
    request = PythonCode("pass")
    sandbox_policy = policy(tmp_path, environment={"SAFE_VALUE": "yes"})

    first = build_docker_args(request, sandbox_policy, workspace, image=IMAGE)
    second = build_docker_args(request, sandbox_policy, workspace, image=IMAGE)

    assert first == second
    assert "--env=SAFE_VALUE=yes" in first


def test_build_docker_args_allows_network_only_with_explicit_opt_in(tmp_path: Path):
    sandbox_policy = policy(tmp_path, network="allow")

    with pytest.raises(ValueError, match="network access"):
        build_docker_args(PythonCode("pass"), sandbox_policy, tmp_path / "work", image=IMAGE)

    args = build_docker_args(
        PythonCode("pass"), sandbox_policy, tmp_path / "work", image=IMAGE,
        allow_network=True,
    )
    assert "--network=none" not in args


def test_predefined_command_requires_allowlist(tmp_path: Path):
    result = DockerSandbox(IMAGE).run(
        PredefinedCommand("python", ("--version",)), policy(tmp_path)
    )

    assert result.reason is StopReason.POLICY_DENIED
    assert result.returncode is None
    assert "allowlist" in result.stderr


def test_predefined_command_uses_only_allowlisted_executable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    captured: list[list[str]] = []

    def fake_collect(self: DockerSandbox, process: object, sandbox_policy: SandboxPolicy, cidfile: Path):
        return b"ok\n", b"", None

    class FakeProcess:
        returncode = 0
        stdout = object()
        stderr = object()

    def fake_popen(args: list[str], **kwargs: object) -> FakeProcess:
        captured.append(args)
        return FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(DockerSandbox, "_collect", fake_collect)
    result = DockerSandbox(IMAGE, command_allowlist=ALLOWLIST).run(
        PredefinedCommand("python", ("--version",)), policy(tmp_path)
    )

    assert result.reason is StopReason.COMPLETED
    assert captured[0][-4:] == ["--entrypoint=", IMAGE, "python", "--version"]


def test_python_code_writes_program_and_declared_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    observed: dict[str, bytes] = {}

    class FakeProcess:
        returncode = 0
        stdout = object()
        stderr = object()

    def fake_popen(args: list[str], **kwargs: object) -> FakeProcess:
        mount = next(arg for arg in args if arg.startswith("--mount="))
        source = Path(mount.split("src=", 1)[1].split(",dst=", 1)[0])
        observed["workspace_mode"] = oct(source.stat().st_mode & 0o777).encode()
        observed["program.py"] = (source / "program.py").read_bytes()
        observed["inputs/data.txt"] = (source / "inputs/data.txt").read_bytes()
        return FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(DockerSandbox, "_collect", lambda self, process, sandbox_policy, cidfile: (b"done\n", b"", None))
    result = DockerSandbox(IMAGE).run(
        PythonCode("print('done')", {"inputs/data.txt": b"payload"}), policy(tmp_path)
    )

    assert observed == {
        "workspace_mode": b"0o777",
        "program.py": b"print('done')",
        "inputs/data.txt": b"payload",
    }
    assert result.stdout == "done\n"


def test_timeout_kills_container_by_cid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    calls: list[list[str]] = []

    class FakeStream:
        def fileno(self) -> int:
            return 10

    class FakeProcess:
        stdout = FakeStream()
        stderr = FakeStream()
        returncode = None

        def kill(self) -> None:
            self.returncode = -9

        def wait(self, timeout: float | None = None) -> int:
            return self.returncode or 0

    def fake_popen(args: list[str], **kwargs: object) -> FakeProcess:
        cidfile = Path(next(arg for arg in args if arg.startswith("--cidfile=")).split("=", 1)[1])
        cidfile.write_text("container-id\n")
        return FakeProcess()

    def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(selectors, "DefaultSelector", lambda: type("Selector", (), {
        "register": lambda self, *args: None,
        "get_map": lambda self: {1: 1},
        "select": lambda self, timeout: [],
        "close": lambda self: None,
    })())
    monkeypatch.setattr(time, "monotonic", iter((0.0, 0.0, 1.0, 1.0)).__next__)
    result = DockerSandbox(IMAGE).run(PythonCode("pass"), policy(tmp_path, timeout_seconds=0.1))

    assert result.reason is StopReason.TIMEOUT
    assert ["docker", "kill", "container-id"] in calls


def test_output_is_bounded_and_reported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    class FakeStream:
        def fileno(self) -> int:
            return 10

    class FakeProcess:
        stdout = FakeStream()
        stderr = FakeStream()
        returncode = None

        def wait(self, timeout: float | None = None) -> int:
            self.returncode = 0
            return 0

    class FakeSelector:
        def __init__(self) -> None:
            self._registered: dict[object, str] = {}

        def register(self, stream: object, _event: int, name: str) -> None:
            self._registered[stream] = name

        def unregister(self, stream: object) -> None:
            self._registered.pop(stream)

        def get_map(self) -> dict[object, str]:
            return self._registered

        def select(self, _timeout: float) -> list[tuple[object, int]]:
            stream, name = next(iter(self._registered.items()))
            return [(type("Key", (), {"fileobj": stream, "data": name})(), selectors.EVENT_READ)]

        def close(self) -> None:
            pass

    process = FakeProcess()
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(selectors, "DefaultSelector", FakeSelector)
    monkeypatch.setattr(os, "read", lambda fd, size: b"x" * size)

    result = DockerSandbox(IMAGE).run(PythonCode("pass"), policy(tmp_path, max_output_bytes=32))

    assert result.reason is StopReason.OUTPUT_LIMIT
    assert len((result.stdout + result.stderr).encode()) <= 32


def test_policy_summary_records_image_and_restrictions_without_secrets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        subprocess, "run",
        lambda args, **kwargs: subprocess.CompletedProcess(args, 0, b"", b""),
    )
    result = DockerSandbox(IMAGE).run(
        PythonCode("pass"), policy(tmp_path, environment={"API_TOKEN": "secret-value"})
    )

    assert result.policy_summary["image"] == IMAGE
    assert result.policy_summary["network"] == "deny"
    assert result.policy_summary["read_only_root"] is True
    assert result.policy_summary["non_root_user"] is True
    assert "secret-value" not in repr(dict(result.policy_summary))


def _docker_available() -> tuple[bool, str]:
    docker = shutil.which("docker")
    if docker is None:
        return False, "docker CLI is not installed"
    try:
        subprocess.run(
            [docker, "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=2, check=True, shell=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False, "docker daemon is unavailable"
    try:
        image = subprocess.run(
            [docker, "image", "inspect", IMAGE], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, timeout=2, check=False, shell=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False, "docker image inspection failed"
    if image.returncode != 0:
        return False, f"local image {IMAGE} is unavailable; integration tests do not pull"
    return True, ""


DOCKER_AVAILABLE, DOCKER_SKIP_REASON = _docker_available()
docker_integration = pytest.mark.skipif(not DOCKER_AVAILABLE, reason=DOCKER_SKIP_REASON)


@docker_integration
def test_integration_is_non_root_denies_network_and_has_read_only_root(tmp_path: Path):
    source = (
        "import os, socket\n"
        "print('uid', os.getuid())\n"
        "try:\n socket.create_connection(('1.1.1.1', 53), timeout=.2); print('network allowed')\n"
        "except OSError:\n print('network denied')\n"
        "try:\n open('/root-write', 'w').write('x'); print('root writable')\n"
        "except OSError:\n print('root readonly')\n"
    )
    result = DockerSandbox(IMAGE).run(PythonCode(source), policy(tmp_path))

    assert result.reason is StopReason.COMPLETED
    assert "uid 0" not in result.stdout
    assert "network denied" in result.stdout
    assert "root readonly" in result.stdout


@docker_integration
def test_integration_hides_host_secret_and_accesses_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HOST_ONLY_SECRET", "must-not-reach-container")
    source = (
        "import os\nfrom pathlib import Path\n"
        "print(os.getenv('HOST_ONLY_SECRET', 'missing'))\n"
        "print(Path('inputs/data.txt').read_text())\n"
    )
    result = DockerSandbox(IMAGE).run(
        PythonCode(source, {"inputs/data.txt": b"payload"}), policy(tmp_path)
    )

    assert result.stdout == "missing\npayload\n"


@docker_integration
def test_integration_timeout_cleans_container(tmp_path: Path):
    started = time.monotonic()
    result = DockerSandbox(IMAGE).run(
        PythonCode("import time\ntime.sleep(10)"), policy(tmp_path, timeout_seconds=0.3)
    )

    assert result.reason is StopReason.TIMEOUT
    assert time.monotonic() - started < 5


@docker_integration
def test_integration_process_limit_is_enforced(tmp_path: Path):
    source = (
        "import subprocess, sys\n"
        "children=[]\n"
        "try:\n"
        " while True: children.append(subprocess.Popen([sys.executable, '-c', 'pass']))\n"
        "except OSError:\n print('limited')\n"
        "finally:\n"
        " for child in children: child.wait()\n"
    )
    result = DockerSandbox(IMAGE).run(
        PythonCode(source), policy(tmp_path, max_processes=4, timeout_seconds=3)
    )

    assert result.reason is StopReason.COMPLETED
    assert "limited" in result.stdout
