# 通过 Django 和 FastAPI 源码学习 Python：教程与练习

## 学习目标

这份教程把 `08-frameworks/django` 和 `08-frameworks/fastapi` 当作 Python 进阶教材，而不是只把它们当作 Web 框架使用手册。

学完以后，你应该能解释这些问题：

- 为什么 `@app.route("/users")`、`@app.get("/users")` 这种语法可以把函数注册到框架里？
- 框架如何把一个 URL 字符串变成“应该调用哪个函数，以及传什么参数”？
- FastAPI 如何从函数签名、类型注解和默认值推断请求参数、依赖和响应模型？
- Django 为什么能用 `class User(models.Model): name = models.CharField(...)` 这种声明式写法生成大量运行时行为？
- 中间件、依赖注入、懒加载配置、描述符、元类和 async 边界分别解决了什么设计问题？

## 源码范围

重点阅读这些文件。下表路径均相对 `08-frameworks/`：

| 主题 | Django 源码 | FastAPI 源码 | Python 知识 |
| --- | --- | --- | --- |
| 路由注册 | `django/django/urls/conf.py` | `fastapi/fastapi/applications.py`, `fastapi/fastapi/routing.py` | 装饰器、闭包、`functools.partial` |
| URL 匹配 | `django/django/urls/resolvers.py` | `fastapi/fastapi/routing.py` | 正则、缓存、对象建模 |
| 请求生命周期 | `django/django/core/handlers/base.py` | `fastapi/fastapi/routing.py` | 高阶函数、中间件链、异常流 |
| 类型驱动 API | 不作为主线 | `fastapi/fastapi/dependencies/utils.py`, `fastapi/fastapi/params.py` | `inspect`、`Annotated`、dataclass |
| 依赖注入 | 不作为主线 | `fastapi/fastapi/dependencies/models.py`, `fastapi/fastapi/dependencies/utils.py` | 递归、缓存、上下文管理器 |
| 懒加载配置 | `django/django/conf/__init__.py` | 部分配置在 `FastAPI.__init__` | `__getattr__`、代理对象 |
| 应用注册表 | `django/django/apps/registry.py` | `APIRouter.routes` | registry、幂等初始化、线程锁 |
| 描述符 | `django/django/utils/functional.py`, `django/django/db/models/fields/related_descriptors.py` | 少量使用 | descriptor、属性访问控制 |
| ORM 元类 | `django/django/db/models/base.py` | 不作为主线 | metaclass、动态类构造 |
| 类视图 | `django/django/views/generic/base.py` | class endpoint 间接支持 | method dispatch、类方法 |

源码版本：

- Django：`django/django/__init__.py` 中的 `VERSION = (6, 1, 0, "alpha", 0)`
- FastAPI：`fastapi/fastapi/__init__.py` 中的 `__version__ = "0.136.1"`

## 学习方法

每一课都按这个节奏学习：

1. 先看可见行为：用户写什么代码。
2. 再追执行路径：这个 API 最终调用了哪些函数。
3. 最后抽象 Python 知识：框架为什么这样设计，换成小代码怎么实现。

推荐命令：

```bash
python playground4.py
rg -n "class APIRoute|def add_api_route|def api_route|def get\\(" 08-frameworks/fastapi/fastapi
rg -n "class URLPattern|class URLResolver|def resolve\\(" 08-frameworks/django/django/urls
rg -n "def get_dependant|def analyze_param|async def solve_dependencies" 08-frameworks/fastapi/fastapi/dependencies
rg -n "class ModelBase|def add_to_class|class Model\\(" 08-frameworks/django/django/db/models/base.py
```

## 第 0 课：从 `MiniFlask` 理解路由注册

先看 `playground4.py`：

```python
class MiniFlask:
    def __init__(self):
        self.routes = {}

    def route(self, path):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator
```

这段代码展示了 Web 框架路由系统的最小模型：

- `self.routes` 是注册表，保存“路径到处理函数”的映射。
- `route(path)` 不直接处理请求，而是返回一个装饰器。
- `decorator(func)` 在函数定义阶段运行，把函数放进注册表。
- `return func` 保留原函数，避免装饰器破坏后续调用和调试信息。

可见行为：

```python
@app.route("/users")
def users():
    return "user list"
```

等价于：

```python
def users():
    return "user list"

users = app.route("/users")(users)
```

### 你要掌握的 Python 知识

- 函数是一等对象，可以存入 dict。
- 装饰器本质是“接收函数、返回函数”的函数。
- 带参数装饰器多一层闭包：`route(path)` 保存 `path`，`decorator(func)` 保存 `func`。
- `self.routes` 是对象状态，不是全局变量，多个 app 可以有自己的路由表。

### 练习 0

修改 `playground4.py`，完成这些小任务：

1. 让 `self.routes` 的 key 从 `path` 变成 `(method, path)`，支持 `GET /users` 和 `POST /users` 指向不同函数。
2. 在 `handle()` 中打印即将调用的函数名：`handler.__name__`。
3. 思考：如果 `decorator()` 不 `return func`，`users` 变量会变成什么？

验收标准：

- `app.handle("GET", "/users")` 和 `app.handle("POST", "/users")` 能返回不同结果。
- 你能说清楚装饰器是在“函数定义时”注册，而不是请求到达时注册。

## 第 1 课：FastAPI 如何把 `@app.get()` 扩展成真实路由系统

从用户代码开始：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
def read_user(user_id: int):
    return {"user_id": user_id}
```

追源码路径：

1. `fastapi/fastapi/applications.py`：`FastAPI.get()` 返回一个装饰器。
2. `FastAPI.api_route()` 或 `FastAPI.get()` 内部调用 `self.router.add_api_route(...)`。
3. `fastapi/fastapi/routing.py`：`APIRouter.add_api_route()` 创建 `APIRoute` 对象。
4. `APIRoute.__init__()` 保存 endpoint、HTTP method、path、response model、dependency 信息。
5. `APIRouter.routes.append(route)` 把路由对象放入注册表。

这和 `MiniFlask` 的关系：

| MiniFlask | FastAPI |
| --- | --- |
| `self.routes = {}` | `APIRouter.routes = []` |
| key 是 path 字符串 | `APIRoute` 对象保存 path、method、schema、依赖等 |
| value 是函数 | `endpoint` 是函数，外加大量元数据 |
| `handle()` 手动查 dict | Starlette/FastAPI 根据 ASGI scope 匹配 route |

### 你要掌握的 Python 知识

- 装饰器可以注册的不只是函数本身，还可以构造一个“描述这个函数的对象”。
- list 注册表比 dict 更灵活，因为真实路由需要按顺序匹配、支持 mount、websocket、子路由。
- 函数对象可以携带注解、文档字符串、模块信息，框架会用 `inspect` 读取它们。
- FastAPI 使用继承和组合：`FastAPI` 继承 Starlette，真正路由管理委托给 `self.router`。

### 设计理念

FastAPI 的装饰器不是为了“包装函数并改变函数行为”，而是为了“在应用启动阶段收集元数据”。这是声明式 API 的核心：用户写起来像声明，框架在运行时把声明变成可执行结构。

### 练习 1

基于 `playground4.py` 写一个 `MiniFastAPI`：

```python
class Route:
    def __init__(self, path, endpoint, methods):
        self.path = path
        self.endpoint = endpoint
        self.methods = set(methods)

class MiniFastAPI:
    def __init__(self):
        self.routes = []
```

要求：

1. 实现 `add_api_route(path, endpoint, methods)`。
2. 实现 `api_route(path, methods)`，返回装饰器。
3. 实现 `get(path)`，内部调用 `api_route(path, ["GET"])`。
4. 打印 `app.routes`，确认里面保存的是 `Route` 对象，不是简单字符串。

思考题：

- 为什么真实框架要保存 route 对象，而不是只保存 path 到 function 的 dict？
- 如果两个路由都能匹配同一个 URL，list 顺序会造成什么影响？

## 第 2 课：Django 如何把 `path()` 变成 URL 解析器

用户代码通常长这样：

```python
from django.urls import path

urlpatterns = [
    path("users/<int:pk>/", user_detail, name="user-detail"),
]
```

追源码路径：

1. `django/django/urls/conf.py` 中的 `path = partial(_path, Pattern=RoutePattern)`。
2. `_path()` 判断 `view` 是 callable 还是 include 结果。
3. 普通 view 会创建 `RoutePattern(route, is_endpoint=True)`。
4. `_path()` 返回 `URLPattern(pattern, view, kwargs, name)`。
5. 请求到来时，`URLResolver.resolve()` 遍历 `url_patterns`，调用每个 pattern 的 `resolve()`。
6. `RoutePattern.match()` 把 URL 中捕获的参数转换为 Python 值，例如 `<int:pk>` 转成 `int`。

重点文件：

- `django/django/urls/conf.py`
- `django/django/urls/resolvers.py`
- `django/django/urls/converters.py`

### 你要掌握的 Python 知识

- `functools.partial` 可以预先固定函数参数，`path()` 和 `re_path()` 因此共用 `_path()`。
- `_route_to_regex()` 用正则解析 `<converter:name>` 语法。
- `functools.lru_cache` 缓存路由字符串到正则的转换结果。
- `RoutePattern.regex` 是 descriptor，根据当前语言环境缓存编译后的正则。
- `Resolver404` 这种异常既表示失败，也携带失败路径和尝试过的 pattern，用于调试。

### 设计理念

Django 的路由更偏“显式配置”。用户把所有 URL 模式放在 `urlpatterns` 里，框架把这个列表转换成一棵 resolver 树。这个设计适合大型项目分模块组织 URL，也适合反向解析 URL name。

### 练习 2

实现一个最小版 `route_to_regex(route)`：

输入：

```python
"users/<int:pk>/posts/<slug:slug>/"
```

输出：

```python
r"^users/(?P<pk>[0-9]+)/posts/(?P<slug>[-a-zA-Z0-9_]+)/"
```

要求：

1. 支持 `str`、`int`、`slug` 三种 converter。
2. 检查参数名必须是合法 Python 标识符：`parameter.isidentifier()`。
3. 用 `functools.lru_cache` 缓存转换结果。
4. 写 3 个断言测试：正常匹配、非法 converter、非法参数名。

思考题：

- Django 为什么要把 URL 参数名限制成合法 Python 标识符？
- 如果 converter 的 `to_python()` 抛出 `ValueError`，为什么应该视为“不匹配”而不是 500 错误？

## 第 3 课：请求生命周期和中间件链

Django 的同步请求核心在 `django/django/core/handlers/base.py`：

1. `BaseHandler.load_middleware()` 从 `settings.MIDDLEWARE` 读取中间件路径。
2. 它从后往前包裹 handler，形成一条调用链。
3. `get_response()` 设置 URLconf，然后调用 `_middleware_chain(request)`。
4. `_get_response()` 调用 `resolve_request()` 找到 view。
5. 依次执行 view middleware、view、exception middleware、template response middleware。

FastAPI 的请求核心在 `fastapi/fastapi/routing.py`：

1. `APIRoute.__init__()` 调用 `self.app = request_response(self.get_route_handler())`。
2. `request_response()` 把一个 `request -> response` 函数转换成 ASGI app。
3. `get_request_handler()` 创建真正处理请求的 async 函数。
4. 它读取 body，执行 `solve_dependencies()`，调用 endpoint，序列化 response。

### 你要掌握的 Python 知识

- 中间件链本质是高阶函数：一个 callable 接收下一个 callable，返回新的 callable。
- Django 用 `import_string()` 从字符串导入类，这是插件机制的基础。
- 同步/异步边界需要显式适配：Django 使用 `sync_to_async()` 和 `async_to_sync()`。
- FastAPI 使用 `AsyncExitStack` 管理请求级和函数级资源清理。
- 异常是控制流的一部分，框架在边界处把异常转换成响应。

### 设计理念

中间件让“横切逻辑”独立于业务处理函数，例如认证、日志、压缩、异常处理。核心设计问题是：谁拥有调用链，谁负责异常转换，谁负责资源清理。

### 练习 3

写一个最小中间件链：

```python
def app(request):
    return f"response for {request}"

def logging_middleware(get_response):
    def wrapper(request):
        print("before")
        response = get_response(request)
        print("after")
        return response
    return wrapper
```

要求：

1. 再写一个 `auth_middleware`，当 request 不等于 `"ok"` 时返回 `"401"`。
2. 实现 `build_chain(app, [logging_middleware, auth_middleware])`。
3. 预测并验证 `before/after` 的打印顺序。
4. 思考：中间件顺序为什么通常要反向包裹？

进阶：

用 `contextlib.ExitStack` 或 `contextlib.AsyncExitStack` 模拟 FastAPI 的 yield dependency 清理过程。

## 第 4 课：FastAPI 的类型驱动参数解析

FastAPI 最值得学习的 Python 特性在 `fastapi/fastapi/dependencies/utils.py` 和 `fastapi/fastapi/params.py`。

用户代码：

```python
from typing import Annotated
from fastapi import Depends, Query

def get_token(token: str):
    return token

@app.get("/items/{item_id}")
def read_item(
    item_id: int,
    q: Annotated[str | None, Query(max_length=50)] = None,
    token: str = Depends(get_token),
):
    return {"item_id": item_id, "q": q, "token": token}
```

追源码路径：

1. `APIRoute.__init__()` 调用 `get_dependant(path=self.path_format, call=self.endpoint, scope="function")`。
2. `get_dependant()` 调用 `get_typed_signature(call)`。
3. `get_typed_signature()` 使用 `inspect.signature()` 读取函数参数。
4. 每个参数交给 `analyze_param()`。
5. `analyze_param()` 识别 `Annotated`、`Depends`、`Query`、`Path`、`Body` 等信息。
6. 结果被放进 `Dependant.path_params`、`query_params`、`body_params`、`dependencies`。

### 你要掌握的 Python 知识

- 类型注解在运行时可以读取，但不会自动校验值。
- `inspect.Signature` 和 `inspect.Parameter` 是函数签名的结构化表示。
- `typing.Annotated[T, metadata]` 可以把类型和框架元数据绑定在一起。
- 默认值也可以承载框架语义，例如 `token: str = Depends(get_token)`。
- sentinel 对象用于区分“用户没有传值”和“用户传了 None”。
- `dataclass` 适合表达中间结果，例如 `ParamDetails` 和 `Dependant`。

### 设计理念

FastAPI 把 Python 函数签名当作 API schema 的来源。函数签名同时服务于：

- 请求参数提取
- 数据校验
- 依赖注入
- OpenAPI 文档生成
- 响应序列化

这是一种“类型和运行时协议结合”的设计。

### 练习 4

实现一个 `inspect_endpoint(func, path)`：

```python
def endpoint(user_id: int, q: str | None = None, limit: int = 10):
    pass
```

要求输出类似：

```python
{
    "path": ["user_id"],
    "query": ["q", "limit"],
}
```

步骤：

1. 用 `inspect.signature(func)` 读取参数。
2. 从 path 字符串 `"/users/{user_id}"` 中提取 path 参数名。
3. 如果参数名在 path 里，归类为 path。
4. 否则归类为 query。
5. 打印每个参数的 annotation 和 default。

进阶：

支持一个自定义 `Depends` 类：

```python
class Depends:
    def __init__(self, dependency):
        self.dependency = dependency
```

让默认值是 `Depends(...)` 的参数进入 `"dependencies"` 分类。

## 第 5 课：FastAPI 的依赖注入图

重点文件：

- `fastapi/fastapi/dependencies/models.py`
- `fastapi/fastapi/dependencies/utils.py`

`Dependant` 是 FastAPI 内部依赖图的节点。它保存：

- 当前要调用的函数：`call`
- 当前函数需要的 path/query/header/cookie/body 参数
- 子依赖：`dependencies`
- 是否使用缓存：`use_cache`
- 依赖作用域：`scope`

`solve_dependencies()` 的核心思路：

1. 遍历当前 `dependant.dependencies`。
2. 递归求解每个子依赖。
3. 如果启用缓存，优先从 `dependency_cache` 取结果。
4. 根据子依赖类型决定如何调用：async、sync、generator、async generator。
5. 把求解结果放入 `values`，最终作为 endpoint 的关键字参数。

### 你要掌握的 Python 知识

- 树和图结构可以用递归求值。
- `cached_property` 可以把代价较高的判断缓存到对象上。
- cache key 需要稳定表达“同一个依赖调用在同一组条件下是否可复用”。
- generator dependency 本质上是上下文管理器：进入时提供值，退出时清理资源。
- async 代码里仍然可能运行 sync 函数，需要线程池隔离阻塞工作。

### 设计理念

依赖注入把“如何获得参数”从 endpoint 里拿出去，让 endpoint 保持业务语义。它的代价是框架内部必须构造和求解一张依赖图。

### 练习 5

写一个迷你依赖注入器：

```python
class Depends:
    def __init__(self, dependency, use_cache=True):
        self.dependency = dependency
        self.use_cache = use_cache
```

要求：

1. 用 `inspect.signature()` 找到默认值为 `Depends` 的参数。
2. 递归调用 dependency。
3. 用 dict 缓存同一个 dependency 的结果。
4. 支持这个例子：

```python
def get_user_id():
    print("load user")
    return 1

def get_user_name(user_id=Depends(get_user_id)):
    return f"user-{user_id}"

def endpoint(name=Depends(get_user_name), user_id=Depends(get_user_id)):
    return name, user_id
```

验收标准：

- `get_user_id()` 在一次 endpoint 调用中只打印一次。
- 你能说明缓存应该是“每次请求级别”，不应该是全局永久缓存。

## 第 6 课：Django 的懒加载配置和应用注册表

重点文件：

- `django/django/conf/__init__.py`
- `django/django/apps/registry.py`
- `django/django/__init__.py`

Django 的 `settings` 不是普通对象，而是 `LazySettings`：

1. 初始时 `_wrapped` 是 `empty`。
2. 第一次访问 `settings.SOME_NAME` 时触发 `__getattr__()`。
3. 如果还没配置，`_setup()` 读取 `DJANGO_SETTINGS_MODULE`。
4. 加载后把值写入 `self.__dict__`，后续访问直接命中缓存。

Django 的 app registry 在 `Apps.populate()` 中完成三阶段初始化：

1. 创建 app config 并导入 app 模块。
2. 导入每个 app 的 models 模块。
3. 调用每个 app config 的 `ready()`。

### 你要掌握的 Python 知识

- `__getattr__()` 只在常规属性查找失败时触发，适合做懒加载。
- `__setattr__()` 可以拦截赋值，并清理缓存。
- 线程锁 `RLock` 用于保证初始化幂等且线程安全。
- registry 是大型框架常见基础设施，用于把分散声明收集到全局可查询结构。
- 初始化要防重入：Django 用 `self.loading` 阻止 `populate()` 递归进入。

### 设计理念

Django 允许许多模块直接 `from django.conf import settings`。如果 settings 在 import 阶段立即加载，很容易产生导入顺序和配置时机问题。懒加载让“引用 settings”与“真正读取配置”解耦。

### 练习 6

实现一个 `LazyConfig`：

```python
class LazyConfig:
    def __init__(self, loader):
        self._loader = loader
        self._wrapped = None

    def __getattr__(self, name):
        ...
```

要求：

1. 第一次访问属性时调用 loader。
2. loader 只调用一次。
3. 访问到的属性缓存到实例上。
4. 实现 `configured` 属性。

进阶：

实现一个 `Registry.populate(items)`，要求：

- 调用两次不会重复初始化。
- 初始化过程中再次调用会抛出 `RuntimeError`。
- 用一个标志位模拟 Django 的 `loading`。

## 第 7 课：描述符、`cached_property` 和关系字段访问

重点文件：

- `django/django/utils/functional.py`
- `django/django/urls/resolvers.py`
- `django/django/db/models/fields/related_descriptors.py`

Django 的 `cached_property` 是 descriptor：

```python
class cached_property:
    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res
```

第一次访问时，`__get__()` 计算值并写入 `instance.__dict__`。第二次访问时，普通实例属性会覆盖非 data descriptor，所以不会再次调用 `__get__()`。

Django URL 中的 `LocaleRegexRouteDescriptor` 也是 descriptor。它根据当前语言环境返回不同的编译正则，并缓存到对象上。

ORM 关系字段更复杂。`ForwardManyToOneDescriptor.__get__()` 负责：

- `child.parent` 时返回关联对象。
- 如果缓存里已有对象，直接返回。
- 如果没有缓存但本地外键有值，从数据库加载。
- 加载后写入字段缓存。
- `__set__()` 时同步外键值、检查类型、维护正反向缓存。

### 你要掌握的 Python 知识

- descriptor 是 Python 属性访问协议：`__get__`、`__set__`、`__delete__`。
- class attribute 可以控制 instance attribute 的读取和写入行为。
- data descriptor 和 non-data descriptor 的优先级不同。
- ORM 使用 descriptor 把“属性访问”变成“缓存、校验、数据库查询、关系维护”。

### 设计理念

描述符让框架把复杂行为隐藏在普通属性语法后面。用户写 `child.parent`，看到的是属性访问；框架看到的是一次可拦截、可缓存、可校验的操作。

### 练习 7

实现一个自己的 `cached_property`：

```python
class User:
    def __init__(self, first, last):
        self.first = first
        self.last = last

    @cached_property
    def full_name(self):
        print("compute")
        return f"{self.first} {self.last}"
```

要求：

1. 第一次访问打印 `compute`。
2. 第二次访问不打印。
3. `u.__dict__` 中能看到 `full_name`。
4. 删除 `del u.__dict__["full_name"]` 后，再访问会重新计算。

进阶：

实现一个 `TypedAttribute` descriptor，赋值时检查类型：

```python
class Product:
    price = TypedAttribute(float)
```

## 第 8 课：Django ORM 元类：把类声明变成运行时模型

重点文件：

- `django/django/db/models/base.py`

用户代码：

```python
class User(models.Model):
    name = models.CharField(max_length=50)
```

这不是普通类定义。因为 `Model` 使用 `ModelBase` 作为 metaclass：

```python
class Model(AltersData, metaclass=ModelBase):
    ...
```

类创建时会进入 `ModelBase.__new__()`：

1. 区分普通属性和带 `contribute_to_class()` 的属性。
2. 调用 `type.__new__()` 先创建类对象。
3. 创建 `_meta`，收集 Meta 配置和字段信息。
4. 动态创建 `DoesNotExist`、`MultipleObjectsReturned` 等异常类。
5. 调用 `add_to_class()`，让字段把自己安装到模型类上。
6. 调用 `_prepare()` 做最后准备。
7. 把模型注册到 app registry。

### 你要掌握的 Python 知识

- metaclass 控制“类对象如何被创建”。
- 类体中的属性会先进入 `attrs` dict，再交给 metaclass。
- `type(name, bases, namespace)` 可以动态创建类。
- `__classcell__` 关系到 `super()` 和闭包，需要保留。
- `contribute_to_class()` 是一种扩展点，比简单 `setattr()` 更强。
- 动态异常类让每个 model 都有自己的异常类型。

### 设计理念

Django ORM 的设计是“声明式类定义”。用户写的是业务模型，框架在类创建阶段把字段、元数据、管理器、关系描述符、异常类都装配好。这样运行时实例才可以用自然的 Python 属性语法工作。

### 练习 8

实现一个迷你 ORM 元类：

```python
class Field:
    def contribute_to_class(self, cls, name):
        self.name = name
        cls._fields[name] = self

class ModelMeta(type):
    def __new__(mcls, name, bases, attrs):
        ...

class MiniModel(metaclass=ModelMeta):
    pass
```

要求：

1. 收集所有 `Field` 属性到 `cls._fields`。
2. 从类属性中移除 `Field`，避免实例访问时直接拿到 Field 对象。
3. 给每个 model 动态创建 `DoesNotExist` 异常类。
4. 支持：

```python
class User(MiniModel):
    name = Field()
    age = Field()

assert "name" in User._fields
assert User.DoesNotExist.__name__ == "DoesNotExist"
```

思考题：

- 为什么字段对象不能只是普通类属性？
- 如果父类和子类都有字段，`_fields` 应该共享还是复制？

## 第 9 课：Django class-based view 的方法分派

重点文件：

- `django/django/views/generic/base.py`

用户代码：

```python
class UserView(View):
    def get(self, request):
        ...

urlpatterns = [
    path("users/", UserView.as_view()),
]
```

`View.as_view()` 返回的不是类实例，而是一个函数：

1. `as_view()` 校验传入的初始化参数。
2. 定义内部函数 `view(request, *args, **kwargs)`。
3. 每次请求到来时创建新的 `self = cls(**initkwargs)`。
4. 调用 `self.setup()` 保存 request、args、kwargs。
5. 调用 `self.dispatch()`。
6. `dispatch()` 根据 HTTP method 找到 `get()`、`post()` 等方法。

### 你要掌握的 Python 知识

- 类也可以生成函数，函数闭包里保存类对象 `cls`。
- `getattr(self, method_name, fallback)` 是动态分派的基础。
- 每次请求创建新的 view 实例，可以避免请求间共享实例状态。
- `view.view_class = cls` 这种函数属性可用于调试和 URL resolver 展示。
- `classonlymethod` 和 `classproperty` 是 descriptor 的应用。

### 设计理念

class-based view 用类组织复用逻辑，用函数适配 URL resolver。URL resolver 只需要 callable，不需要知道背后是函数视图还是类视图。

### 练习 9

实现一个 `MiniView.as_view()`：

```python
class MiniView:
    http_method_names = ["get", "post"]

    @classmethod
    def as_view(cls, **initkwargs):
        ...
```

要求：

1. 返回一个函数 `view(request)`。
2. request 可以是 `{"method": "GET"}`。
3. `dispatch()` 根据 method 调用 `get()` 或 `post()`。
4. 不支持的方法返回 `"405"`。
5. 验证每次调用 `view()` 都会创建新实例。

## 第 10 课：同步、异步和资源清理边界

重点文件：

- `django/django/core/handlers/base.py`
- `fastapi/fastapi/routing.py`
- `fastapi/fastapi/dependencies/models.py`
- `fastapi/fastapi/dependencies/utils.py`

Django 同时支持 sync view 和 async view。`BaseHandler.adapt_method_mode()` 根据目标模式决定：

- async handler 中遇到 sync 方法，用 `sync_to_async()` 包装。
- sync handler 中遇到 async 方法，用 `async_to_sync()` 包装。

FastAPI 以 async ASGI app 为核心：

- sync endpoint 会通过 `run_in_threadpool()` 执行。
- async endpoint 会直接 `await`。
- generator dependency 被转换成 context manager。
- `AsyncExitStack` 确保依赖 cleanup 在正确时机执行。

### 你要掌握的 Python 知识

- `async def` 调用后返回 coroutine，必须 `await` 才执行。
- `inspect.iscoroutinefunction()` 可判断函数是否 async。
- 阻塞同步函数不能直接跑在事件循环上。
- 上下文管理器把 acquire/release 绑定在一起。
- `AsyncExitStack` 适合动态管理多个 async context manager。

### 设计理念

框架的 async 支持不是把所有函数都变成 async，而是在边界处做适配。边界包括 middleware、view、dependency、response rendering 和 cleanup。

### 练习 10

写一个 `call_endpoint(func, **values)`：

要求：

1. 如果 `func` 是 async function，则 `await func(**values)`。
2. 如果 `func` 是 sync function，在 async 环境中用 `asyncio.to_thread()` 调用。
3. 写两个 endpoint，一个 sync，一个 async。
4. 打印调用顺序，确认二者都能返回结果。

进阶：

写一个 async context manager 依赖：

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def resource():
    print("open")
    yield "db"
    print("close")
```

用 `AsyncExitStack` 动态进入它，确认 `close` 一定执行。

## Django 与 FastAPI 的设计对照

| 维度 | Django | FastAPI |
| --- | --- | --- |
| API 风格 | 显式配置、约定完整 | 类型驱动、函数签名即 schema |
| 路由 | `urlpatterns` 列表和 resolver 树 | 装饰器注册 `APIRoute` |
| 请求处理 | handler + middleware + resolver + view | ASGI app + route handler + dependency solver |
| 配置 | `LazySettings` 懒加载全局配置 | `FastAPI(...)` 实例参数为主 |
| 扩展点 | middleware、app config、model field、class-based view | dependency、router、response model、middleware |
| Python 高级特性 | descriptor、metaclass、lazy proxy、registry | type hints、inspect、dataclass、async context |
| 适合学习 | 大型框架初始化、ORM、声明式类系统 | 类型注解运行时化、依赖注入、ASGI/async |

不要用“谁更好”理解这两个框架。更好的问题是：

- Django 为什么需要强大的全局 registry 和懒加载配置？
- FastAPI 为什么能把 endpoint 函数签名作为中心抽象？
- 两者如何在用户 API 简洁和内部复杂度之间做取舍？

## 综合练习：写一个 TinyPyAPI

目标：把前 10 课的知识合成一个小框架。

### 功能要求

1. 路由注册：

```python
app = TinyPyAPI()

@app.get("/users/{user_id}")
def read_user(user_id: int, token=Depends(get_token)):
    return {"user_id": user_id, "token": token}
```

2. 路由匹配：

- 支持 `/users/{user_id}`。
- 支持把 `user_id` 转成 `int`。
- 未匹配返回 `"404"`。

3. 依赖注入：

- 支持默认值为 `Depends(func)`。
- 支持依赖递归。
- 同一次请求内缓存依赖结果。

4. 中间件：

- 支持 `app.add_middleware(middleware)`。
- middleware 可以在 endpoint 前后打印日志。

5. descriptor：

- 实现一个 `cached_property`，用于缓存编译后的 route regex。

6. 测试：

- 写 `assert app.handle("GET", "/users/123") == {...}`。
- 测试依赖缓存只执行一次。
- 测试 404。
- 测试 middleware 顺序。

### 推荐文件

可以新建：

```text
08-frameworks/exercises/tiny_pyapi.py
08-frameworks/exercises/test_tiny_pyapi.py
```

### 评分标准

完成后你应该能解释：

- `@app.get()` 在什么时候执行？
- route 对象里保存了哪些元数据？
- path 参数如何从字符串变成 Python 值？
- endpoint 的参数字典是如何拼出来的？
- dependency cache 的生命周期是什么？
- middleware 顺序为什么影响输出？

## 10 天学习安排

| 天数 | 内容 | 产出 |
| --- | --- | --- |
| 第 1 天 | `playground4.py` 和 FastAPI 路由装饰器 | `MiniFastAPI` |
| 第 2 天 | Django `path()` 和 `RoutePattern` | `route_to_regex()` |
| 第 3 天 | Django `URLResolver.resolve()` | URL 匹配追踪笔记 |
| 第 4 天 | Django/FastAPI 请求生命周期 | `build_chain()` |
| 第 5 天 | FastAPI `inspect.signature()` 参数解析 | `inspect_endpoint()` |
| 第 6 天 | FastAPI dependency graph | 迷你依赖注入器 |
| 第 7 天 | Django `LazySettings` 和 `Apps.populate()` | `LazyConfig` 和 `Registry` |
| 第 8 天 | descriptor 和 `cached_property` | 自定义 descriptor |
| 第 9 天 | Django `ModelBase` 元类 | 迷你 ORM 元类 |
| 第 10 天 | 综合项目 | `TinyPyAPI` 和测试 |

## 阅读源码时的检查清单

每读一个框架 API，都回答这 8 个问题：

1. 用户写的最小代码是什么？
2. 入口函数或类在哪里？
3. 它是在注册阶段执行，还是在请求阶段执行？
4. 它把信息保存到了哪个对象或注册表？
5. 哪些信息来自函数对象、类型注解、默认值或类属性？
6. 哪个函数负责把声明转换成可执行调用？
7. 错误会以异常、返回值还是响应对象的方式传播？
8. 哪些结果被缓存，缓存何时失效？

## 常见误区

- 不要从整个 Django 或 FastAPI 文件树顺序阅读。先追一个行为，再展开依赖文件。
- 不要把类型注解理解成 Python 自动校验。FastAPI 是读取注解后主动创建校验模型。
- 不要以为装饰器一定会包装函数。FastAPI 的路由装饰器主要是注册元数据。
- 不要把 `settings` 理解成普通全局变量。Django 的 `settings` 是懒加载代理。
- 不要把 Django model 字段理解成普通实例属性。字段在类创建阶段被 metaclass 和 descriptor 改造成运行时行为。
- 不要忽略 sync/async 适配。真实框架大量复杂性都在边界处理上。

## 推荐下一步

完成综合练习后，可以继续做两类深挖：

1. Django ORM 查询链：读 `django/django/db/models/query.py`，学习 QuerySet 的惰性求值、链式 API、clone 设计。
2. FastAPI OpenAPI 生成：读 `fastapi/fastapi/openapi/utils.py`，学习如何从 route、dependency、Pydantic field 生成 JSON schema。
