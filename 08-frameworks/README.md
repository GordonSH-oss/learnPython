# 08-frameworks - 通过框架源码学习 Python

这个目录包含两个真实 Python Web 框架源码：

- `django/`：Django 6.1 alpha 源码
- `fastapi/`：FastAPI 0.136.1 源码

这里的学习目标不是“会用 Django 或 FastAPI 写接口”，而是通过阅读框架源码理解 Python 的语言能力和大型项目设计方式。

## 从哪里开始

先读：

- `PYTHON_FRAMEWORK_SOURCE_LEARNING.md`：完整教程、源码阅读路线和练习
- `../playground4.py`：一个极简 `MiniFlask`，适合作为理解路由装饰器的入口

建议顺序：

1. 从 `playground4.py` 的 `self.routes` 和 `@app.route()` 开始，理解“装饰器注册函数”的最小模型。
2. 对照 FastAPI 的 `app.get()`、`api_route()`、`APIRoute`，看真实框架如何扩展这个模型。
3. 对照 Django 的 `path()`、`RoutePattern`、`URLResolver`，看另一种路由解析设计。
4. 继续阅读请求生命周期、依赖注入、懒加载配置、描述符、元类和异步边界。

## 你会学到的 Python 知识

- 装饰器、闭包、高阶函数和 callable 对象
- `inspect.signature()`、`typing.Annotated`、运行时类型解析
- dataclass、Enum、sentinel 默认值和缓存 key
- descriptor 协议、`cached_property`、`__getattr__`、`__setattr__`
- metaclass、类创建过程、动态属性注入
- 中间件链、递归解析、注册表、懒加载
- `async def`、协程检测、线程池桥接和 `AsyncExitStack`

## 使用建议

这个目录的源码量很大，不建议按文件树从头读。每次只围绕一个问题阅读一条调用链，例如：

- `@app.get("/users/{id}")` 最终把什么对象放进了哪里？
- Django 的 `path("users/<int:pk>/", view)` 如何变成可匹配的正则？
- FastAPI 为什么能从函数参数类型自动推断 query、path、body 和 dependency？
- Django 模型为什么只写字段声明，就能获得 `_meta`、管理器和异常类？

这些问题的详细路线和练习都在 `PYTHON_FRAMEWORK_SOURCE_LEARNING.md`。
