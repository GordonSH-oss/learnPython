# 08 原生扩展调试、构建与发布

## 学习目标

完成本章后，你应该能够：

- 区分 Python 异常、导入错误、链接错误和原生崩溃
- 构建 debug 或 sanitizer 版本并用 LLDB/GDB 定位 C 栈帧
- 检查扩展依赖、架构和导出符号
- 使用 `pyproject.toml` 和 wheel 构建隔离交付扩展
- 设计 Python、平台和 ABI 测试矩阵

## 四类失败

| 失败 | 典型表现 | 首先检查 |
| --- | --- | --- |
| Python 契约错误 | `TypeError`、`ValueError` | 参数解析和异常协议 |
| 导入/装载错误 | `ImportError`、找不到 symbol | 文件名、架构、依赖和初始化符号 |
| 链接错误 | 构建阶段 undefined symbol | 目标文件、库顺序、Python 配置 |
| 原生错误 | crash、hang、内存损坏 | C 栈、sanitizer、生命周期、线程 |

Python traceback 通常无法解释越界写或错误引用计数。原生扩展与解释器同进程，崩溃会终止整个 Python 进程。

## Debug 构建

性能构建使用 `-O3`，调试时应优先保留符号和清晰栈帧：

```bash
make clean
make CFLAGS='-std=c17 -O0 -g -Wall -Wextra -Wpedantic' all
```

当前 Makefile 不记录 CFLAGS 变化，切换配置前必须 clean，或为 debug/release 使用不同构建目录。

优化后的变量可能被删除、内联或重排。不要在难以解释的 `-O3` 崩溃中直接猜测源码状态。

## LLDB

```bash
lldb -- python3 -c 'import sys; sys.path.insert(0, "build"); import mymath; mymath.sum_squares(10)'
```

常用命令：

```text
breakpoint set --name mymath_sum_squares
run
thread backtrace all
frame variable
next
step
```

崩溃时保留 Python 版本、扩展文件、输入、平台架构和完整 C backtrace。多线程 hang 应查看所有线程栈和锁等待位置。

## Sanitizer

Clang/GCC 可构建 ASan/UBSan：

```bash
make clean
make CFLAGS='-std=c17 -O1 -g -Wall -Wextra -Wpedantic \
  -fsanitize=address,undefined -fno-omit-frame-pointer' all
```

Python 可执行文件和动态装载的 sanitizer runtime 在不同平台上可能需要额外配置，例如预加载 runtime。若普通 Python 无法装载 sanitizer 扩展，应使用工具链文档推荐的方法或构建 sanitizer 版本 CPython。

ThreadSanitizer 需要单独构建，通常不能与 ASan 同时使用。它只对实际执行到的并发路径报告问题。

## Python 的原生调试构建

CPython debug build 会启用额外断言和内存检查，扩展后缀与 ABI 也可能不同。还可以使用：

```bash
PYTHONMALLOC=debug python3 -X dev -m unittest -v test_using_c.py
```

这不能替代 sanitizer，但能更早暴露部分 API 误用和内存分配器问题。

## 检查二进制

macOS：

```bash
file build/mymath*.so
otool -L build/mymath*.so
nm -gU build/mymath*.so | rg PyInit
```

Linux：

```bash
file build/mymath*.so
ldd build/mymath*.so
readelf -d build/mymath*.so
nm -D build/mymath*.so | rg PyInit
```

确认：

- 架构与 Python 进程一致
- 导出 `PyInit_mymath`
- 依赖库能在目标机器找到
- 没有意外绑定本机绝对路径

## 从 Makefile 到 `pyproject.toml`

Makefile 适合解释底层编译命令，但发布 Python 包应声明构建后端：

```toml
[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"
```

源代码包和 wheel 应在隔离环境构建：

```bash
python -m pip install build
python -m build
python -m venv /tmp/wheel-test
/tmp/wheel-test/bin/python -m pip install dist/*.whl
/tmp/wheel-test/bin/python -c 'import mymath; print(mymath.sum_squares(10))'
```

测试本地源码目录中的 import 不等于 wheel 可安装。最终验收必须从干净环境安装实际产物。

## Wheel 平台矩阵

原生 wheel 通常绑定 Python ABI、操作系统和 CPU 架构。发布前决定：

- CPython 版本范围
- macOS arm64、x86_64 或 universal2
- Linux manylinux/musllinux 目标
- Windows x64/ARM64 与 MSVC 工具链
- 是否支持 free-threaded CPython
- 是否使用 Limited API/Stable ABI

Stable ABI 只能减少 CPython 小版本绑定，不会解决外部库、CPU、操作系统和编译器 ABI 问题。

## 外部动态库

ctypes 包装或扩展若依赖自己的 `.dylib`/`.so`，必须决定：

- wheel 是否捆绑库
- 运行时如何定位
- SONAME/install name/rpath 如何设置
- 许可证是否允许再分发
- 安全更新和 ABI 版本如何管理

常用修复工具包括 Linux `auditwheel`、macOS `delocate` 和 Windows `delvewheel`。它们不能修复不兼容 ABI，只负责检查或重写可再分发依赖关系。

## CI 验证层次

1. Python 单元测试和错误契约。
2. C 编译零警告。
3. debug/sanitizer 测试。
4. 每个目标平台构建 wheel。
5. 干净环境安装 wheel 并运行 smoke test。
6. 代表性平台运行 benchmark 趋势。

不要只在开发者已有 build 目录的机器上测试；残留动态库和头文件会隐藏打包缺陷。

## 崩溃兼容策略

生产包可以保留纯 Python 回退实现，并提供环境变量或 feature flag 禁用原生路径。这样有助于：

- 在不支持平台保持功能
- 快速隔离原生回归
- 比较正确性和性能
- 在崩溃现场临时恢复服务

回退实现必须共享测试，避免两条路径语义漂移。

## 发布检查表

- 公共 Python API 和异常行为有测试。
- 引用、buffer、C 内存和系统资源在所有路径释放。
- GIL 和线程安全契约有文档与并发测试。
- wheel 在干净环境安装和导入。
- 二进制不引用开发机绝对路径。
- 支持矩阵与实际 CI 一致。
- benchmark 使用 release 构建和真实输入。
- 有版本策略、符号文件和原生崩溃复现说明。

## 动手练习

1. 分别构建 `-O0 -g` 和 `-O3` 扩展，在 LLDB 断点中比较变量可见性。
2. 使用 `nm` 验证模块导出 `PyInit_mymath`。
3. 创建最小 `pyproject.toml`，构建 wheel 并在全新 venv 安装。
4. 检查 wheel 文件名中的 Python、ABI、平台标签。
5. 设计 Linux、macOS、Windows 与 Python 版本 CI 矩阵，并说明哪些任务运行 sanitizer、wheel smoke test 和 benchmark。
