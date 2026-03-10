# 快速查找索引

这是一个快速查找文件的索引，按字母顺序排列。

## A

- `add.py` → `06-tools-and-tests/`
- `ADD_DATA_GUIDE.md` → `02-database/`
- `analyze_md.py` → `06-tools-and-tests/`

## C

- `chunking.py` → `06-tools-and-tests/`
- `config.yaml` → `05-devops/`
- `container/` → `05-devops/`

## D

- `data_class.py` → `03-python-basics/`
- `database.py` → `02-database/`
- `docker-compose.yml` → `05-devops/`
- `DUPLICATE_INSERT_EXPLANATION.md` → `02-database/`

## E

- `example.db` → `02-database/`

## F

- `forward_reference_example.py` → `01-type-system/`
- `FORWARD_REFERENCE.md` → `01-type-system/`

## G

- `generic_invariance_explanation.py` → `01-type-system/`

## I

- `instantiation_demo.py` → `01-type-system/`

## L

- `learn_typing.py` → `01-type-system/`
- `LINKED_LIST_INITIALIZATION.md` → `03-python-basics/`

## M

- `milvus_add_new_data.py` → `02-database/`
- `milvus_data/` → `05-devops/`
- `milvus_demo.db` → `02-database/`
- `milvus_search.py` → `02-database/`
- `milvus_use.py` → `02-database/`
- `MILVUS_PERSISTENCE.md` → `02-database/`
- `MILVUS_SCHEMA_EXPLANATION.md` → `02-database/`
- `MILVUS_SETUP.md` → `02-database/`

## O

- `objectname.md` → `06-tools-and-tests/`
- `openai_demo.py` → `04-api-integration/`

## P

- `persistence_example.py` → `02-database/`
- `PERSISTENCE_COMPARISON.md` → `02-database/`

## R

- `runtime_vs_type_checking.py` → `01-type-system/`
- `RUNTIME_VS_TYPE_CHECKING.md` → `01-type-system/`

## S

- `self_examples.py` → `03-python-basics/`
- `SELF_EXPLANATION.md` → `03-python-basics/`
- `slice_explanation.py` → `03-python-basics/`
- `sqlalchemy_example.py` → `02-database/`
- `sqlalchemy_tutorial.py` → `02-database/`
- `SQLALCHEMY_QUICK_REFERENCE.md` → `02-database/`
- `structure_output.json` → `06-tools-and-tests/`

## T

- `test.py` → `06-tools-and-tests/`
- `test.txt` → `06-tools-and-tests/`
- `test.yaml` → `06-tools-and-tests/`
- `test_duplicate_insert.py` → `02-database/`
- `test_import.py` → `06-tools-and-tests/`
- `test_persistence.py` → `02-database/`
- `tuple_equality_explanation.py` → `03-python-basics/`
- `tuple_immutability_explanation.py` → `03-python-basics/`
- `tutorial.db` → `02-database/`
- `type_annotation_usefulness.py` → `01-type-system/`
- `typevar_bound_explanation.py` → `01-type-system/`
- `typevar_usage_scenarios.py` → `01-type-system/`

## U

- `use_chunking.py` → `06-tools-and-tests/`
- `use_milvus_with_schema.py` → `02-database/`

## V

- `volumes/` → `05-devops/`
- `VOLUMES_EXPLANATION.md` → `02-database/`

---

## 按主题查找

### 类型系统相关
```
01-type-system/
├── forward_reference_example.py
├── generic_invariance_explanation.py
├── instantiation_demo.py
├── learn_typing.py
├── runtime_vs_type_checking.py
├── type_annotation_usefulness.py
├── typevar_bound_explanation.py
└── typevar_usage_scenarios.py
```

### 数据库相关
```
02-database/
├── SQLAlchemy: database.py, sqlalchemy_example.py, sqlalchemy_tutorial.py
├── Milvus: milvus_*.py, use_milvus_with_schema.py
└── 测试: test_duplicate_insert.py, test_persistence.py
```

### Python 基础
```
03-python-basics/
├── data_class.py
├── self_examples.py
├── slice_explanation.py
├── tuple_equality_explanation.py
└── tuple_immutability_explanation.py
```

### API 集成
```
04-api-integration/
└── openai_demo.py
```

### DevOps
```
05-devops/
├── docker-compose.yml
├── config.yaml
└── 数据目录: container/, volumes/, milvus_data/
```

### 工具和测试
```
06-tools-and-tests/
├── 测试: test.py, test_import.py
└── 工具: add.py, analyze_md.py, chunking.py, use_chunking.py
```

---

## 常见搜索

**Q: 在哪学习类型注解？**  
A: `01-type-system/learn_typing.py` 和 `01-type-system/type_annotation_usefulness.py`

**Q: 如何使用 SQLAlchemy？**  
A: `02-database/sqlalchemy_tutorial.py` 有完整教程

**Q: Milvus 怎么用？**  
A: 从 `02-database/MILVUS_SETUP.md` 开始，然后看 `milvus_use.py`

**Q: self 关键字是什么？**  
A: `03-python-basics/SELF_EXPLANATION.md` 有详细说明

**Q: 如何调用 OpenAI API？**  
A: `04-api-integration/openai_demo.py`

**Q: Docker 配置在哪？**  
A: `05-devops/docker-compose.yml`

**Q: 测试文件在哪？**  
A: `06-tools-and-tests/` 目录下所有 `test_*.py` 文件
