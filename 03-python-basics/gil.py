"""
Python GIL 教程：为什么 GIL 会影响多线程计算

运行方式：
    python 03-python-basics/gil.py

可以调大计算量，让差异更明显：
    python 03-python-basics/gil.py --work 20000000

学习目标：
    1. 理解 GIL 是什么。
    2. 理解为什么 CPU 密集型任务用多线程通常不会变快。
    3. 区分 CPU 密集型任务和 I/O 密集型任务。
    4. 知道什么时候该用 threading，什么时候该用 multiprocessing。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


# 本目录里有一个教学文件 copy.py。直接运行本文件时，Python 会把脚本目录
# 放到 sys.path[0]，这可能遮蔽标准库 copy 模块，并影响 multiprocessing 等库。
# 这个教程不依赖同目录模块，所以先移除脚本目录，避免本地教学文件干扰标准库导入。
SCRIPT_DIR = Path(__file__).resolve().parent
if sys.path and Path(sys.path[0]).resolve() == SCRIPT_DIR:
    sys.path.pop(0)

import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Callable


LINE = "=" * 72


def title(text: str) -> None:
    print(f"\n{LINE}\n{text}\n{LINE}")


def explain_gil() -> None:
    title("1. GIL 是什么")
    print(
        """
GIL 的全称是 Global Interpreter Lock，中文通常叫“全局解释器锁”。

在常见的 CPython 解释器里，多个线程可以同时存在，但同一时刻通常只有
一个线程能执行 Python 字节码。

可以把 CPU 密集型 Python 代码想象成下面这样：

    线程 A 想执行 Python 字节码 -> 先拿 GIL -> 执行一小段 -> 释放 GIL
    线程 B 想执行 Python 字节码 -> 先拿 GIL -> 执行一小段 -> 释放 GIL

关键点：
  - GIL 保护的是 CPython 解释器内部对象管理和内存管理。
  - GIL 不是你代码里的 Lock，但它会影响 Python 字节码的并行执行。
  - 多线程仍然有用，只是对“纯 Python CPU 计算”通常没有加速效果。
"""
    )

    gil_status = getattr(sys, "_is_gil_enabled", None)
    if callable(gil_status):
        print("当前解释器 GIL 是否启用:", gil_status())
    else:
        print("当前解释器未暴露 sys._is_gil_enabled()，通常可按 CPython GIL 模型理解。")

    print("Python 实现:", sys.implementation.name)
    print("Python 版本:", sys.version.split()[0])
    print("CPU 核心数:", os.cpu_count())


def cpu_bound_task(work: int) -> int:
    """纯 Python CPU 密集型计算，用来观察 GIL 对线程的影响。"""
    total = 0
    for number in range(work):
        total += (number * number) % 97
    return total


def io_bound_task(seconds: float) -> float:
    """模拟 I/O 等待：sleep 时线程不需要持续执行 Python 字节码。"""
    time.sleep(seconds)
    return seconds


def measure(label: str, fn: Callable[[], object]) -> float:
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    print(f"{label:<28} 耗时: {elapsed:.3f}s  结果摘要: {str(result)[:60]}")
    return elapsed


def run_sequential_cpu(tasks: int, work: int) -> list[int]:
    return [cpu_bound_task(work) for _ in range(tasks)]


def run_threaded_cpu(tasks: int, work: int) -> list[int]:
    with ThreadPoolExecutor(max_workers=tasks) as executor:
        return list(executor.map(cpu_bound_task, [work] * tasks))


def run_process_cpu(tasks: int, work: int) -> list[int]:
    with ProcessPoolExecutor(max_workers=tasks) as executor:
        return list(executor.map(cpu_bound_task, [work] * tasks))


def run_sequential_io(tasks: int, seconds: float) -> list[float]:
    return [io_bound_task(seconds) for _ in range(tasks)]


def run_threaded_io(tasks: int, seconds: float) -> list[float]:
    with ThreadPoolExecutor(max_workers=tasks) as executor:
        return list(executor.map(io_bound_task, [seconds] * tasks))


def cpu_experiment(tasks: int, work: int) -> None:
    title("2. 实验：CPU 密集型任务，多线程通常不会更快")
    print(
        f"""
本实验会执行 {tasks} 个相同的纯 Python 计算任务。
每个任务循环 {work:,} 次。

预期：
  - 顺序执行：一个任务接一个任务跑。
  - 多线程：多个线程争抢同一个 GIL，不能真正并行执行 Python 字节码。
  - 多进程：每个进程有自己的解释器和自己的 GIL，可以利用多个 CPU 核心。
"""
    )

    sequential = measure(
        "顺序执行 CPU 任务",
        lambda: run_sequential_cpu(tasks, work),
    )
    threaded = measure(
        "多线程执行 CPU 任务",
        lambda: run_threaded_cpu(tasks, work),
    )

    multiprocess: float | None = None
    try:
        multiprocess = measure(
            "多进程执行 CPU 任务",
            lambda: run_process_cpu(tasks, work),
        )
    except (OSError, PermissionError) as error:
        print(f"多进程执行 CPU 任务              当前环境不可用: {error}")
        print("说明：某些沙箱或受限环境会禁止 multiprocessing 需要的系统信号量。")

    print(
        f"""
观察：
  - 多线程 / 顺序执行耗时比: {threaded / sequential:.2f}x
  - 多进程 / 顺序执行耗时比: {multiprocess / sequential:.2f}x
""" if multiprocess is not None else f"""
观察：
  - 多线程 / 顺序执行耗时比: {threaded / sequential:.2f}x
  - 多进程实验在当前环境不可用；在普通本机终端中通常可以运行。
"""
    )

    print(
        """
如果多线程没有明显变快，这是 GIL 对 CPU 密集型 Python 代码的典型影响。
多进程可能更快，也可能因为任务太小、进程启动和数据传输成本太高而不明显。
"""
    )


def io_experiment(tasks: int, seconds: float) -> None:
    title("3. 实验：I/O 密集型任务，多线程通常有用")
    print(
        f"""
本实验用 time.sleep({seconds}) 模拟 I/O 等待。
真实场景可以是网络请求、数据库查询、文件读写等。

等待 I/O 时，线程不会一直占用 Python 字节码执行权，所以其他线程有机会运行。
这就是为什么 GIL 存在时，多线程仍然适合很多 I/O 密集型任务。
"""
    )

    sequential = measure(
        "顺序执行 I/O 等待",
        lambda: run_sequential_io(tasks, seconds),
    )
    threaded = measure(
        "多线程执行 I/O 等待",
        lambda: run_threaded_io(tasks, seconds),
    )

    print(
        f"""
观察：
  - 多线程 / 顺序执行耗时比: {threaded / sequential:.2f}x

通常你会看到多线程 I/O 明显更快，因为多个等待可以重叠发生。
"""
    )


def lock_vs_gil_demo() -> None:
    title("4. GIL 不是用来保护你业务数据的锁")
    print(
        """
常见误区：
  “有 GIL，所以多线程操作共享变量一定安全。”

这个说法不可靠。
GIL 保护解释器内部状态，不等于保护你的业务不变量。
当多个线程读写同一份业务数据时，仍然应该使用 threading.Lock、
Queue、不可变数据、消息传递等方式设计同步。
"""
    )

    shared_counter = 0
    lock = threading.Lock()

    def add_many(times: int) -> None:
        nonlocal shared_counter
        for _ in range(times):
            with lock:
                shared_counter += 1

    threads = [threading.Thread(target=add_many, args=(10_000,)) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print("使用 threading.Lock 后，计数结果:", shared_counter)
    print("预期结果:", 4 * 10_000)


def decision_guide() -> None:
    title("5. 什么时候用线程，什么时候用进程")
    print(
        """
选择建议：
  - CPU 密集型纯 Python 计算：优先 multiprocessing、ProcessPoolExecutor、
    C 扩展、NumPy、向量化、任务队列，或其他能绕开 GIL 限制的方案。
  - I/O 密集型任务：threading、ThreadPoolExecutor、asyncio 都可以考虑。
  - 共享状态很多的并发代码：先减少共享状态，再选择同步工具。

一句话记忆：
  - 线程适合“等”：网络、磁盘、数据库、外部服务。
  - 进程适合“算”：大量 Python 循环、解析、压缩、加密、图像处理等 CPU 工作。
"""
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Python GIL 可运行教程")
    parser.add_argument(
        "--tasks",
        type=int,
        default=4,
        help="并发任务数量，默认 4",
    )
    parser.add_argument(
        "--work",
        type=int,
        default=5_000_000,
        help="每个 CPU 任务的循环次数，默认 5,000,000",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.5,
        help="每个 I/O 模拟任务的 sleep 秒数，默认 0.5",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    explain_gil()
    cpu_experiment(tasks=args.tasks, work=args.work)
    io_experiment(tasks=args.tasks, seconds=args.sleep)
    lock_vs_gil_demo()
    decision_guide()


if __name__ == "__main__":
    main()
