# 标准库：时间与数学

## `datetime` 与 `zoneinfo`

- [ ] 我能区分日期、时间、时间间隔和带时区的时间。
- [ ] 我会使用 aware datetime、`timedelta`、`ZoneInfo` 和 ISO 8601。

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

utc_now = datetime.now(timezone.utc)
shanghai = utc_now.astimezone(ZoneInfo("Asia/Shanghai"))
print(shanghai.isoformat())
```

常见坑：不要混用 naive 和 aware datetime；时区转换与格式化是两件事；跨夏令时区域不要手写固定 UTC 偏移。

自查：为什么服务器通常保存 UTC？`replace(tzinfo=...)` 与 `astimezone(...)` 有何不同？

练习：解析一个 ISO 8601 时间，转换到上海时区，并计算距现在的小时数。

仓库关联：扩展主题。

## `time`

- [ ] 我知道 `time.time()` 是墙上时钟，`time.monotonic()` 适合测持续时间。
- [ ] 我会使用 `sleep` 和单调时钟实现超时测量。

```python
import time

started = time.monotonic()
time.sleep(0.01)
print(time.monotonic() - started)
```

常见坑：系统时间可能被校准，不能用 `time.time()` 判断耗时；`sleep` 不是精确调度器。

自查：重试超时为什么应使用 `monotonic()`？

练习：写一个上下文管理器，记录代码块运行耗时。

仓库关联：扩展主题。

## `math`、`decimal`、`statistics`、`random`

- [ ] 我知道浮点数、十进制定点数、统计量和伪随机数各自的适用边界。
- [ ] 我会使用 `isclose`、`Decimal`、`mean`、`median`、`Random`。

```python
from decimal import Decimal
from math import isclose
from statistics import mean

print(isclose(0.1 + 0.2, 0.3))
print(Decimal("0.1") + Decimal("0.2"))
print(mean([2, 4, 6]))
```

常见坑：金额不要直接依赖二进制浮点；`random` 不用于密码和令牌；统计函数要考虑空样本和异常值。

自查：为什么 `Decimal("0.1")` 比 `Decimal(0.1)` 更可靠？安全随机数应使用哪个模块？

练习：实现一个金额求和函数，并为浮点计算写容差断言。

仓库关联：扩展主题。

