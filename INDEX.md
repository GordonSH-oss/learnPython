# 快速查找索引

这是一个快速查找文件的索引，按主题和常见问题组织。第三方框架源码目录只列入口，不展开全部源码文件。

## 入口文件

- `README.md` - 仓库总览和学习路径
- `STRUCTURE.md` - 目录结构说明
- `LEARNING_GAPS.md` - Python 全栈 + AI 学习缺口矩阵
- `requirements/` - 分主题依赖清单

## 按主题查找

### 环境和依赖
```
00-environment/
├── README.md
└── config_example.py

requirements/
├── base.txt
├── web.txt
├── data.txt
├── ai.txt
└── dev.txt
```

### 类型系统
```
01-type-system/
├── learn_typing.py
├── type_annotation_usefulness.py
├── forward_reference_example.py
├── runtime_vs_type_checking.py
├── generic_invariance_explanation.py
├── typevar_bound_explanation.py
├── typevar_usage_scenarios.py
└── advanced_typing.py
```

### 数据库
```
02-database/
├── SQLAlchemy: database.py, sqlalchemy_example.py, sqlalchemy_tutorial.py
├── Milvus: milvus_use.py, milvus_search.py, milvus_add_new_data.py, use_milvus_with_schema.py
└── 测试: test_duplicate_insert.py, test_persistence.py
```

### Python 基础
```
03-python-basics/
├── OOP: self_examples.py, polymorphism.py, decorators.py
├── 函数和分派: args_and_kwargs.py, singledispatch.py, multiple_dispatch.py
├── 数据模型: data_class.py, slice_explanation.py, special-methods/
├── 迭代和生成器: generator-comprehension/
├── 数据校验: pydantic/
└── 标准库: standard_library_tour.py, bz2_compression.py
```

### API 集成
```
04-api-integration/
├── openai_demo.py
└── resilient_api_client.py
```

### DevOps
```
05-devops/
├── docker-compose.yml
├── config.yaml
└── container/
```

### 工具和测试
```
06-tools-and-tests/
├── add.py
├── analyze_md.py
├── chunking.py
├── markdown_retrieval.py
├── use_chunking.py
├── test.py
└── test_import.py
```

### 深度学习
```
07-deep-learning/
├── fundamentals/    # 框架无关的线性代数与 NumPy 练习
└── pytorch/
    ├── notebooks/   # 13 节交互式课程
    ├── common/      # 数据、模型、训练、设备和检查点
    ├── examples/    # 终端可运行的完整示例
    └── tests/       # 课程与核心逻辑测试
```

### 框架源码
```
08-frameworks/
├── README.md
├── PYTHON_FRAMEWORK_SOURCE_LEARNING.md
├── django/
└── fastapi/
```

### 网络、错误、并发
```
09-networking/
├── README.md
└── urllib_request_tutorial.py

10-error-handle/
├── README.md
├── basics.py
├── context_manager.py
└── sdk_example.py

11-concurrency/
├── README.md
└── asyncio_pipeline.py
```

### 全栈 + AI
```
12-web-backend/
├── README.md
└── fastapi_app.py

13-data-science/
├── README.md
└── pandas_workflow.py

14-ai-applications/
├── README.md
└── rag_pipeline.py

15-security-observability/
├── README.md
└── logging_security.py

16-capstone-project/
├── README.md
└── app_skeleton.py
```

## 常见搜索

**Q: 从哪里开始补齐 Python 学习路线？**  
A: 先看 `LEARNING_GAPS.md`，再从 `00-environment/README.md` 开始。

**Q: 在哪学习类型注解？**  
A: `01-type-system/learn_typing.py`、`01-type-system/type_annotation_usefulness.py`、`01-type-system/advanced_typing.py`。

**Q: 如何使用 SQLAlchemy？**  
A: `02-database/sqlalchemy_tutorial.py` 和 `02-database/SQLALCHEMY_QUICK_REFERENCE.md`。

**Q: Milvus 怎么用？**  
A: 从 `02-database/MILVUS_SETUP.md` 开始，然后看 `02-database/milvus_use.py`。

**Q: self、装饰器、多态在哪里？**  
A: `03-python-basics/SELF_EXPLANATION.md`、`03-python-basics/decorators.py`、`03-python-basics/polymorphism.py`。

**Q: 如何写带重试和错误边界的 API 客户端？**  
A: `04-api-integration/resilient_api_client.py`。

**Q: 如何不用 SDK，直接用 Python 标准库发送 HTTP 请求？**  
A: `09-networking/README.md` 和 `09-networking/urllib_request_tutorial.py`。

**Q: 如何处理异常和自定义错误码？**  
A: `10-error-handle/README.md` 和 `10-error-handle/sdk_example.py`。

**Q: 如何学习 asyncio 并发？**  
A: `11-concurrency/asyncio_pipeline.py`。

**Q: 如何从零搭一个 FastAPI 后端？**  
A: `12-web-backend/README.md` 和 `12-web-backend/fastapi_app.py`。

**Q: 如何做 pandas 数据清洗？**  
A: `13-data-science/pandas_workflow.py`。

**Q: 如何理解 RAG 的基本数据流？**  
A: `14-ai-applications/rag_pipeline.py`。

**Q: 如何学习日志脱敏和输入校验？**  
A: `15-security-observability/logging_security.py`。

**Q: 如何做端到端综合项目？**  
A: `16-capstone-project/README.md` 和 `16-capstone-project/app_skeleton.py`。

**Q: 如何通过 Django 和 FastAPI 源码学习 Python 进阶知识？**  
A: `08-frameworks/PYTHON_FRAMEWORK_SOURCE_LEARNING.md`。
