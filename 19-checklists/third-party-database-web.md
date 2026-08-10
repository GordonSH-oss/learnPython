# 第三方库：数据库与 Web

## SQLAlchemy

- [ ] 我能区分 Core、ORM、Engine、Connection、Session 和事务。
- [ ] 我会使用声明式模型、查询、参数绑定、提交、回滚和关闭 Session。

安装：`python -m pip install sqlalchemy`（仓库基线 `sqlalchemy>=2.0`）。

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite+pysqlite:///:memory:")
with engine.begin() as conn:
    conn.execute(text("create table users (id integer, name text)"))
    conn.execute(text("insert into users values (:id, :name)"), {"id": 1, "name": "Ada"})
```

常见坑：Session 不是全局共享对象；提交边界要明确；懒加载可能造成 N+1 查询；迁移应使用 Alembic 而不是启动时随意改表。

自查：Engine 与 Session 的生命周期分别是什么？ORM 查询如何避免 N+1？

练习：为用户表写 ORM 模型、分页查询和事务失败回滚测试。

仓库关联：[SQLAlchemy Core](../02-database/guides/04-sqlalchemy-core.md)、[ORM](../02-database/guides/05-sqlalchemy-orm.md)。

## FastAPI

- [ ] 我知道路由、依赖、请求模型、响应模型和 OpenAPI 的关系。
- [ ] 我会使用 `FastAPI`、路径操作、Pydantic 模型、`Depends` 和状态码。

安装：`python -m pip install "fastapi[standard]"`（仓库基线 `fastapi>=0.110`）。

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str

@app.post("/items", response_model=Item)
async def create_item(item: Item) -> Item:
    return item
```

常见坑：阻塞函数不要直接放在异步路径中；响应模型会过滤输出字段；依赖对象的生命周期要与请求范围匹配。

自查：请求校验发生在哪里？`Depends` 如何改善测试和资源管理？

练习：为仓库中的 FastAPI 应用添加校验失败响应、依赖注入的数据库 Session 和测试客户端。

仓库关联：[FastAPI 示例](../12-web-backend/fastapi_app.py)、[框架学习](../08-frameworks/PYTHON_FRAMEWORK_SOURCE_LEARNING.md)。

## Django

- [ ] 我知道 Django 的 URL、View、Model、Template 和 Middleware 请求链。
- [ ] 我会定位 settings、迁移、ORM 查询、表单/序列化和管理后台入口。

安装：本仓库包含 Django 源码学习目录；具体项目依赖以 `08-frameworks/django-projects/` 配置为准。

```python
from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok"})
```

常见坑：不要在请求中执行未分页的大查询；迁移文件属于版本控制；中间件顺序会影响认证、事务和异常处理；CSRF 和权限不能省略。

自查：一次请求如何穿过 Middleware 到 View？Django ORM 查询何时真正执行？

练习：在现有 Django 项目中增加健康检查 URL，写一个 ORM 查询并为它添加测试。

仓库关联：[Django/FastAPI 源码学习](../08-frameworks/PYTHON_FRAMEWORK_SOURCE_LEARNING.md)。

