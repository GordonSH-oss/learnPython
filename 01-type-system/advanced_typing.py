"""Advanced typing examples used by modern Python projects.

Run:
    python 01-type-system/advanced_typing.py
"""

from __future__ import annotations

from typing import Literal, Protocol, TypedDict, overload


class UserPayload(TypedDict):
    id: int
    name: str
    role: Literal["admin", "member"]


class JsonWriter(Protocol):
    def write_json(self, payload: UserPayload) -> str:
        ...


class SimpleWriter:
    def write_json(self, payload: UserPayload) -> str:
        return f"{payload['id']}:{payload['name']}:{payload['role']}"


@overload
def normalize_id(value: int) -> int:
    ...


@overload
def normalize_id(value: str) -> int:
    ...


def normalize_id(value: int | str) -> int:
    return int(value)


def export_user(writer: JsonWriter, payload: UserPayload) -> str:
    return writer.write_json(payload)


def main() -> None:
    payload: UserPayload = {"id": normalize_id("42"), "name": "Alice", "role": "admin"}
    print(export_user(SimpleWriter(), payload))


if __name__ == "__main__":
    main()
