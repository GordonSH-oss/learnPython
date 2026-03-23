# Python 学习仓库

这是一个用于学习 Python 编程的练习仓库，按照主题分类整理了各种学习材料。

## 目录结构

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
- `self_examples.py` - self 关键字示例
- `slice_explanation.py` - 切片机制详解
- `tuple_equality_explanation.py` - 元组相等性说明
- `tuple_immutability_explanation.py` - 元组不可变性说明
- `SELF_EXPLANATION.md` - self 关键字文档
- `LINKED_LIST_INITIALIZATION.md` - 链表初始化文档

### 📁 04-api-integration - API 集成
第三方 API 的使用示例。

**文件列表：**
- `openai_demo.py` - OpenAI API 使用示例

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
- `objectname.md` - 对象命名文档
- `structure_output.json` - 结构输出
- `test.txt` - 测试文本
- `test.yaml` - 测试配置

### 📁 07-deep-learning - PyTorch 深度学习
PyTorch 深度学习从基础到实战的完整教程。

**基础教程：**
- `pytorch_basics.py` - PyTorch 基础入门
- `tensors.py` - 张量操作详解（待添加）
- `autograd.py` - 自动微分机制（待添加）

**神经网络：**
- `neural_networks.py` - 构建神经网络（待添加）
- `training_loop.py` - 训练循环（待添加）
- `datasets_dataloaders.py` - 数据加载（待添加）

**实战项目：**
- `linear_regression.py` - 线性回归（待添加）
- `image_classification.py` - 图像分类（待添加）
- `cnn_mnist.py` - CNN 手写数字识别（待添加）
- `transfer_learning.py` - 迁移学习（待添加）

**文档：**
- `README.md` - 完整的学习指南和资源

## 学习路径建议

1. **Python 基础** → 从 `03-python-basics` 开始
2. **类型系统** → 进入 `01-type-system` 学习高级类型特性
3. **数据库操作** → 学习 `02-database` 中的 SQLAlchemy 和向量数据库
4. **API 集成** → 探索 `04-api-integration` 中的第三方 API
5. **容器化** → 了解 `05-devops` 中的部署知识

## 使用说明

- 每个目录都是独立的学习模块
- `.py` 文件包含可运行的示例代码
- `.md` 文件包含详细的说明文档
- 建议按照文件名和文档说明逐步学习

## 环境要求

- Python 3.9+
- 虚拟环境：`~/.virtualenvs/ML/`
- 相关依赖请查看各模块的具体文件

## 贡献

这是个人学习仓库，用于记录 Python 学习过程中的练习和笔记。
