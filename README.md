# Python 学习仓库

这是一个用于学习 Python 编程的练习仓库，按照主题分类整理了各种学习材料。

## 目录结构

### 📁 00-environment - 环境、依赖和项目结构
学习虚拟环境、依赖清单、环境变量配置和 Python 项目入口。

**文件列表：**
- `README.md` - 环境和依赖学习指南
- `config_example.py` - 标准库配置读取示例

### 📁 01-type-system - Python 类型系统
学习 Python 的类型注解、泛型、类型检查等高级特性。

**文件列表：**
- `learn_typing.py` - Python 类型注解基础
- `forward_reference_example.py` - 前向引用示例
- `runtime_vs_type_checking.py` - 运行时 vs 类型检查
- `generic_invariance_explanation.py` - 泛型不变性说明
- `instantiation_demo.py` - 实例化演示
- `type_annotation_usefulness.py` - 类型注解的用途
- `typevar_bound_explanation.py` - TypeVar 边界说明
- `typevar_usage_scenarios.py` - TypeVar 使用场景
- `advanced_typing.py` - 工程常用高级类型示例
- `FORWARD_REFERENCE.md` - 前向引用文档
- `RUNTIME_VS_TYPE_CHECKING.md` - 运行时与类型检查对比文档

### 📁 02-database - 数据库
包含 SQLAlchemy ORM 和 Milvus 向量数据库的学习材料。

**SQLAlchemy 相关：**
- `database.py` - 数据库基础操作
- `sqlalchemy_example.py` - SQLAlchemy 示例
- `sqlalchemy_tutorial.py` - SQLAlchemy 教程
- `SQLALCHEMY_QUICK_REFERENCE.md` - SQLAlchemy 快速参考

**Milvus 相关：**
- `milvus_use.py` - Milvus 基础使用
- `milvus_search.py` - Milvus 搜索示例
- `milvus_add_new_data.py` - 添加新数据到 Milvus
- `use_milvus_with_schema.py` - 使用 Schema 的 Milvus
- `persistence_example.py` - 持久化示例
- `test_persistence.py` - 持久化测试
- `test_duplicate_insert.py` - 重复插入测试
- `MILVUS_SETUP.md` - Milvus 设置指南
- `MILVUS_SCHEMA_EXPLANATION.md` - Milvus Schema 说明
- `MILVUS_PERSISTENCE.md` - Milvus 持久化文档
- `ADD_DATA_GUIDE.md` - 添加数据指南
- `DUPLICATE_INSERT_EXPLANATION.md` - 重复插入说明
- `PERSISTENCE_COMPARISON.md` - 持久化方案对比
- `VOLUMES_EXPLANATION.md` - 卷挂载说明

### 📁 03-python-basics - Python 基础特性
Python 语言的基础概念和特性。

**文件列表：**
- `data_class.py` - 数据类使用
- `decorators.py` - 装饰器与带参数装饰器
- `multiple_dispatch.py` - 多分派函数示例
- `singledispatch.py` - 单分派泛化函数示例
- `self_examples.py` - self 关键字示例
- `slice_explanation.py` - 切片机制详解
- `tuple_equality_explanation.py` - 元组相等性说明
- `tuple_immutability_explanation.py` - 元组不可变性说明
- `standard_library_tour.py` - 标准库常用工具组合示例
- `MULTIPLEDISPATCH.md` - multipledispatch 教程文档
- `SINGLEDISPATCH.md` - singledispatch 教程文档
- `SELF_EXPLANATION.md` - self 关键字文档
- `LINKED_LIST_INITIALIZATION.md` - 链表初始化文档

### 📁 04-api-integration - API 集成
第三方 API 的使用示例。

**文件列表：**
- `openai_demo.py` - OpenAI API 使用示例
- `resilient_api_client.py` - 可测试 API 客户端、重试和错误边界示例

### 📁 05-devops - 容器化和部署
Docker、docker-compose 等容器化相关的配置和数据。

**目录结构：**
- `container/` - 容器相关文件
- `volumes/` - Docker 卷数据
- `milvus_data/` - Milvus 数据文件

### 📁 06-tools-and-tests - 工具和测试
各种工具脚本和测试文件。

**文件列表：**
- `test.py` - 通用测试文件
- `test_import.py` - 导入测试
- `add.py` - 加法工具
- `analyze_md.py` - Markdown 分析工具
- `chunking.py` - 文本分块工具
- `use_chunking.py` - 分块使用示例
- `markdown_retrieval.py` - Markdown 切分与 hybrid 检索评分
- `objectname.md` - 对象命名文档
- `structure_output.json` - 结构输出
- `test.txt` - 测试文本
- `test.yaml` - 测试配置

### 📁 07-deep-learning - 深度学习与 PyTorch
从框架无关的数学基础，进阶到 PyTorch 训练、调试和模型导出。

- `fundamentals/` - 线性代数原理与 NumPy 实践
- `pytorch/notebooks/` - 13 节交互式课程
- `pytorch/common/` - 数据、模型、训练、设备和检查点公共模块
- `pytorch/examples/` - CNN、迁移学习、RNN、Attention、混合精度与导出示例
- `pytorch/tests/` - 核心逻辑和课程结构测试

### 📁 08-frameworks - 通过框架源码学习 Python
包含 Django 和 FastAPI 两个真实框架源码，用来学习 Python 进阶特性和大型项目设计。

**核心文档：**
- `README.md` - 模块入口说明
- `PYTHON_FRAMEWORK_SOURCE_LEARNING.md` - 通过 Django/FastAPI 源码学习 Python 的教程与练习

**学习重点：**
- 装饰器、闭包和路由注册
- URL resolver、注册表和中间件链
- 类型注解、`inspect` 和依赖注入
- descriptor、懒加载配置和 metaclass
- sync/async 边界和资源清理

### 📁 09-networking - 网络请求
学习 Python 标准库 `urllib.request` 的 HTTP 请求模型，并通过 MaaS Claude Messages API 示例理解真实 API 调用。

**文件列表：**
- `README.md` - `urllib.request` 网络请求教程
- `urllib_request_tutorial.py` - 使用环境变量调用 Claude Messages API 的可运行示例

**学习重点：**
- URL、method、headers、body 和 response 的关系
- GET 请求和 POST JSON 请求
- 从环境变量读取 base URL 和 API key
- `HTTPError`、`URLError` 和 timeout 的处理

### 📁 10-error-handle - 错误处理
学习基础异常、自定义异常、错误码、上下文管理器和 SDK 错误边界。

**文件列表：**
- `README.md` - 错误处理学习路径
- `basics.py` - 基础异常处理示例
- `context_manager.py` - 上下文管理器和资源释放
- `sdk_example.py` - SDK 风格异常体系

### 📁 11-concurrency - 并发和异步
学习线程、进程、`asyncio`、队列、超时和 worker pipeline。

**文件列表：**
- `README.md` - 并发学习指南
- `asyncio_pipeline.py` - 异步任务流水线示例

### 📁 12-web-backend - Web 后端开发
学习 FastAPI 后端项目结构、请求模型、响应模型和错误返回。

**文件列表：**
- `README.md` - Web 后端学习指南
- `fastapi_app.py` - 最小 FastAPI 应用示例

### 📁 13-data-science - 数据分析和机器学习基础
学习 pandas 数据清洗、聚合、特征生成和机器学习前置知识。

**文件列表：**
- `README.md` - 数据分析学习指南
- `pandas_workflow.py` - pandas 清洗和聚合示例

### 📁 14-ai-applications - AI 应用工程
学习 LLM API、embedding、RAG、检索、结构化输出和 AI 应用测试。

**文件列表：**
- `README.md` - AI 应用工程学习指南
- `rag_pipeline.py` - 不依赖外部服务的玩具 RAG 示例

### 📁 15-security-observability - 安全和可观测性
学习密钥保护、日志脱敏、输入校验、健康检查和排障信息设计。

**文件列表：**
- `README.md` - 安全和可观测性学习指南
- `logging_security.py` - 日志脱敏和 URL 校验示例

### 📁 16-capstone-project - 综合项目
把 Web API、数据库、检索、LLM、测试和部署串成一个 AI 知识库服务。

**文件列表：**
- `README.md` - 综合项目路线
- `app_skeleton.py` - 标准库版端到端骨架

### 📁 18-c-extensions - C 语言强化 Python 与 CPython 源码
用 C 扩展提升 Python 性能，以及阅读 CPython 解释器源码。

**C 扩展方式：**
- `arithmetic.c` + `ctypes_demo.py` - ctypes 调用 C 共享库
- `mymath_module.c` + `setup_mymath.py` - Python/C API 扩展模块
- `c_extension_demo.py` - C 扩展使用和性能对比
- `cython_example.pyx` + `setup_cython.py` - Cython 加速

**CPython 源码阅读：**
- `CPYTHON_SOURCE_GUIDE.md` - CPython 源码阅读指南
- `object_model.c` - 注释版 PyObject 结构和引用计数
- `list_internals.c` - 注释版 list 内存布局和扩容策略

### 📁 requirements - 依赖清单
按学习方向拆分依赖，避免一开始安装全部重依赖。

**文件列表：**
- `base.txt` - 通用依赖
- `web.txt` - Web 后端依赖
- `data.txt` - 数据分析依赖
- `ai.txt` - AI 和深度学习依赖
- `dev.txt` - 测试和质量工具

## 学习路径建议

1. **环境和项目结构** → 从 `00-environment` 建立依赖、配置和运行入口意识
2. **Python 基础** → 学习 `03-python-basics` 和标准库
3. **类型系统和错误处理** → 学习 `01-type-system` 与 `10-error-handle`
4. **测试、网络和并发** → 学习 `06-tools-and-tests`、`09-networking`、`11-concurrency`
5. **数据库和 Web 后端** → 学习 `02-database`、`12-web-backend`
6. **数据、深度学习和 AI 应用** → 学习 `13-data-science`、`07-deep-learning`、`14-ai-applications`
7. **部署、安全和综合项目** → 学习 `05-devops`、`15-security-observability`、`16-capstone-project`
8. **框架源码** → 通过 `08-frameworks` 阅读 Django/FastAPI 源码，理解大型项目设计
9. **C 扩展与底层** → 通过 `18-c-extensions` 学习 C 扩展和 CPython 源码

## 使用说明

- 每个目录都是独立的学习模块
- `.py` 文件包含可运行的示例代码
- `.md` 文件包含详细的说明文档
- 建议按照文件名和文档说明逐步学习

## 环境要求

- Python 3.9+
- 虚拟环境：`~/.virtualenvs/ML/`
- 相关依赖请查看 `requirements/`

## 贡献

这是个人学习仓库，用于记录 Python 学习过程中的练习和笔记。
