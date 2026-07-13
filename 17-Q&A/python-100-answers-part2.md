# Python 100 道面试题答案（第二部分：36-70）

## 异步编程（36-40）

### 36. 解释 async/await 与回调的区别

**答案：**

**回调方式（Callback Hell）：**
```python
def fetch_user(user_id, callback):
    # 模拟异步操作
    time.sleep(1)
    callback({"id": user_id, "name": "Alice"})

def fetch_posts(user, callback):
    time.sleep(1)
    callback([{"title": "Post 1"}, {"title": "Post 2"}])

def fetch_comments(post, callback):
    time.sleep(1)
    callback(["Comment 1", "Comment 2"])

# 回调地狱
fetch_user(1, lambda user:
    fetch_posts(user, lambda posts:
        fetch_comments(posts[0], lambda comments:
            print(comments)
        )
    )
)
```

**async/await 方式：**
```python
import asyncio

async def fetch_user(user_id):
    await asyncio.sleep(1)
    return {"id": user_id, "name": "Alice"}

async def fetch_posts(user):
    await asyncio.sleep(1)
    return [{"title": "Post 1"}, {"title": "Post 2"}]

async def fetch_comments(post):
    await asyncio.sleep(1)
    return ["Comment 1", "Comment 2"]

async def main():
    user = await fetch_user(1)
    posts = await fetch_posts(user)
    comments = await fetch_comments(posts[0])
    print(comments)

asyncio.run(main())
```

**优势：**
- 代码更线性，易读
- 避免回调地狱
- 更好的错误处理
- 支持 try/except

---

### 37. 如何在同步代码中调用异步函数？

**答案：**

```python
import asyncio

async def async_function():
    await asyncio.sleep(1)
    return "Result"

# 方法 1：使用 asyncio.run()
result = asyncio.run(async_function())
print(result)

# 方法 2：获取事件循环
loop = asyncio.get_event_loop()
result = loop.run_until_complete(async_function())
print(result)

# 方法 3：在已有事件循环中运行（Jupyter）
# await async_function()  # 只在 async 环境中有效

# 方法 4：使用 asyncio.create_task（在 async 函数中）
async def caller():
    task = asyncio.create_task(async_function())
    result = await task
    return result

# 方法 5：同步包装器
def sync_wrapper():
    return asyncio.run(async_function())

# 注意：不能在已有事件循环中使用 asyncio.run()
# 解决方案：使用 nest_asyncio
import nest_asyncio
nest_asyncio.apply()
```

---

### 38. 解释以下代码的执行顺序

**代码：**
```python
import asyncio

async def main():
    print("1")
    await asyncio.sleep(0)
    print("2")

print("0")
asyncio.run(main())
print("3")
```

**答案：**
输出顺序：0, 1, 2, 3

**执行流程：**
1. `print("0")` - 同步执行
2. `asyncio.run(main())` - 启动事件循环
3. `print("1")` - 在协程中执行
4. `await asyncio.sleep(0)` - 让出控制权，但立即恢复
5. `print("2")` - 继续执行协程
6. 事件循环结束
7. `print("3")` - 同步执行

**更复杂的例子：**
```python
import asyncio

async def task1():
    print("Task 1 start")
    await asyncio.sleep(2)
    print("Task 1 end")

async def task2():
    print("Task 2 start")
    await asyncio.sleep(1)
    print("Task 2 end")

async def main():
    print("Main start")
    await asyncio.gather(task1(), task2())
    print("Main end")

asyncio.run(main())

# 输出:
# Main start
# Task 1 start
# Task 2 start
# Task 2 end  (1秒后)
# Task 1 end  (2秒后)
# Main end
```

---

### 39. 什么是事件循环？如何获取当前事件循环？

**答案：**

事件循环是异步编程的核心，负责调度和执行异步任务。

```python
import asyncio

# 获取当前事件循环
loop = asyncio.get_event_loop()

# 获取正在运行的事件循环（只在 async 函数中）
async def get_running_loop():
    loop = asyncio.get_running_loop()
    return loop

# 创建新的事件循环
new_loop = asyncio.new_event_loop()
asyncio.set_event_loop(new_loop)

# 手动运行事件循环
async def task():
    await asyncio.sleep(1)
    return "Done"

loop = asyncio.get_event_loop()
result = loop.run_until_complete(task())
print(result)

# 运行直到所有任务完成
loop.run_forever()  # 持续运行
loop.stop()  # 停止循环

# 事件循环的生命周期
async def main():
    loop = asyncio.get_running_loop()
    
    # 调度回调
    loop.call_soon(lambda: print("Called soon"))
    
    # 延迟调度
    loop.call_later(1, lambda: print("Called later"))
    
    # 在特定时间调度
    loop.call_at(loop.time() + 2, lambda: print("Called at time"))
    
    await asyncio.sleep(3)

asyncio.run(main())
```

---

### 40. 如何取消一个正在运行的协程？

**答案：**

```python
import asyncio

async def long_running_task():
    try:
        print("Task started")
        await asyncio.sleep(10)
        print("Task completed")
    except asyncio.CancelledError:
        print("Task was cancelled")
        raise  # 重要：重新抛出异常

async def main():
    # 创建任务
    task = asyncio.create_task(long_running_task())
    
    # 等待 1 秒后取消
    await asyncio.sleep(1)
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        print("Main: Task cancelled")

asyncio.run(main())

# 输出:
# Task started
# Task was cancelled
# Main: Task cancelled

# 取消多个任务
async def main2():
    tasks = [
        asyncio.create_task(long_running_task()),
        asyncio.create_task(long_running_task()),
        asyncio.create_task(long_running_task())
    ]
    
    await asyncio.sleep(1)
    
    # 取消所有任务
    for task in tasks:
        task.cancel()
    
    # 等待所有任务完成（包括取消）
    await asyncio.gather(*tasks, return_exceptions=True)

# 超时取消
async def with_timeout():
    try:
        await asyncio.wait_for(long_running_task(), timeout=2.0)
    except asyncio.TimeoutError:
        print("Task timed out")

# 使用上下文管理器
from contextlib import suppress

async def main3():
    task = asyncio.create_task(long_running_task())
    
    await asyncio.sleep(1)
    task.cancel()
    
    with suppress(asyncio.CancelledError):
        await task
```

---

## 性能优化（41-45）

### 41. 使用 `__slots__` 能节省多少内存？

**答案：**

```python
import sys

class Without