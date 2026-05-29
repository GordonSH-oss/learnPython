# Python 基础异常处理

## 一、异常处理语法结构

```python
try:
    # 可能出错的代码
    result = 10 / 0
except ZeroDivisionError as e:
    # 捕获特定异常
    print(f"除零错误：{e}")
except (TypeError, ValueError) as e:
    # 同时捕获多种异常
    print(f"类型或值错误：{e}")
except Exception as e:
    # 兜底：捕获所有异常（慎用，会掩盖 bug）
    print(f"未知错误：{e}")
else:
    # try 块无异常时执行（不常用但很有用）
    print("执行成功，结果：", result)
finally:
    # 无论是否异常都执行（清理资源必用）
    print("清理完毕")
```

**各子句职责：**
- `except`：捕获并处理异常
- `else`：成功路径的后续逻辑，比放在 try 末尾更清晰
- `finally`：释放资源（文件、连接、锁），不能省略

---

## 二、Python 内置异常层次（常用部分）

```
BaseException
├── SystemExit          # sys.exit() 触发，不要用 except Exception 捕获
├── KeyboardInterrupt   # Ctrl+C，同上
└── Exception           # 所有普通异常的基类
    ├── TypeError       # 类型不匹配
    ├── ValueError      # 类型对但值非法（如 int("abc")）
    ├── AttributeError  # 访问不存在的属性
    ├── KeyError        # 字典键不存在
    ├── IndexError      # 列表下标越界
    ├── NameError       # 变量未定义
    ├── FileNotFoundError  # 文件不存在（OSError 子类）
    ├── PermissionError    # 权限不足（OSError 子类）
    ├── TimeoutError       # 超时（OSError 子类）
    ├── RuntimeError    # 运行时逻辑错误
    ├── StopIteration   # 迭代器耗尽
    └── ImportError     # 模块导入失败
```

**捕获原则：**
- 优先捕获具体异常，不要直接 `except Exception`
- 永远不要裸 `except:`（会吞掉 `KeyboardInterrupt`）
- `SystemExit` / `KeyboardInterrupt` 不要捕获，除非你知道自己在做什么

---

## 三、raise：主动抛出异常

```python
def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")  # 抛出内置异常
    return a / b

# 重新抛出当前异常（在 except 块内）
try:
    divide(1, 0)
except ValueError:
    print("记录日志...")
    raise  # 不带参数的 raise：原样重新抛出，保留完整堆栈
```

---

## 四、异常链：raise ... from

```python
def load_config(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError as e:
        # 转换异常类型，同时保留原始原因
        raise RuntimeError(f"配置文件加载失败：{path}") from e
```

- `from e`：显式异常链，traceback 会显示 "The above exception was the direct cause of..."
- `from None`：抑制原始异常，对外只暴露新异常（SDK 屏蔽底层细节时用）

---

## 五、获取异常详细信息

```python
import traceback

try:
    int("not a number")
except ValueError as e:
    print(type(e).__name__)   # ValueError
    print(e.args)             # ('invalid literal for int()...',)
    print(str(e))             # invalid literal for int() with base 10: 'not a number'
    traceback.print_exc()     # 打印完整堆栈到 stderr
    tb_str = traceback.format_exc()  # 获取堆栈字符串（写日志用）
```

---

## 六、常见反模式

```python
# 反模式 1：吞掉异常，问题无声消失
try:
    risky()
except Exception:
    pass  # 永远不要这样做

# 反模式 2：捕获范围太宽
try:
    result = process(data)
except Exception as e:
    log(e)  # 连 KeyboardInterrupt 都可能被捕获

# 正确做法：只捕获你能处理的异常
try:
    result = process(data)
except (ValueError, KeyError) as e:
    handle_bad_input(e)
```
