# Python 学习仓库目录结构

```
learn-python/
│
├── README.md                          # 项目主文档
├── LEARNING_GAPS.md                   # 学习缺口矩阵
│
├── requirements/                      # 分主题依赖清单
│   ├── base.txt                       # 通用依赖
│   ├── web.txt                        # Web 后端依赖
│   ├── data.txt                       # 数据分析依赖
│   ├── ai.txt                         # AI 和深度学习依赖
│   └── dev.txt                        # 测试和质量工具
│
├── 00-environment/                    # 环境、依赖和项目结构
│   ├── README.md                      # 环境学习指南
│   └── config_example.py              # 环境变量配置示例
│
├── 01-type-system/                    # Python 类型系统
│   ├── README.md                      # 类型系统学习指南
│   ├── learn_typing.py                # 类型注解基础
│   ├── forward_reference_example.py   # 前向引用示例
│   ├── runtime_vs_type_checking.py    # 运行时 vs 类型检查
│   ├── generic_invariance_explanation.py  # 泛型不变性
│   ├── instantiation_demo.py          # 实例化演示
│   ├── type_annotation_usefulness.py  # 类型注解用途
│   ├── typevar_bound_explanation.py   # TypeVar 边界
│   ├── typevar_usage_scenarios.py     # TypeVar 使用场景
│   ├── advanced_typing.py             # 高级 typing 示例
│   ├── FORWARD_REFERENCE.md           # 前向引用文档
│   └── RUNTIME_VS_TYPE_CHECKING.md    # 运行时类型检查文档
│
├── 02-database/                       # 数据库
│   ├── README.md                      # 数据库学习指南
│   │
│   ├── [SQLAlchemy 相关]
│   ├── database.py                    # 数据库基础
│   ├── sqlalchemy_example.py          # SQLAlchemy 示例
│   ├── sqlalchemy_tutorial.py         # SQLAlchemy 教程
│   ├── SQLALCHEMY_QUICK_REFERENCE.md  # 快速参考
│   │
│   ├── [Milvus 相关]
│   ├── milvus_use.py                  # Milvus 基础使用
│   ├── milvus_search.py               # Milvus 搜索
│   ├── milvus_add_new_data.py         # 添加数据
│   ├── use_milvus_with_schema.py      # 使用 Schema
│   ├── persistence_example.py         # 持久化示例
│   ├── test_persistence.py            # 持久化测试
│   ├── test_duplicate_insert.py       # 重复插入测试
│   ├── MILVUS_SETUP.md                # Milvus 设置
│   ├── MILVUS_SCHEMA_EXPLANATION.md   # Schema 说明
│   ├── MILVUS_PERSISTENCE.md          # 持久化文档
│   ├── ADD_DATA_GUIDE.md              # 添加数据指南
│   ├── DUPLICATE_INSERT_EXPLANATION.md # 重复插入说明
│   ├── PERSISTENCE_COMPARISON.md      # 持久化方案对比
│   ├── VOLUMES_EXPLANATION.md         # 卷挂载说明
│   │
│   └── [数据库文件]
│       ├── example.db                 # 示例数据库
│       ├── tutorial.db                # 教程数据库
│       └── milvus_demo.db             # Milvus 演示数据库
│
├── 03-python-basics/                  # Python 基础
│   ├── README.md                      # 基础特性学习指南
│   ├── data_class.py                  # 数据类
│   ├── decorators.py                  # 装饰器与带参数装饰器
│   ├── multiple_dispatch.py           # 多分派函数
│   ├── singledispatch.py              # 单分派泛化函数
│   ├── MULTIPLEDISPATCH.md            # multipledispatch 文档
│   ├── self_examples.py               # self 关键字示例
│   ├── SINGLEDISPATCH.md              # singledispatch 文档
│   ├── slice_explanation.py           # 切片详解
│   ├── tuple_equality_explanation.py  # 元组相等性
│   ├── tuple_immutability_explanation.py # 元组不可变性
│   ├── standard_library_tour.py       # 标准库工具组合
│   ├── SELF_EXPLANATION.md            # self 文档
│   └── LINKED_LIST_INITIALIZATION.md  # 链表初始化
│
├── 04-api-integration/                # API 集成
│   ├── README.md                      # API 集成指南
│   ├── openai_demo.py                 # OpenAI API 示例
│   └── resilient_api_client.py        # 可测试 API 客户端骨架
│
├── 05-devops/                         # 容器化和部署
│   ├── README.md                      # DevOps 指南
│   ├── docker-compose.yml             # Docker Compose 配置
│   ├── config.yaml                    # 通用配置
│   ├── container/                     # 容器文件
│   ├── volumes/                       # Docker 卷数据
│   └── milvus_data/                   # Milvus 数据
│
├── 06-tools-and-tests/                # 工具和测试
│   ├── README.md                      # 工具和测试指南
│   ├── test.py                        # 通用测试
│   ├── test_import.py                 # 导入测试
│   ├── add.py                         # 加法工具
│   ├── analyze_md.py                  # Markdown 分析
│   ├── chunking.py                    # 文本分块
│   ├── markdown_retrieval.py          # Markdown 检索评分
│   ├── use_chunking.py                # 分块使用示例
│   ├── objectname.md                  # 对象命名文档
│   ├── structure_output.json          # 结构输出
│   ├── test.txt                       # 测试文本
│   └── test.yaml                      # 测试配置
│
├── 07-deep-learning/                  # 深度学习原理与 PyTorch
│   ├── README.md                      # 学习路线入口
│   ├── fundamentals/                  # 框架无关的数学与 NumPy 练习
│   └── pytorch/                       # PyTorch 专属课程
│       ├── notebooks/                 # 13 节交互式课程
│       ├── common/                    # 训练、数据、模型和检查点公共模块
│       ├── examples/                  # 可从终端运行的完整示例
│       ├── tests/                     # 轻量单元与课程结构测试
│       ├── data/                      # 下载的数据集（忽略提交）
│       └── artifacts/                 # 检查点和导出模型（忽略提交）
│
├── 08-frameworks/                     # 通过框架源码学习 Python
│   ├── README.md                      # 框架源码学习入口
│   ├── PYTHON_FRAMEWORK_SOURCE_LEARNING.md # Django/FastAPI 源码教程与练习
│   ├── django/                        # Django 源码
│   └── fastapi/                       # FastAPI 源码
│
├── 09-networking/                     # 网络请求
│   ├── README.md                      # urllib.request 网络请求教程
│   └── urllib_request_tutorial.py     # Claude Messages API 调用示例
│
├── 10-error-handle/                   # 错误处理
│   ├── README.md                      # 错误处理学习路径
│   ├── basics.py                      # 基础异常处理
│   ├── context_manager.py             # 上下文管理器
│   └── sdk_example.py                 # SDK 异常体系
│
├── 11-concurrency/                    # 并发和异步
│   ├── README.md                      # 并发学习指南
│   └── asyncio_pipeline.py            # asyncio worker pipeline
│
├── 12-web-backend/                    # Web 后端开发
│   ├── README.md                      # Web 后端学习指南
│   └── fastapi_app.py                 # FastAPI 示例应用
│
├── 13-data-science/                   # 数据分析和机器学习基础
│   ├── README.md                      # 数据分析学习指南
│   └── pandas_workflow.py             # pandas 工作流
│
├── 14-ai-agents/                      # AI Agent 系统工程
│   ├── README.md                      # 14 课学习路线
│   ├── agent_core/                    # 框架无关教学核心
│   ├── guides/                        # Agent 系统教程
│   ├── examples/                      # 离线与框架示例
│   ├── tests/                         # 行为与课程测试
│   └── rag_pipeline.py                # 玩具 RAG pipeline
│
├── 15-security-observability/         # 安全和可观测性
│   ├── README.md                      # 安全和可观测性指南
│   └── logging_security.py            # 日志脱敏和输入校验
│
└── 16-capstone-project/               # 综合项目
    ├── README.md                      # AI 知识库服务路线
    └── app_skeleton.py                # 标准库版端到端骨架

├── 18-c-extensions/                   # C 强化 Python 与 CPython 源码
│   ├── README.md                      # 学习指南
│   ├── arithmetic.c                   # ctypes 共享库源码
│   ├── ctypes_demo.py                 # ctypes 调用示例
│   ├── mymath_module.c                # C 扩展模块（Python/C API）
│   ├── setup_mymath.py                # C 扩展编译脚本
│   ├── c_extension_demo.py            # C 扩展性能对比
│   ├── cython_example.pyx             # Cython 加速示例
│   ├── setup_cython.py                # Cython 编译脚本
│   ├── CPYTHON_SOURCE_GUIDE.md        # CPython 源码阅读指南
│   ├── object_model.c                 # 注释版 PyObject 结构
│   └── list_internals.c              # 注释版 list 实现
```

## 快速导航

### 按学习主题
- **🔤 类型系统**: `01-type-system/`
- **⚙️ 环境依赖**: `00-environment/`
- **💾 数据库**: `02-database/`
- **🐍 Python 基础**: `03-python-basics/`
- **🔌 API 集成**: `04-api-integration/`
- **🐳 容器化**: `05-devops/`
- **🔧 工具测试**: `06-tools-and-tests/`
- **🧠 深度学习**: `07-deep-learning/`
- **🧩 框架源码**: `08-frameworks/`
- **🔧 C 扩展与源码**: `18-c-extensions/`
- **🌐 网络请求**: `09-networking/`
- **🧯 错误处理**: `10-error-handle/`
- **⚡ 并发异步**: `11-concurrency/`
- **🕸️ Web 后端**: `12-web-backend/`
- **📊 数据分析**: `13-data-science/`
- **🤖 AI Agent**: `14-ai-agents/`
- **🔐 安全观测**: `15-security-observability/`
- **🧱 综合项目**: `16-capstone-project/`

### 按文件类型
- **📝 文档 (*.md)**: 每个目录都有 README.md 和相关文档
- **🐍 代码 (*.py)**: Python 示例和工具脚本
- **⚙️ 配置 (*.yaml, *.yml)**: Docker 和应用配置
- **💾 数据 (*.db)**: SQLite 数据库文件

## 学习路径

### 初学者路径
1. `00-environment/` - 环境、依赖和项目结构
2. `03-python-basics/` - Python 基础特性
3. `01-type-system/` - 类型系统
4. `10-error-handle/` - 错误处理
5. `09-networking/` - HTTP 请求基础

### 进阶路径
1. `01-type-system/` - 高级类型特性
2. `11-concurrency/` - 并发和异步
3. `02-database/` - 数据库和向量数据库
4. `12-web-backend/` - Web 后端
5. `08-frameworks/` - 框架源码与 Python 设计理念

### 项目实践路径
1. 从 `04-api-integration/` 开始集成 API
2. 通过 `09-networking/` 理解 SDK 底层的 HTTP 调用
3. 使用 `02-database/` 和 `14-ai-agents/` 构建 RAG 与 Agent
4. 通过 `12-web-backend/` 暴露服务
5. 用 `06-tools-and-tests/` 测试和优化
6. 通过 `05-devops/` 和 `15-security-observability/` 部署和排障

## 文件统计

- **总目录数**: 17 个主题目录 + 3 个数据目录
- **Python 文件**: 约 60+ 个学习示例文件，另包含 Django/FastAPI 源码中的大量 Python 文件
- **文档文件**: 约 30+ 个学习文档，另包含框架源码自带文档
- **配置文件**: 3 个
- **数据库文件**: 3 个

## 使用建议

1. **每个目录独立**: 可以单独学习任一主题
2. **README 优先**: 先阅读各目录的 README.md
3. **代码可运行**: 所有 .py 文件都可以直接运行
4. **边学边改**: 修改代码参数观察结果
5. **做好笔记**: 在代码中添加自己的注释

## 维护建议

- 新增文件时放入对应主题目录
- 每个新主题创建独立目录
- 保持 README.md 文档更新
- 定期清理临时文件和测试数据
