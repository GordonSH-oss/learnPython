"""项目内部共享的类型定义。

其他模块可以使用 ``from custom_types import UserId``，也可以像 Requests
一样使用 ``import custom_types as _t`` 来集中访问这些类型。
"""

from typing import Literal, NewType, TypeAlias, TypedDict


# TypeAlias 创建类型别名。它只影响静态类型检查，不创建新的运行时类型。
# Python 3.12+ 也可以写成：type Url = str
Url: TypeAlias = str
QueryValue: TypeAlias = str | int | float | bool | None
QueryParams: TypeAlias = dict[str, QueryValue]

# NewType 让类型检查器区分 UserId 和普通 int，适合防止参数传错。
UserId = NewType("UserId", int)

HttpMethod: TypeAlias = Literal["GET", "POST", "PUT", "DELETE"]


class RequestOptions(TypedDict, total=False):
    """描述一个具有固定字段结构的字典。"""

    timeout: float
    follow_redirects: bool
