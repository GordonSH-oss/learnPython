# 标准库：测试、安全与资源管理

## `unittest` 与 `unittest.mock`

- [ ] 我能写测试用例、断言、fixture 生命周期和 mock。
- [ ] 我知道 mock 必须 patch 使用方查找依赖的路径。

```python
import unittest

class TestTotal(unittest.TestCase):
    def test_total(self) -> None:
        self.assertEqual(sum([1, 2, 3]), 6)

if __name__ == "__main__":
    unittest.main()
```

常见坑：测试不应依赖真实网络或时间；mock 过多会掩盖真实集成问题；`patch("定义模块.名称")` 通常比 patch 第三方原始模块正确。

自查：单元测试与集成测试边界是什么？为什么 mock 的位置很重要？

练习：为读取 API 的函数 mock 网络客户端，分别覆盖成功、超时和无效响应。

仓库关联：扩展主题；第三方测试见 [pytest 清单](third-party-quality.md)。

## `contextlib`

- [ ] 我知道上下文管理器保证进入和退出逻辑成对执行。
- [ ] 我会使用 `contextmanager`、`closing`、`suppress` 和 `ExitStack`。

```python
from contextlib import contextmanager

@contextmanager
def managed(name: str):
    print("open", name)
    try:
        yield name
    finally:
        print("close", name)

with managed("resource") as value:
    print(value)
```

常见坑：清理代码放在 `finally`；不要无条件吞掉异常；多个动态资源适合 `ExitStack`。

自查：`with` 块中抛异常时退出代码是否执行？`suppress` 什么时候会隐藏真正的问题？

练习：用 `ExitStack` 同时管理多个文件，并让其中一个打开失败时已打开资源仍被关闭。

仓库关联：[上下文管理器](../10-error-handle/context_manager.py)。

## `hashlib` 与 `secrets`

- [ ] 我能区分哈希、加密、随机数和密码派生。
- [ ] 我会使用 `sha256`、`hmac.compare_digest` 和 `secrets.token_urlsafe`。

```python
import hashlib
import secrets

digest = hashlib.sha256(b"hello").hexdigest()
token = secrets.token_urlsafe(24)
print(digest, token)
```

常见坑：哈希不能解密；`random` 不适合安全令牌；密码不能直接用一次 SHA-256，应使用专用密码哈希算法；比较秘密值要避免普通字符串比较的时序泄漏。

自查：哈希摘要适合完整性校验还是保密？为什么令牌必须使用 `secrets`？

练习：实现文件 SHA-256 校验，并生成不可预测的短期重置令牌。

仓库关联：[安全与可观测性](../15-security-observability/README.md)。

