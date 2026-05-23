import asyncio
import time


def print_section(title):
    print(f"\n{'=' * 12} {title} {'=' * 12}")


async def say_after(delay, message):
    """等待一段时间后返回结果。

    async def 调用后不会立刻执行函数体，而是创建一个 coroutine object。
    只有被 await、asyncio.run()、asyncio.create_task() 或 gather() 调度后才会运行。
    """
    print(f"start: {message}")
    await asyncio.sleep(delay)  # 让出事件循环，其他 coroutine 可以继续执行
    print(f"done:  {message}")
    return message.upper()


async def basic_await():
    print_section("1. basic await")

    result = await say_after(0.3, "hello")
    print(f"result: {result}")


async def sequential_vs_concurrent():
    print_section("2. sequential vs concurrent")

    start = time.perf_counter()
    await say_after(0.5, "sequential task 1")
    await say_after(0.5, "sequential task 2")
    print(f"sequential elapsed: {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    results = await asyncio.gather(
        say_after(0.5, "concurrent task 1"),
        say_after(0.5, "concurrent task 2"),
    )
    print(f"concurrent elapsed: {time.perf_counter() - start:.2f}s")
    print(f"gather results: {results}")


async def create_task_example():
    print_section("3. create_task")

    task = asyncio.create_task(say_after(0.8, "background task"))

    for index in range(3):
        print(f"main coroutine keeps working: step {index + 1}")
        await asyncio.sleep(0.25)

    result = await task
    print(f"background result: {result}")


async def slow_operation():
    try:
        print("slow operation started")
        await asyncio.sleep(2)
        print("slow operation finished")
        return "slow result"
    except asyncio.CancelledError:
        print("slow operation was cancelled")
        raise


async def timeout_example():
    print_section("4. timeout and cancellation")

    try:
        result = await asyncio.wait_for(slow_operation(), timeout=0.6)
        print(result)
    except asyncio.TimeoutError:
        print("timeout: slow operation took too long")


async def maybe_fail(name, fail=False):
    await asyncio.sleep(0.2)

    if fail:
        raise ValueError(f"{name} failed")

    return f"{name} succeeded"


async def error_handling_example():
    print_section("5. gather error handling")

    try:
        await asyncio.gather(
            maybe_fail("task A"),
            maybe_fail("task B", fail=True),
            maybe_fail("task C"),
        )
    except ValueError as error:
        print(f"gather stopped with error: {error}")

    results = await asyncio.gather(
        maybe_fail("task D"),
        maybe_fail("task E", fail=True),
        maybe_fail("task F"),
        return_exceptions=True,
    )
    print(f"gather with return_exceptions=True: {results}")


async def producer(queue):
    for item in range(1, 4):
        await asyncio.sleep(0.2)
        await queue.put(item)
        print(f"produced: {item}")

    await queue.put(None)  # sentinel value: 通知 consumer 没有更多数据了


async def consumer(queue):
    while True:
        item = await queue.get()

        if item is None:
            queue.task_done()
            print("consumer stopped")
            break

        print(f"consumed: {item}")
        queue.task_done()


async def queue_example():
    print_section("6. producer / consumer queue")

    queue = asyncio.Queue()

    producer_task = asyncio.create_task(producer(queue))
    consumer_task = asyncio.create_task(consumer(queue))

    await producer_task
    await queue.join()
    await consumer_task


async def main():
    await basic_await()
    await sequential_vs_concurrent()
    await create_task_example()
    await timeout_example()
    await error_handling_example()
    await queue_example()


if __name__ == "__main__":
    asyncio.run(main())
