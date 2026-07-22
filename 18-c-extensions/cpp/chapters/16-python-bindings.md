# 16 使用 C++ 扩展 Python

## 学习目标

- 理解 C++ binding 与 Python/C API 的关系
- 使用 pybind11 建立最小模块的心智模型
- 设计异常、所有权、GIL 和 buffer 边界
- 判断何时使用 pybind11、nanobind、Cython 或 C ABI

## pybind11 的位置

pybind11 是 header-only C++ binding 库，使用模板生成 Python/C API 胶水：

```text
C++ 函数/类
   ↓ pybind11 模板
Python/C API 调用
   ↓ 编译
Python 扩展模块
```

最小示例：

```cpp
#include <pybind11/pybind11.h>

int add(int left, int right) { return left + right; }

PYBIND11_MODULE(example, module) {
    module.def("add", &add);
}
```

pybind11 不是 Python 或 C++ 标准库，需要单独安装并加入构建系统。本教程不把外部依赖作为默认构建的一部分。

## 自动转换的成本

pybind11 可以把 Python list 转为 `std::vector`，但通常意味着逐元素转换和复制。高性能数组应使用 buffer protocol、NumPy 支持或明确 view 类型。

方便转换不等于零成本。用第 `using-c` 教程的边界模型分析：参数检查、复制、C++ 计算和返回对象分别占多少。

## 所有权策略

绑定返回裸指针或引用时必须指定 Python 对象能否比 C++ owner 活得更久。pybind11 return value policy、keep_alive 和智能指针 holder 都是在表达所有权图。

默认使用值返回或 `unique_ptr` 所有权转移。shared_ptr 只有在 C++ 模型本身确实共享所有权时使用。

## 异常

pybind11 会把常见 C++ 异常转换为 Python 异常，也支持注册自定义异常。仍不能让异常逃出模块初始化或 C ABI 边界，析构函数也不应抛异常。

## GIL

C++ 函数从 Python 调用时持有 GIL。纯 C++ 长计算可使用 call guard 或显式释放，但无 GIL 时不能操作 Python 对象，输入 view 的并发安全也必须证明。

## 工具选择

| 场景 | 常见选择 |
| --- | --- |
| 已有 C ABI | ctypes/cffi |
| 手写最细 CPython 控制 | Python/C API |
| C++ 类库绑定 | pybind11/nanobind |
| 渐进加速 Python 算法 | Cython |
| 稳定跨语言核心 | C ABI 外层 + 各语言包装 |

## 生产检查

- wheel 覆盖 Python、OS 和 CPU 矩阵
- 不把编译器私有 C++ ABI 暴露给其他工具链
- 所有权 policy 有测试
- 异常映射与纯 Python API 一致
- GIL release 区域不访问 Python
- 大数组避免隐式复制
- sanitizer 和 debug Python 验证通过

## 动手练习

1. 在虚拟环境安装 pybind11，构建最小 add 模块。
2. 绑定一个 Rule-of-Zero C++ 类。
3. 比较 `std::vector<double>` 自动转换与 buffer/NumPy view 的成本。
4. 故意返回局部对象引用，解释为什么 binding policy 无法修复已失效对象。

