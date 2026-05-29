# Web 后端开发

这个模块把 Python 基础、类型系统、错误处理、网络和数据库连接成一个可运行的 Web 服务学习路径。

## 学习目标

- 理解 Web 请求从 HTTP 到 Python 函数的路径。
- 会设计 REST API 的路由、请求模型、响应模型和错误返回。
- 会用依赖注入管理配置、数据库会话和鉴权。
- 知道本地开发、测试和生产部署的差异。

## 本目录文件

- `fastapi_app.py`：一个最小 FastAPI 应用，包含健康检查、请求模型、内存数据存储和统一错误返回。

## 推荐命令

```bash
python -m pip install -r requirements/web.txt
uvicorn 12-web-backend.fastapi_app:app --reload
```

因为目录名包含连字符，直接用模块路径启动可能不方便。也可以进入目录后运行：

```bash
cd 12-web-backend
uvicorn fastapi_app:app --reload
```

## 学习路线

1. 先访问 `/health`，确认服务启动。
2. 用 `POST /notes` 创建一条 note。
3. 用 `GET /notes/{note_id}` 查询。
4. 故意查询不存在的 ID，观察 404 的错误结构。
5. 后续把内存字典替换成 SQLAlchemy 数据库。

## 练习

1. 给 note 增加 `tags: list[str]`。
2. 增加 `GET /notes`，支持按关键字过滤。
3. 把内存存储抽象成 `NoteRepository`，再写单元测试。
