# 上下文管理器与异常处理

## 一、with 语句：资源安全管理

`with` 语句保证资源在使用完毕后一定被释放，即使中途抛出异常。

```python
# 不用 with：异常时 f.close() 不会执行
f = open("data.txt")
data = f.read()  # 如果这里抛异常，文件句柄泄漏
f.close()

# 用 with：无论是否异常，退出时自动调用 f.close()
with open("data.txt") as f:
    data = f.read()

# 同时管理多个资源
with open("src.txt") as src, open("dst.txt", "w") as dst:
    dst.write(src.read())
```

---

## 二、自定义上下文管理器（类实现）

实现 `__enter__` 和 `__exit__` 两个方法：

```python
class DatabaseConnection:
    def __init__(self, dsn):
        self.dsn = dsn
        self.conn = None

    def __enter__(self):
        self.conn = connect(self.dsn)  # 获取资源
        return self.conn               # as 子句拿到的值

    def __exit__(self, exc_type, exc_val, exc_tb):
        # exc_type/exc_val/exc_tb：异常信息，无异常时均为 None
        if self.conn:
            if exc_type is None:
                self.conn.commit()     # 无异常：提交
            else:
                self.conn.rollback()   # 有异常：回滚
            self.conn.close()
        return False  # False/None：不抑制异常，让它继续传播
                      # True：抑制异常（慎用）

with DatabaseConnection("sqlite:///app.db") as conn:
    conn.execute("INSERT INTO users VALUES (1, 'Alice')")
```

**`__exit__` 返回值：**
- `False` / `None`：异常继续向上传播（通常选这个）
- `True`：吞掉异常，`with` 块之后的代码正常执行

---

## 三、contextlib.contextmanager：生成器实现

用 `yield` 把上下文管理器写成函数，更简洁：

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(name):
    print(f"获取资源：{name}")
    resource = acquire(name)  # __enter__ 逻辑
    try:
        yield resource         # with ... as resource 拿到的值
    except SomeError as e:
        handle_error(e)        # 可以在这里处理特定异常
        raise                  # 重新抛出，不要静默吞掉
    finally:
        release(resource)      # __exit__ 逻辑，总是执行

with managed_resource("db_pool") as res:
    res.query("SELECT 1")
```

**规则：** `yield` 前是 `__enter__`，`yield` 后（finally）是 `__exit__`，`yield` 只能出现一次。

---

## 四、contextlib 常用工具

```python
from contextlib import suppress, nullcontext

# suppress：静默忽略指定异常（只在你确定可以忽略时用）
with suppress(FileNotFoundError):
    os.remove("temp.txt")  # 文件不存在时不报错

# nullcontext：占位上下文管理器，用于条件性 with
def process(file_path, conn=None):
    ctx = conn if conn else nullcontext()
    with ctx:
        ...  # conn 为 None 时不做任何上下文管理
```

---

## 五、异常处理 + 上下文管理器组合模式

```python
@contextmanager
def sdk_operation(operation_name):
    """统一包装 SDK 操作：日志 + 异常转换"""
    import logging
    logger = logging.getLogger("sdk")
    logger.info(f"开始：{operation_name}")
    try:
        yield
        logger.info(f"完成：{operation_name}")
    except SdkBaseError:
        raise  # SDK 自有异常直接透传
    except Exception as e:
        logger.error(f"操作失败：{operation_name}", exc_info=True)
        raise RuntimeError(f"{operation_name} 执行失败") from e

# 使用
with sdk_operation("上传文件"):
    upload(file_path)
```
