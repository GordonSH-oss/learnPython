# 标准库：函数式与迭代

## `itertools`

- [ ] 我知道它提供惰性、可组合的迭代器构件。
- [ ] 我会使用 `chain`、`islice`、`count`、`cycle`、`repeat`、`groupby`、`product`。

```python
from itertools import chain, islice, product

values = chain([1, 2], [3, 4])
print(list(islice(values, 3)))
print(list(product(["S", "M"], ["red", "blue"])))
```

常见坑：迭代器通常只能消费一次；`groupby` 只合并相邻键，通常需要先排序；无限迭代器必须配合终止条件。

自查：`chain` 与列表相加在内存行为上有何不同？为什么 `groupby` 前常常要排序？

练习：不生成完整列表，取偶数序列的前 10 项，并生成颜色和尺寸的笛卡尔积。

仓库关联：[标准库组合示例](../03-python-basics/standard_library_tour.py)、[生成器课程](../03-python-basics/generator-comprehension/COMPREHENSIONS_VS_GENERATORS.md)。

## `functools`

- [ ] 我知道它用于函数包装、缓存、偏函数和归约。
- [ ] 我会使用 `wraps`、`lru_cache`、`cached_property`、`partial`、`reduce`、`singledispatch`。

```python
from functools import lru_cache, partial

@lru_cache(maxsize=128)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

base_two = partial(int, base=2)
print(fib(20), base_two("1010"))
```

常见坑：缓存参数必须可哈希；无界缓存可能持续占用内存；装饰器不使用 `wraps` 会丢失原函数元数据。

自查：缓存有副作用或依赖外部状态的函数会怎样？`partial` 与闭包各适合什么场景？

练习：为一个纯函数添加缓存并打印 `cache_info()`，再实现保留元数据的计时装饰器。

仓库关联：[装饰器示例](../03-python-basics/decorators.py)、[单分派](../03-python-basics/SINGLEDISPATCH.md)。

## `operator`

- [ ] 我知道它把运算符和属性访问表示为可传递的函数。
- [ ] 我会使用 `itemgetter`、`attrgetter`、`methodcaller` 和常见算术函数。

```python
from operator import attrgetter, itemgetter

rows = [{"name": "Ada", "score": 90}, {"name": "Lin", "score": 95}]
print(sorted(rows, key=itemgetter("score"), reverse=True))

class User:
    def __init__(self, name: str) -> None:
        self.name = name

print(sorted([User("Lin"), User("Ada")], key=attrgetter("name"))[0].name)
```

常见坑：getter 引用的键或属性不存在时会抛异常；简单 lambda 往往更容易表达复杂转换，不必强行使用 `operator`。

自查：`itemgetter(1)` 和 `lambda x: x[1]` 有什么共同点？何时 `attrgetter("a.b")` 更清晰？

练习：分别按字典的两个字段和对象的嵌套属性排序。

仓库关联：扩展主题，可结合 [特殊方法课程](../03-python-basics/special-methods/README.md) 理解运算符协议。

