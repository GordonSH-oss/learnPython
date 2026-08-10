# 标准库：工程与运行时

## `logging`

- [ ] 我知道 logger、handler、formatter 和 level 的职责。
- [ ] 我会使用模块级 logger、参数化日志和异常堆栈。

```python
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger.info("user_id=%s loaded", 42)
```

常见坑：库代码不要随意 `basicConfig`；不要把密码和令牌写入日志；`logger.exception()` 应在异常处理上下文中使用。

自查：为什么日志消息用 `%s` 参数而不是 f-string？如何让不同模块输出不同级别？

练习：为一个 API 请求记录请求 ID、耗时和异常，同时脱敏 Authorization 头。

仓库关联：[安全与可观测性](../15-security-observability/README.md)。

## `argparse` 与 `configparser`

- [ ] 我能为命令行参数设置类型、默认值、必填项和帮助文本。
- [ ] 我知道配置文件、环境变量和命令行参数需要明确优先级。

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=8000)
args = parser.parse_args([])
print(args.port)
```

常见坑：配置值通常先以字符串读入；不要把秘密提交进 INI 文件；参数命名和默认值应保持向后兼容。

自查：配置覆盖优先级如何设计？`parse_args([])` 为什么适合测试解析逻辑？

练习：实现 `--verbose`、`--config` 和端口校验，并为解析函数写测试。

仓库关联：[环境配置示例](../00-environment/config_example.py)。

## `inspect` 与 `importlib`

- [ ] 我知道 `inspect` 用于观察对象，`importlib` 用于动态导入。
- [ ] 我会使用 `signature`、`getsource`（开发环境）和 `import_module`。

```python
import importlib
import inspect

json_module = importlib.import_module("json")
print(inspect.signature(json_module.dumps))
```

常见坑：动态导入会隐藏依赖并增加错误路径；`getsource` 对内置函数、打包代码或优化环境可能不可用；不要把不可信字符串直接当模块名加载。

自查：插件系统为什么需要动态导入？反射代码如何保持可测试？

练习：根据模块名加载一个函数，检查它的签名后再调用。

仓库关联：[模块加载教程](../03-python-basics/module_loading_tutorial.py)。

