"""Read application settings from environment variables.

Run:
    python 00-environment/config_example.py
"""

from __future__ import annotations

from dataclasses import dataclass
import os


def _read_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _read_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    app_env: str
    app_port: int
    database_url: str
    debug: bool

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "dev"),
            app_port=_read_int("APP_PORT", 8000),
            database_url=os.getenv("DATABASE_URL", "sqlite:///app.db"),
            debug=_read_bool("DEBUG", False),
        )


def main() -> None:
    settings = Settings.from_env()
    print(settings)


if __name__ == "__main__":
    main()
