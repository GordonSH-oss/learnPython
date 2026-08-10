# 第三方库：工程与质量

## `pytest`

- [ ] 我知道 pytest 的发现规则、断言、fixture 和参数化。
- [ ] 我会使用 `pytest.raises`、`monkeypatch`、`tmp_path`、`caplog` 和 `@pytest.mark.parametrize`。

安装：`python -m pip install pytest`（仓库基线 `pytest>=8.0`）。

```python
import pytest

@pytest.mark.parametrize("value, expected", [(2, 4), (3, 9)])
def test_square(value: int, expected: int) -> None:
    assert value * value == expected

def test_error() -> None:
    with pytest.raises(ValueError):
        raise ValueError("bad input")
```

常见坑：fixture 作用域会影响状态隔离；参数化数据应覆盖边界；不要为了绿色测试把真实行为全部 mock 掉。

自查：fixture 的 `scope` 如何影响生命周期？如何测试日志、临时文件和异常？

练习：为一个 JSON 解析函数添加正常、缺字段、无效 JSON 和空输入测试。

仓库关联：[工具与测试](../06-tools-and-tests/README.md)、[PyTorch 测试](../07-deep-learning/pytorch/tests/)。

## `mypy`

- [ ] 我知道静态类型检查与运行时校验不是同一件事。
- [ ] 我会使用 `mypy path/to/file.py`、`Optional`/联合类型、泛型和 `Protocol`。

安装：`python -m pip install mypy`（仓库基线 `mypy>=1.10`）。

```python
def total(values: list[int]) -> int:
    return sum(values)

# mypy 会报告：str 不能作为 list[int] 的元素。
values: list[int] = [1, "2"]  # type: ignore[assignment]
```

常见坑：`# type: ignore` 应尽量带错误码并说明原因；第三方包没有类型信息时可能需要 stub；类型通过不代表业务逻辑正确。

自查：`Any` 为什么会让错误消失？`Protocol` 如何支持结构化类型检查？

练习：为一个仓库中的函数补齐参数和返回值类型，运行 mypy 并修复至少三个真实问题。

仓库关联：[类型系统](../01-type-system/README.md)。

