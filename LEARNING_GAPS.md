# Python 全栈 + AI 学习缺口矩阵

这份矩阵用于判断仓库里已有学习资料覆盖了哪些知识、还缺什么，以及应该补到哪个目录。

## 覆盖状态

| 方向 | 当前状态 | 已有材料 | 后续深化 |
| --- | --- | --- | --- |
| 环境和工程结构 | 已补入口 | `00-environment`、`requirements/` | pyproject、包发布、pre-commit |
| Python 基础 | 已补入口 | `03-python-basics`、`standard_library_tour.py` | 文件 I/O 深入、复制、命名空间专题 |
| 类型系统 | 已补入口 | `01-type-system`、`advanced_typing.py` | `Self`、`ParamSpec`、mypy/pyright 配置 |
| 错误处理 | 已补入口 | `10-error-handle` | 错误码文档生成、API 层错误响应 |
| 网络请求 | 部分覆盖 | `09-networking` | `requests`、`httpx`、分页、流式响应、WebSocket |
| API 集成 | 已补入口 | `04-api-integration`、`resilient_api_client.py` | OpenAI 结构化输出、流式调用、工具调用 |
| 数据库 | 部分覆盖 | `02-database` | SQL 基础、迁移、索引、事务隔离、Redis |
| 测试和工具 | 已补入口 | `06-tools-and-tests`、`markdown_retrieval.py` | pytest fixture、mock、ruff、mypy、CI |
| 并发和异步 | 已补入口 | `11-concurrency` | 线程池、进程池、async HTTP、取消传播 |
| Web 后端 | 已补入口 | `12-web-backend`、`08-frameworks` | 鉴权、数据库会话、后台任务、部署 |
| 数据分析 | 已补入口 | `13-data-science` | 可视化、特征工程、scikit-learn 基线 |
| 深度学习 | 已形成完整路线 | `07-deep-learning` | 可继续增加 Transformer 与生产部署专题 |
| AI Agent 工程 | 已补系统课程 | `14-ai-agents` | 继续扩展真实业务评测集与生产适配器 |
| 安全和可观测性 | 已补入口 | `15-security-observability` | 指标、trace id、健康检查、审计日志 |
| 综合项目 | 已补入口 | `16-capstone-project` | 接入真实 FastAPI、数据库、Milvus 和 LLM |

## 推荐补齐顺序

1. `00-environment`：先统一环境、依赖和项目结构。
2. `06-tools-and-tests`、`10-error-handle`：先让测试和错误边界稳定。
3. `11-concurrency`、`09-networking`：补真实服务开发的 I/O 基础。
4. `12-web-backend`、`02-database`：形成后端应用骨架。
5. `13-data-science`、`07-deep-learning`：补数据和模型训练基础。
6. `14-ai-agents`：把模型、工具、memory、RAG、评测和生产治理连起来。
7. `15-security-observability`、`16-capstone-project`：补生产化和端到端项目。

## 验收标准

- 每个新增主题至少包含一个 `README.md` 和一个可运行 `.py` 示例。
- 需要第三方依赖的示例必须在 `requirements/` 中记录。
- 默认测试不依赖真实网络、真实 API key 或 GPU。
- 根目录 `README.md`、`INDEX.md`、`STRUCTURE.md` 必须能找到新增主题。
