"""
Python 错误报出和处理教程

运行方式：
    python 03-python-basics/error_handling.py

学习目标：
    1. 理解错误如何被 raise 抛出。
    2. 理解 try / except / else / finally 的执行顺序。
    3. 学会定义业务异常，并携带错误码等业务信息。
    4. 学会保留错误上下文，避免把真正的问题吞掉。
"""

from __future__ import annotations

import sys
from pathlib import Path


# 本目录里有 copy.py 教学文件。直接运行本文件时，脚本目录会排在 sys.path
# 前面，可能遮蔽标准库 copy，并影响 traceback 等标准库模块的导入。
# 这个教程不依赖同目录模块，所以先移除脚本目录，避免导入标准库时被干扰。
SCRIPT_DIR = Path(__file__).resolve().parent
if sys.path and Path(sys.path[0]).resolve() == SCRIPT_DIR:
    sys.path.pop(0)

import traceback


LINE = "=" * 72


def title(text: str) -> None:
    print(f"\n{LINE}\n{text}\n{LINE}")


class BusinessError(Exception):
    """业务异常基类：用 code 表示可识别的业务错误类型。"""

    def __init__(self, message: str, code: int = 1000) -> None:
        self.message = message
        self.code = code
        super().__init__(message)

    def __str__(self) -> str:
        return f"[code={self.code}] {self.message}"


class AuthError(BusinessError):
    """认证相关错误。"""

    def __init__(self, message: str) -> None:
        super().__init__(message, code=2001)


class PaymentError(BusinessError):
    """支付相关错误。"""

    def __init__(self, message: str) -> None:
        super().__init__(message, code=3001)


def lesson_1_error_propagation() -> None:
    title("1. 错误会沿调用栈向上冒泡")

    def parse_age(raw_age: str) -> int:
        return int(raw_age)

    def create_user(raw_age: str) -> dict[str, int]:
        age = parse_age(raw_age)
        return {"age": age}

    try:
        create_user("not-a-number")
    except ValueError as error:
        print("捕获到 ValueError:", error)
        print(
            """
说明：
  - int("not-a-number") 会抛出 ValueError。
  - parse_age() 没有处理它，错误会继续传给 create_user()。
  - create_user() 也没有处理，最终被外层 try / except 捕获。
"""
        )


def lesson_2_try_except_else_finally() -> None:
    title("2. try / except / else / finally 的执行顺序")

    def divide(left: int, right: int) -> float:
        return left / right

    for right in [2, 0]:
        print(f"\n尝试计算 10 / {right}")
        try:
            result = divide(10, right)
        except ZeroDivisionError as error:
            print("except: 除数不能为 0:", error)
        else:
            print("else: 没有异常时执行，结果是:", result)
        finally:
            print("finally: 无论是否出错都会执行，常用于释放资源")

    print(
        """
规则：
  - try：放可能出错的代码。
  - except：处理指定类型的错误。
  - else：try 没有出错时执行。
  - finally：不管是否出错都执行。
"""
    )


def lesson_3_raise_business_error() -> None:
    title("3. 主动 raise：把业务失败变成可处理的异常")

    def require_login(token: str | None) -> str:
        if token is None:
            raise AuthError("登录已过期，请重新登录")
        return token

    def pay(balance: int, amount: int) -> str:
        if amount <= 0:
            raise PaymentError("支付金额必须大于 0")
        if balance < amount:
            raise PaymentError("余额不足")
        return "支付成功"

    for action in [
        lambda: require_login(None),
        lambda: pay(balance=10, amount=99),
        lambda: pay(balance=100, amount=20),
    ]:
        try:
            print("执行结果:", action())
        except BusinessError as error:
            print("业务错误:", error)
            print("错误码:", error.code)

    print(
        """
说明：
  - raise 用来主动报错。
  - 自定义异常可以携带 code、message、detail 等业务信息。
  - 外层可以统一捕获 BusinessError，再根据 code 做不同处理。
"""
    )


def lesson_4_except_order() -> None:
    title("4. except 顺序：先写具体错误，再写通用错误")

    def load_config(name: str) -> dict[str, str]:
        if not name:
            raise ValueError("配置名不能为空")
        if name == "missing":
            raise FileNotFoundError("配置文件不存在")
        return {"name": name}

    for name in ["", "missing", "prod"]:
        try:
            print(f"\n读取配置: {name!r}")
            print(load_config(name))
        except FileNotFoundError as error:
            print("文件错误:", error)
        except ValueError as error:
            print("参数错误:", error)
        except Exception as error:
            print("兜底错误:", error)

    print(
        """
规则：
  - except 会从上到下匹配，匹配到一个后就不会继续往下匹配。
  - 具体异常要放在前面。
  - Exception 这种兜底捕获要放最后，并且不要无声吞掉。
"""
    )


def lesson_5_exception_chaining() -> None:
    title("5. raise from：保留底层错误原因")

    def parse_user_id(raw_user_id: str) -> int:
        try:
            return int(raw_user_id)
        except ValueError as error:
            raise BusinessError("用户 ID 格式错误", code=4001) from error

    try:
        parse_user_id("abc")
    except BusinessError as error:
        print("对外展示的业务错误:", error)
        print("\n完整 traceback 会同时显示业务错误和底层 ValueError:")
        traceback.print_exception(type(error), error, error.__traceback__, limit=6, file=sys.stdout)

    print(
        """
说明：
  - raise NewError(...) from old_error 可以建立错误因果链。
  - 对用户或调用方展示业务错误。
  - 对日志和排查保留底层技术错误。
"""
    )


def lesson_6_bad_and_good_patterns() -> None:
    title("6. 常见坏写法和推荐写法")

    print(
        """
坏写法 1：裸 except，会捕获太多东西，排查困难。

    try:
        risky_code()
    except:
        pass

坏写法 2：捕获 Exception 后什么都不做，真实错误被吞掉。

    try:
        risky_code()
    except Exception:
        return None

推荐写法：

    try:
        risky_code()
    except SpecificError as error:
        log(error)
        recover()

原则：
  - 能处理才捕获，不能处理就让错误继续抛出。
  - 捕获尽量具体的异常类型。
  - 需要转换异常时，用 raise from 保留原因。
  - 资源清理放 finally，或优先使用 with 上下文管理器。
"""
    )


def main() -> None:
    lesson_1_error_propagation()
    lesson_2_try_except_else_finally()
    lesson_3_raise_business_error()
    lesson_4_except_order()
    lesson_5_exception_chaining()
    lesson_6_bad_and_good_patterns()


if __name__ == "__main__":
    main()
