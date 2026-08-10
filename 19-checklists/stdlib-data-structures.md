# 标准库：基础与数据结构

## `collections`

- [ ] 我知道它为常见容器模式提供专用数据结构。
- [ ] 我会导入并使用 `Counter`、`defaultdict`、`deque`、`namedtuple`、`ChainMap`。

常用 API：`Counter.most_common()`、`defaultdict(factory)`、`deque.appendleft()`、`deque.popleft()`、`deque(maxlen=n)`。

```python
from collections import Counter, defaultdict, deque

counts = Counter("banana")
groups = defaultdict(list)
for name, team in [("Ada", "A"), ("Lin", "B"), ("Bob", "A")]:
    groups[team].append(name)

recent = deque(["a", "b"], maxlen=3)
recent.extend(["c", "d"])
print(counts.most_common(2), dict(groups), list(recent))
```

常见坑：`defaultdict` 的工厂必须可调用；`deque` 适合两端操作，但不适合频繁随机索引；`Counter` 对不存在的键返回 `0`。

自查：为什么队列通常用 `deque` 而不是 `list.pop(0)`？`Counter` 的减法为什么可能丢弃零值和负值？

练习：统计一段文本中出现最多的 3 个单词，并用长度为 5 的 `deque` 保存最近处理的单词。

仓库关联：[标准库组合示例](../03-python-basics/standard_library_tour.py)。

## `enum`

- [ ] 我知道枚举用于表达有限且有名称的状态集合。
- [ ] 我会使用 `Enum`、`IntEnum`、`auto()`，并区分成员名称和值。

```python
from enum import Enum, auto

class Status(Enum):
    PENDING = auto()
    RUNNING = auto()
    DONE = auto()

status = Status.RUNNING
print(status.name, status.value, status is Status.RUNNING)
```

常见坑：普通 `Enum` 成员不等于其原始值；不要用字符串散落表达业务状态；持久化枚举时要明确保存名称还是值。

自查：`Enum` 与一组模块常量相比有什么优势？何时需要 `IntEnum`？

练习：为订单定义状态枚举，并写一个只允许 `PENDING -> PAID -> SHIPPED` 的状态转换函数。

仓库关联：扩展主题，当前仓库没有独立枚举课程。

## `dataclasses`

- [ ] 我知道数据类会生成初始化、表示和比较等样板方法。
- [ ] 我会使用 `@dataclass`、`field()`、`default_factory`、`frozen=True`。

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class User:
    name: str
    tags: tuple[str, ...] = field(default_factory=tuple)

print(User("Ada", ("admin",)))
```

常见坑：可变默认值必须使用 `default_factory`；`frozen=True` 是浅层不可变；类型注解不会自动执行运行时校验。

自查：数据类与普通类的边界是什么？为什么 `tags: list[str] = []` 不合法？

练习：定义一个带创建时间和项目列表的 `Task`，确保不同实例不共享项目列表。

仓库关联：[数据类示例](../03-python-basics/data_class.py)。

## `typing`

- [ ] 我知道类型注解主要服务于静态分析、IDE 和接口设计。
- [ ] 我会使用联合类型、`TypeVar`、`Generic`、`Protocol`、`TypedDict`、`Callable`。

```python
from typing import Protocol, TypeVar

T = TypeVar("T")

class SupportsClose(Protocol):
    def close(self) -> None: ...

def first(items: list[T]) -> T:
    if not items:
        raise ValueError("items must not be empty")
    return items[0]
```

常见坑：注解默认不会阻止错误值进入运行时；`Any` 会传播并削弱检查；容器的可变性会影响泛型协变与不变性。

自查：`Protocol` 和继承 ABC 有什么区别？`Any` 与 `object` 有什么区别？

练习：为“可发送消息”的对象定义协议，并让两个没有共同父类的类通过类型检查。

仓库关联：[类型系统学习路线](../01-type-system/README.md)、[鸭子类型](../03-python-basics/DUCK_TYPING.md)。

## `copy`

- [ ] 我能区分赋值、浅拷贝和深拷贝。
- [ ] 我会使用 `copy.copy()` 和 `copy.deepcopy()`，并知道何时应避免深拷贝。

```python
import copy

original = {"items": [{"id": 1}]}
shallow = copy.copy(original)
deep = copy.deepcopy(original)
original["items"][0]["id"] = 9
print(shallow["items"][0]["id"], deep["items"][0]["id"])
```

常见坑：浅拷贝仍共享嵌套对象；深拷贝可能昂贵，也可能复制不应复制的资源；项目文件命名为 `copy.py` 会遮蔽标准库模块。

自查：切片复制列表属于哪类拷贝？为什么数据库连接不适合深拷贝？

练习：构造一个含嵌套列表的配置，分别用赋值、浅拷贝和深拷贝修改并预测结果。

仓库关联：[拷贝示例](../03-python-basics/copy.py)。

