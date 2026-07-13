# 自定义类型并引入类型检查

## 学习目标

学完这一节，你可以：

- 像 Requests 的 `_types.py` 一样集中管理项目类型。
- 区分类型别名、`NewType`、`Literal` 和 `TypedDict`。
- 使用 mypy 在运行代码前发现参数类型错误。
- 判断什么时候需要额外的运行时数据校验。

## 1. `_t` 只是模块别名

Requests 在内部使用了类似下面的结构：

```python
from . import _types as _t

def prepare_url(url: _t.UriType, params: _t.ParamsType) -> None:
    ...
```

`_t` 不是 Python 的特殊语法，只是 `_types` 模块的简称。本教程采用同样的组织方式：

```text
custom_types.py       集中定义类型
custom_type_demo.py   导入并使用类型
custom_type_errors.py 故意包含错误，观察检查结果
```

在 [custom_types.py](custom_types.py) 中定义类型，在其他文件中导入：

```python
import custom_types as _t

def find_user(user_id: _t.UserId) -> str:
    ...
```

模块名前的下划线通常表示“项目内部使用”。你也可以把文件命名为 `_types.py`；本教程使用 `custom_types.py`，避免与标准库的 `types` 模块混淆。

## 2. 四种常见的自定义类型

### 类型别名

本仓库使用兼容较多类型检查器版本的 `TypeAlias`：

```python
from typing import TypeAlias

Url: TypeAlias = str
QueryValue: TypeAlias = str | int | float | bool | None
QueryParams: TypeAlias = dict[str, QueryValue]
```

Python 3.12+ 也可以使用更新的 `type Url = str` 语法。较旧版本的 mypy 可能无法解析这种新语法，因此学习项目中先使用 `TypeAlias`。

类型别名用于给复杂类型一个有业务含义的名字。`Url` 在运行时仍然是 `str`，因此类型检查器不会区分 `Url` 与普通字符串：

```python
url: Url = "hello"  # 静态检查可以通过，但它不是有效 URL
```

类型注解表达的是“值应是什么类型”，不保证字符串内容符合 URL 格式。

### `NewType`

当你希望类型检查器区分底层类型相同、业务含义不同的值时，使用 `NewType`：

```python
from typing import NewType

UserId = NewType("UserId", int)

def find_user(user_id: UserId) -> str:
    ...

find_user(UserId(42))  # 正确
find_user(42)          # mypy 报错
```

`NewType` 的运行时成本很小，但 Python 运行时仍不会自动校验数据。`UserId("42")` 也不会自动把字符串转换成整数。

### `Literal`

当参数只能从有限选项中选择时，使用 `Literal`：

```python
from typing import Literal, TypeAlias

HttpMethod: TypeAlias = Literal["GET", "POST", "PUT", "DELETE"]
```

这样，`"PATCH"` 会被类型检查器指出，而不是等到请求发出后才发现不支持。

### `TypedDict`

当函数接收具有固定字段的字典时，使用 `TypedDict`：

```python
from typing import TypedDict

class RequestOptions(TypedDict, total=False):
    timeout: float
    follow_redirects: bool
```

`total=False` 表示字段可以省略。类型检查器仍会检查字段名和字段值，例如把 `timeout` 写成字符串会被报告。

## 3. 安装并运行 mypy

仓库的 `requirements/dev.txt` 已经声明 mypy。安装开发依赖：

```bash
python -m pip install -r requirements/dev.txt
```

先运行正确示例：

```bash
python 01-type-system/custom_type_demo.py
```

然后检查它：

```bash
python -m mypy 01-type-system/custom_types.py \
  01-type-system/custom_type_demo.py
```

预期结果：

```text
Success: no issues found in 2 source files
```

最后检查故意写错的示例：

```bash
python -m mypy 01-type-system/custom_type_errors.py
```

mypy 应该指出三类问题：

- `"PATCH"` 不属于 `HttpMethod` 允许的值。
- `list[str]` 不能作为 `QueryParams` 的值。
- 普通 `int` 不能直接传给要求 `UserId` 的函数。

注意：运行 `custom_type_errors.py` 时，Python 本身可能不会阻止这些调用。mypy 是独立的静态检查步骤，通常放在编辑器、提交检查或 CI 中运行。

## 4. 静态检查与运行时校验不是一回事

Requests 的 `Url` 类型注解只能告诉检查器“这里应该传字符串或字节等允许的类型”。是否包含 `https://`，仍要靠 `prepare_url()` 中的运行时逻辑检查。

```text
代码输入
   |
   +-- mypy：检查声明的类型是否匹配，不执行代码
   |
   +-- Python：执行代码，由 prepare_url() 检查 URL 内容
```

如果输入来自用户、配置文件或网络，不能只依赖类型注解。你仍然需要：

- 用普通条件和 `raise` 编写运行时校验。
- 或使用 Pydantic 等数据验证工具解析外部输入。
- 在系统内部使用类型注解，让错误更早暴露在编辑器和 CI 中。

## 5. 练习

1. 给 `HttpMethod` 增加 `"PATCH"`，再次运行 mypy。
2. 给 `RequestOptions` 增加可选的 `headers: dict[str, str]`。
3. 新建 `OrderId = NewType("OrderId", int)`，验证 `find_user(OrderId(1))` 会被 mypy 拒绝。
4. 在 `build_request()` 中增加运行时 URL 校验：URL 不以 `http://` 或 `https://` 开头时抛出 `ValueError`。

完成第 4 题后，你就复现了 Requests 的核心设计：类型检查负责开发阶段的类型约束，运行时校验负责真实数据的内容约束。
