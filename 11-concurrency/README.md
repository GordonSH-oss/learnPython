# 并发和异步

并发学习的重点不是背 API，而是判断任务类型：I/O 密集任务适合线程或 `asyncio`，CPU 密集任务适合多进程或把计算交给底层 C/NumPy/PyTorch。

## 学习目标

- 区分并发、并行、异步。
- 会用 `asyncio` 控制超时、取消和并发数量。
- 理解 queue、worker、backpressure 的关系。
- 知道什么时候用线程池、进程池或 async HTTP 客户端。

## 本目录文件

- `asyncio_pipeline.py`：用 `asyncio.Queue`、worker 和 timeout 搭一个最小任务流水线。

## 学习路线

1. 先运行 `python 11-concurrency/asyncio_pipeline.py`。
2. 把 worker 数从 2 改成 1 和 5，观察总耗时变化。
3. 把某个任务的延迟改大，观察 `asyncio.timeout()` 如何让任务失败但不拖垮整体。
4. 再学习 `httpx.AsyncClient`，把示例里的模拟 I/O 换成真实 HTTP 请求。

## 关键判断

| 场景 | 优先工具 |
| --- | --- |
| 调很多 HTTP API | `asyncio` + `httpx.AsyncClient` |
| 文件或阻塞库调用 | `ThreadPoolExecutor` |
| Python 纯计算 | `ProcessPoolExecutor` |
| NumPy/PyTorch 计算 | 先用库自身的向量化/GPU 能力 |
