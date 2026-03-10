# Python 学习仓库目录结构

```
learn-python/
│
├── README.md                          # 项目主文档
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
│   ├── self_examples.py               # self 关键字示例
│   ├── slice_explanation.py           # 切片详解
│   ├── tuple_equality_explanation.py  # 元组相等性
│   ├── tuple_immutability_explanation.py # 元组不可变性
│   ├── SELF_EXPLANATION.md            # self 文档
│   └── LINKED_LIST_INITIALIZATION.md  # 链表初始化
│
├── 04-api-integration/                # API 集成
│   ├── README.md                      # API 集成指南
│   └── openai_demo.py                 # OpenAI API 示例
│
├── 05-devops/                         # 容器化和部署
│   ├── README.md                      # DevOps 指南
│   ├── docker-compose.yml             # Docker Compose 配置
│   ├── config.yaml                    # 通用配置
│   ├── container/                     # 容器文件
│   ├── volumes/                       # Docker 卷数据
│   └── milvus_data/                   # Milvus 数据
│
└── 06-tools-and-tests/                # 工具和测试
    ├── README.md                      # 工具和测试指南
    ├── test.py                        # 通用测试
    ├── test_import.py                 # 导入测试
    ├── add.py                         # 加法工具
    ├── analyze_md.py                  # Markdown 分析
    ├── chunking.py                    # 文本分块
    ├── use_chunking.py                # 分块使用示例
    ├── objectname.md                  # 对象命名文档
    ├── structure_output.json          # 结构输出
    ├── test.txt                       # 测试文本
    └── test.yaml                      # 测试配置
```

## 快速导航

### 按学习主题
- **🔤 类型系统**: `01-type-system/`
- **💾 数据库**: `02-database/`
- **🐍 Python 基础**: `03-python-basics/`
- **🔌 API 集成**: `04-api-integration/`
- **🐳 容器化**: `05-devops/`
- **🔧 工具测试**: `06-tools-and-tests/`

### 按文件类型
- **📝 文档 (*.md)**: 每个目录都有 README.md 和相关文档
- **🐍 代码 (*.py)**: Python 示例和工具脚本
- **⚙️ 配置 (*.yaml, *.yml)**: Docker 和应用配置
- **💾 数据 (*.db)**: SQLite 数据库文件

## 学习路径

### 初学者路径
1. `03-python-basics/` - Python 基础特性
2. `01-type-system/` - 类型系统
3. `02-database/` - 数据库操作
4. `04-api-integration/` - API 使用

### 进阶路径
1. `01-type-system/` - 高级类型特性
2. `02-database/` - 向量数据库
3. `05-devops/` - 容器化部署

### 项目实践路径
1. 从 `04-api-integration/` 开始集成 API
2. 使用 `02-database/` 存储数据
3. 通过 `05-devops/` 容器化部署
4. 用 `06-tools-and-tests/` 测试和优化

## 文件统计

- **总目录数**: 6 个主题目录 + 3 个数据目录
- **Python 文件**: 约 40+ 个
- **文档文件**: 约 20+ 个
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
