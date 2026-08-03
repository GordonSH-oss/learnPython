"""Public contracts for sandbox execution."""

from dataclasses import dataclass, field
from enum import Enum
import math
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Mapping, Protocol, TypeAlias, runtime_checkable


class _FrozenJSONMapping(dict[str, object]):
    """An immutable dict that remains serializable by the standard JSON encoder."""

    def __setitem__(self, key: str, value: object) -> None:
        raise TypeError("mapping is immutable")

    def __delitem__(self, key: str) -> None:
        raise TypeError("mapping is immutable")

    def clear(self) -> None:
        raise TypeError("mapping is immutable")

    def pop(self, key: str, default: object = None) -> object:
        raise TypeError("mapping is immutable")

    def popitem(self) -> tuple[str, object]:
        raise TypeError("mapping is immutable")

    def setdefault(self, key: str, default: object = None) -> object:
        raise TypeError("mapping is immutable")

    def update(self, *args: object, **kwargs: object) -> None:
        raise TypeError("mapping is immutable")

    def __ior__(self, other: object) -> _FrozenJSONMapping:
        raise TypeError("mapping is immutable")


def _freeze_json_value(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("policy_summary must contain JSON-compatible values")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, nested_value in value.items():
            if not isinstance(key, str):
                raise TypeError("policy_summary keys must be strings")
            frozen[key] = _freeze_json_value(nested_value)
        return _FrozenJSONMapping(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json_value(item) for item in value)
    raise TypeError("policy_summary must contain JSON-compatible values")


class StopReason(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    OUTPUT_LIMIT = "output_limit"
    RESOURCE_LIMIT = "resource_limit"
    POLICY_DENIED = "policy_denied"


@dataclass(frozen=True)
class PredefinedCommand:
    name: str
    arguments: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("name must be a string")
        if not self.name:
            raise ValueError("name must not be empty")
        if not isinstance(self.arguments, (tuple, list)):
            raise TypeError("arguments must be a sequence of strings")
        if any(not isinstance(argument, str) for argument in self.arguments):
            raise TypeError("arguments must contain only strings")
        object.__setattr__(self, "arguments", tuple(self.arguments))


@dataclass(frozen=True)
class PythonCode:
    source: str
    files: Mapping[str, bytes] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.source, str):
            raise TypeError("source must be a string")
        if not isinstance(self.files, Mapping):
            raise TypeError("files must be a mapping")
        for path, content in self.files.items():
            if not isinstance(path, str):
                raise TypeError("file paths must be strings")
            if not path or Path(path).is_absolute() or ".." in Path(path).parts:
                raise ValueError("file paths must be relative and stay within the workspace")
            if not isinstance(content, bytes):
                raise TypeError("file contents must be bytes")
        object.__setattr__(self, "files", MappingProxyType(dict(self.files)))


ExecutionRequest: TypeAlias = PredefinedCommand | PythonCode


@dataclass(frozen=True)
class SandboxPolicy:
    workspace: Path
    timeout_seconds: float = 5
    max_output_bytes: int = 65536
    max_memory_bytes: int | None = 268435456
    max_cpu_seconds: int | None = 2
    max_processes: int | None = 16
    network: Literal["deny", "allow"] = "deny"
    environment: Mapping[str, str] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_output_bytes <= 0:
            raise ValueError("max_output_bytes must be positive")
        for name, value in (
            ("max_memory_bytes", self.max_memory_bytes),
            ("max_cpu_seconds", self.max_cpu_seconds),
            ("max_processes", self.max_processes),
        ):
            if value is not None and value <= 0:
                raise ValueError(f"{name} must be positive when set")
        if self.network not in ("deny", "allow"):
            raise ValueError("network must be 'deny' or 'allow'")
        if not isinstance(self.environment, Mapping):
            raise TypeError("environment must be a mapping")
        for name, value in self.environment.items():
            if not isinstance(name, str) or not isinstance(value, str):
                raise TypeError("environment must contain only string keys and values")
        object.__setattr__(self, "environment", MappingProxyType(dict(self.environment)))


@dataclass(frozen=True)
class ExecutionResult:
    stdout: str
    stderr: str
    returncode: int | None
    reason: StopReason
    duration_seconds: float
    policy_summary: Mapping[str, object] = field(repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.duration_seconds, (int, float)) or isinstance(self.duration_seconds, bool):
            raise TypeError("duration_seconds must be a finite non-negative number")
        if not math.isfinite(self.duration_seconds) or self.duration_seconds < 0:
            raise ValueError("duration_seconds must be a finite non-negative number")
        if not isinstance(self.policy_summary, Mapping):
            raise TypeError("policy_summary must be a mapping")
        summary = _freeze_json_value(self.policy_summary)
        assert isinstance(summary, _FrozenJSONMapping)
        object.__setattr__(self, "policy_summary", summary)


@runtime_checkable
class Sandbox(Protocol):
    def run(self, request: ExecutionRequest, policy: SandboxPolicy) -> ExecutionResult:
        ...
