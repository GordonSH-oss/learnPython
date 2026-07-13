# Python 类型系统

学习 Python 的类型注解、泛型、类型检查等高级特性。

## 核心概念

### 1. 类型注解基础
- **文件**: `learn_typing.py`
- **内容**: Python 3.9+ 的现代类型注解写法
- **要点**: `list[int]`, `dict[str, int]`, `int | None`

### 2. 前向引用 (Forward Reference)
- **文件**: `forward_reference_example.py`, `FORWARD_REFERENCE.md`
- **内容**: 解决类型注解中的循环依赖问题
- **要点**: 使用字符串引用尚未定义的类型

### 3. 自定义类型与静态检查
- **文件**: `CUSTOM_TYPES_AND_CHECKING.md`, `custom_types.py`, `custom_type_demo.py`, `custom_type_errors.py`
- **内容**: 仿照 Requests 的 `_types as _t` 组织方式，自定义并集中管理类型
- **要点**: `type`、`NewType`、`Literal`、`TypedDict`、mypy，以及静态检查与运行时校验的区别

### 4. 运行时 vs 类型检查
- **文件**: `runtime_vs_type_checking.py`, `RUNTIME_VS_TYPE_CHECKING.md`
- **内容**: TYPE_CHECKING 的使用场景
- **要点**: 避免运行时导入开销，仅用于类型检查

### 5. 泛型 (Generics)
- **文件**: `generic_invariance_explanation.py`
- **内容**: 泛型不变性、协变、逆变
- **要点**: `List[Animal]` 和 `List[Dog]` 的关系

### 6. TypeVar
- **文件**: `typevar_bound_explanation.py`, `typevar_usage_scenarios.py`
- **内容**: 类型变量的边界和使用场景
- **要点**: 泛型函数和类的类型参数

### 7. 其他
- `instantiation_demo.py` - 类实例化演示
- `type_annotation_usefulness.py` - 类型注解的实际用途
- `advanced_typing.py` - `Protocol`、`TypedDict`、`Literal`、`overload` 等工程常用高级类型

## 学习顺序建议

1. `learn_typing.py` - 基础语法
2. `type_annotation_usefulness.py` - 理解为什么需要类型注解
3. `CUSTOM_TYPES_AND_CHECKING.md` - 自定义类型并使用 mypy
4. `forward_reference_example.py` - 前向引用
5. `runtime_vs_type_checking.py` - 运行时优化
6. `generic_invariance_explanation.py` - 泛型
7. `typevar_bound_explanation.py` - TypeVar 基础
8. `typevar_usage_scenarios.py` - TypeVar 高级用法
9. `advanced_typing.py` - 工程常用高级类型

## 工具推荐

- **mypy**: 静态类型检查器
  ```bash
  pip install mypy
  mypy your_file.py
  ```

- **pyright**: 微软的类型检查器
  ```bash
  pip install pyright
  pyright your_file.py
  ```
