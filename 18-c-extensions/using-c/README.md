# 用 C 接口扩展并加速 Python

这套教程面向已经掌握 Python，并学过 C 指针、数组、结构体、动态内存和共享库的开发者。目标不是简单地把 Python 代码翻译成 C，而是学会识别性能热点、设计稳定边界、验证结果，再选择成本合适的接口。

如果 C 基础还不牢固，先学习 [C 语言系统教程](../c-language/README.md)，至少完成第 01 至 12 章和第 18 章共享库。

## 学完以后你能做什么

- 使用 `ctypes` 调用已有 C 动态库，并正确声明参数、返回值和数组指针。
- 使用 Python/C API 编写可以 `import` 的原生扩展模块。
- 理解 Python 对象到 C 值的转换、异常协议和引用所有权。
- 使用 Cython 渐进式地给 Python 热点添加静态类型。
- 使用 buffer protocol 在 Python 与 C 之间借用连续内存，避免逐元素复制。
- 判断何时可以释放 GIL，并为共享 C 状态设计同步策略。
- 使用 debug、sanitizer、wheel 和多平台 CI 交付原生扩展。
- 设计避免频繁跨语言调用和重复复制的数据接口。
- 先验证正确性，再用可重复基准判断优化是否真实有效。

## 三条技术路径

| 路径 | 适用场景 | 优点 | 主要代价 |
| --- | --- | --- | --- |
| `ctypes` | 已有稳定的 C ABI，快速集成系统库 | Python 标准库自带，不写扩展胶水 | 类型声明靠人工维护，调用与转换有成本 |
| Python/C API | 需要原生 Python 模块、对象或精细控制 | 能直接使用 Python 对象模型和异常系统 | 代码量大，引用计数和版本兼容要求高 |
| Cython | 已有 Python 算法需要渐进加速 | 语法接近 Python，类型化循环较直接 | 增加构建依赖，仍需理解生成代码和边界成本 |

选择原则：已有 C 库先考虑 `ctypes`；需要长期发布的原生模块考虑 Python/C API；主要目标是加速现有 Python 数值循环时优先评估 Cython。NumPy 已经提供所需向量化操作时，通常先使用 NumPy，而不是自己维护 C 扩展。

## 环境准备

本目录已在 Apple Silicon Mac 上使用 Python 3.14 和 Apple Clang 验证。先检查工具：

```bash
python3 --version
python3-config --includes
clang --version
```

如果没有 Command Line Tools：

```bash
xcode-select --install
```

核心的 `ctypes` 和 Python/C API 示例不依赖 `setuptools`。运行：

```bash
cd 18-c-extensions/using-c
make all
make test
make benchmark
```

Cython 是可选部分，建议在虚拟环境安装：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools cython
make cython
```

## 学习路线

| 顺序 | 教程 | 核心问题 | 配套文件 |
| --- | --- | --- | --- |
| 1 | [选择 C 接口](chapters/01-choosing-an-interface.md) | C 什么时候会加速 Python，应选哪条路径？ | `benchmark.py` |
| 2 | [`ctypes` 调用 C ABI](chapters/02-ctypes.md) | Python 如何安全调用动态库？ | `arithmetic.h`、`arithmetic.c`、`ctypes_demo.py` |
| 3 | [Python/C API 扩展](chapters/03-python-c-api.md) | 原生模块如何解析参数、报告异常并返回对象？ | `mymath_module.c`、`c_extension_demo.py` |
| 4 | [Buffer protocol 与零拷贝](chapters/04-buffer-protocol.md) | 如何借用连续数据而不逐元素复制？ | `ctypes_demo.py`、`mymath_module.c` |
| 5 | [GIL、线程与并发](chapters/05-gil-and-concurrency.md) | 何时能释放 GIL，C 状态由谁同步？ | `mymath_module.c` |
| 6 | [正确测量和优化](chapters/06-performance.md) | 怎样证明加速正确、稳定且值得维护？ | `benchmark.py`、`test_using_c.py` |
| 7 | [Cython 渐进加速](chapters/07-cython.md) | 如何通过类型化逐步移除 Python 热点开销？ | `cython_example.pyx`、`setup_cython.py` |
| 8 | [调试、构建与发布](chapters/08-debugging-and-packaging.md) | 如何调试崩溃并交付跨平台 wheel？ | `Makefile`、构建配置 |

完成接口教程后，再阅读 [CPython 源码阅读指南](CPYTHON_SOURCE_GUIDE.md)。源码阅读与扩展开发相关，但不是加速 Python 的前置条件。

## 数据流心智模型

无论使用哪种工具，一次调用都包含边界成本：

```text
Python 对象
   |
   | 参数检查、类型转换、可能的数据复制
   v
C 值 / 连续缓冲区
   |
   | 执行热点计算
   v
C 结果
   |
   | 转换为 Python 对象或写回缓冲区
   v
Python 调用者
```

如果每次跨边界只做一次加法，调用成本可能超过计算本身。有效的加速通常把一批工作交给一次 C 调用，例如处理整个数组、解析整块数据或完成完整算法。

## 目录说明

| 路径 | 说明 |
| --- | --- |
| `Makefile` | 统一构建、测试、基准和清理入口 |
| `chapters/` | 从接口选择到发布的教程 |
| `arithmetic.h/.c` | 具有明确 C ABI 的动态库 |
| `ctypes_demo.py` | 动态库加载、签名声明、数组传递和错误处理 |
| `mymath_module.c` | 使用 Python/C API 实现的原生模块 |
| `c_extension_demo.py` | 原生扩展行为演示 |
| `benchmark.py` | 基于中位数的正确性与性能比较 |
| `test_using_c.py` | 跨边界契约的自动测试 |
| `cython_example.pyx` | 类型化素数筛示例 |
| `setup_cython.py` | Cython 可选构建入口 |
| `CPYTHON_SOURCE_GUIDE.md` | CPython 对象模型和源码阅读路线 |

教程中的“零拷贝”表示包装层没有主动复制数据，不代表硬件、操作系统或下游库永远不会产生其他复制。借用缓冲区也意味着调用期间必须遵守导出者的生命周期和并发规则。

构建产物全部进入 `build/`，不会与源码混在一起。使用 `make clean` 删除它们。

## 何时不应该用 C

- 还没有测量，不知道热点在哪里。
- 主要耗时来自网络、磁盘或数据库等待。
- 算法复杂度有明显改进空间。
- 标准库、NumPy 或成熟第三方库已经提供优化实现。
- 输入规模太小，跨语言调用和转换成本占主导。
- 团队无法承担原生崩溃、平台构建和 ABI 兼容的维护成本。

C 可以减少特定热点的 CPU 时间，但也把内存安全、整数范围和构建兼容责任交给扩展作者。正确结果和清晰接口始终先于加速比。
