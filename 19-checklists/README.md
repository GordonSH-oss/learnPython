# Python 库自查与复习清单

本目录面向已经掌握 Python 基础语法、希望系统复习常用库的学习者。清单以 Python 3.10+ 为基线，示例优先采用仓库 `requirements/` 中声明的第三方库版本。

## 使用方法

每次选择一个主题，按以下顺序复习：

1. 不看示例，先回答“用途”和“自查问题”。
2. 给能独立写出的项目勾选 `[x]`；只能看懂但写不出的项目仍保留 `[ ]`。
3. 运行或手写最小示例，再完成小练习。
4. 一周后重新回答自查问题；能够解释取舍和常见坑才算掌握。

建议状态约定：`[ ]` 未掌握、`[x]` 已掌握、`[~]` 需要复习。Markdown 不原生支持 `[~]`，但可作为个人标记使用。

## 清单索引

### Python 标准库

| 顺序 | 主题 | 主要模块 |
| --- | --- | --- |
| 1 | [基础与数据结构](stdlib-data-structures.md) | `collections`、`enum`、`dataclasses`、`typing`、`copy` |
| 2 | [函数式与迭代](stdlib-functional-iteration.md) | `itertools`、`functools`、`operator` |
| 3 | [文件与系统](stdlib-files-system.md) | `pathlib`、`os`、`sys`、`shutil`、`tempfile`、`subprocess` |
| 4 | [数据与文本](stdlib-data-text.md) | `json`、`csv`、`re`、`string`、`sqlite3` |
| 5 | [时间与数学](stdlib-time-math.md) | `datetime`、`time`、`zoneinfo`、`math`、`decimal`、`statistics`、`random` |
| 6 | [工程与运行时](stdlib-engineering-runtime.md) | `logging`、`argparse`、`configparser`、`inspect`、`importlib` |
| 7 | [并发与网络](stdlib-concurrency-network.md) | `threading`、`multiprocessing`、`concurrent.futures`、`asyncio`、`urllib`、`http` |
| 8 | [测试、安全与资源管理](stdlib-testing-security.md) | `unittest`、`unittest.mock`、`contextlib`、`hashlib`、`secrets` |

### 常用第三方库

| 顺序 | 主题 | 主要库 |
| --- | --- | --- |
| 9 | [工程与质量](third-party-quality.md) | `pytest`、`mypy` |
| 10 | [HTTP 与数据校验](third-party-http-validation.md) | `requests`、`httpx`、Pydantic |
| 11 | [数据库与 Web](third-party-database-web.md) | SQLAlchemy、FastAPI、Django |
| 12 | [数据科学](third-party-data-science.md) | NumPy、pandas、Matplotlib、scikit-learn |
| 13 | [AI](third-party-ai.md) | PyTorch、OpenAI Python SDK、LangGraph |

## 推荐复习路径

- **基础路径**：基础与数据结构 -> 函数式与迭代 -> 文件与系统 -> 数据与文本 -> 时间与数学。
- **工程路径**：工程与运行时 -> 测试、安全与资源管理 -> 工程与质量。
- **后端路径**：并发与网络 -> HTTP 与数据校验 -> 数据库与 Web。
- **数据路径**：数据与文本 -> 时间与数学 -> 数据科学。
- **AI 路径**：HTTP 与数据校验 -> 数据科学 -> AI。

## 选型速记

| 场景 | 优先选择 | 原因 |
| --- | --- | --- |
| 新代码处理路径 | `pathlib` | 面向对象、可组合、跨平台语义清晰 |
| 兼容旧 API 或底层环境变量 | `os` / `os.path` | 生态兼容面广，系统接口更完整 |
| 简单同步 HTTP | `requests` | API 直观、资料丰富 |
| 同时需要同步和异步 HTTP | `httpx` | 提供 `Client` 与 `AsyncClient`，接口接近 |
| I/O 密集并发 | 线程或 `asyncio` | 等待期间可以执行其他任务 |
| CPU 密集并行 | 多进程 | 绕开 CPython GIL，实现多核并行 |
| 标准库测试框架 | `unittest` | 无第三方依赖、类式组织 |
| 常规项目测试 | `pytest` | fixture、参数化和断言体验更简洁 |
| API 服务 | FastAPI | 类型驱动、异步友好、自动生成 OpenAPI |
| 完整后台系统 | Django | ORM、管理后台、认证等能力完整 |

## 仓库入口

- [Python 基础](../03-python-basics/README.md)
- [类型系统](../01-type-system/README.md)
- [数据库](../02-database/README.md)
- [工具与测试](../06-tools-and-tests/README.md)
- [并发与异步](../11-concurrency/README.md)
- [数据科学](../13-data-science/README.md)
- [AI Agent](../14-ai-agents/README.md)

