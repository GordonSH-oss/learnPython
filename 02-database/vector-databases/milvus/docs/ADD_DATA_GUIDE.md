# Milvus 添加新数据指南

## 📋 场景说明

当前 `use_milvus.py` 的保护机制会阻止重复插入：
- 如果集合已存在 → 跳过插入
- 这适合初始化数据，但不适合添加新数据

## 🎯 添加新数据的方案

### 方案1：使用独立的添加脚本（推荐）

创建一个专门的脚本 `add_new_data.py` 来添加新数据。

**优点**：
- ✅ 不影响现有代码
- ✅ 职责清晰
- ✅ 可以随时添加新数据

**使用方法**：
```bash
python add_new_data.py
```

### 方案2：修改现有代码，添加增量插入功能

在 `use_milvus.py` 中添加一个函数来支持增量添加。

### 方案3：使用 RELOAD_DATA 标志

设置 `RELOAD_DATA = True` 会重新插入所有数据（包括旧数据）。

**缺点**：
- ❌ 会重复插入旧数据
- ❌ 不是真正的增量添加

## 💡 推荐方案：独立脚本 + 函数封装

### 步骤1：创建添加新数据的函数

```python
def add_new_data_to_collection(
    client: MilvusClient,
    collection_name: str,
    new_docs: list,
    embedding_fn,
    subject: str = "general"
):
    """
    向集合中添加新数据
    
    Args:
        client: MilvusClient 实例
        collection_name: 集合名称
        new_docs: 新的文档列表
        embedding_fn: 嵌入函数
        subject: 数据主题（可选）
    
    Returns:
        插入结果
    """
    # 生成向量
    vectors = embedding_fn.encode_documents(new_docs)
    
    # 使用时间戳作为 ID（避免冲突）
    import time
    base_id = int(time.time() * 1000)
    
    # 准备数据
    data = [
        {
            "id": base_id + i,
            "vector": vectors[i],
            "text": new_docs[i],
            "subject": subject
        }
        for i in range(len(vectors))
    ]
    
    # 插入数据
    res = client.insert(collection_name=collection_name, data=data)
    
    # 等待索引完成
    time.sleep(2)
    
    return res
```

### 步骤2：使用函数添加新数据

```python
from pymilvus import MilvusClient, model
import os

# 设置环境变量
hf_cache_dir = os.path.expanduser('~/huggingface_cache')
os.makedirs(hf_cache_dir, exist_ok=True)
os.environ['HF_HOME'] = hf_cache_dir
os.environ['HF_DATASETS_CACHE'] = hf_cache_dir

# 连接
client = MilvusClient(uri="http://localhost:19530")
embedding_fn = model.DefaultEmbeddingFunction()

# 新数据
new_docs = [
    "Machine learning is a subset of AI.",
    "Deep learning uses neural networks.",
]

# 添加新数据
res = add_new_data_to_collection(
    client=client,
    collection_name="demo_collection",
    new_docs=new_docs,
    embedding_fn=embedding_fn,
    subject="technology"
)

print(f"✓ 添加了 {res['insert_count']} 条新数据")
```

## 🔧 ID 生成策略

### 策略1：使用时间戳（推荐）

```python
import time
base_id = int(time.time() * 1000)  # 毫秒时间戳
```

**优点**：
- ✅ 唯一性好
- ✅ 可以排序（按时间）
- ✅ 简单易用

**缺点**：
- ⚠️ 如果同一毫秒内插入多条，可能冲突

### 策略2：使用 UUID

```python
import uuid
record_id = str(uuid.uuid4())
```

**优点**：
- ✅ 绝对唯一
- ✅ 不会冲突

**缺点**：
- ⚠️ 无法排序
- ⚠️ ID 较长

### 策略3：查询最大 ID 后递增

```python
# 查询当前最大 ID
results = client.query(
    collection_name=collection_name,
    filter="",
    output_fields=["id"],
    limit=1,
    order_by=[("id", "desc")]
)

max_id = results[0]['id'] if results else -1
new_id = max_id + 1
```

**优点**：
- ✅ ID 连续
- ✅ 易于管理

**缺点**：
- ⚠️ 需要查询操作
- ⚠️ 并发时可能冲突

## 📝 完整示例

### 示例1：添加单条数据

```python
from pymilvus import MilvusClient, model
import os
import time

# 设置环境变量
hf_cache_dir = os.path.expanduser('~/huggingface_cache')
os.makedirs(hf_cache_dir, exist_ok=True)
os.environ['HF_HOME'] = hf_cache_dir
os.environ['HF_DATASETS_CACHE'] = hf_cache_dir

from pymilvus import model

# 连接
client = MilvusClient(uri="http://localhost:19530")
COLLECTION_NAME = "demo_collection"

# 检查集合是否存在
if not client.has_collection(collection_name=COLLECTION_NAME):
    print("❌ 集合不存在，请先运行 use_milvus.py")
    exit(1)

# 准备新数据
embedding_fn = model.DefaultEmbeddingFunction()
new_doc = "This is a new document to add."

# 生成向量
vector = embedding_fn.encode_documents([new_doc])[0]

# 使用时间戳作为 ID
new_id = int(time.time() * 1000)

# 插入数据
data = [{
    "id": new_id,
    "vector": vector,
    "text": new_doc,
    "subject": "new"
}]

res = client.insert(collection_name=COLLECTION_NAME, data=data)
print(f"✓ 添加了 {res['insert_count']} 条新数据，ID: {new_id}")

# 等待索引
time.sleep(2)
```

### 示例2：批量添加数据

```python
# 批量添加多条数据
new_docs = [
    "Document 1",
    "Document 2",
    "Document 3",
]

vectors = embedding_fn.encode_documents(new_docs)
base_id = int(time.time() * 1000)

data = [
    {
        "id": base_id + i,
        "vector": vectors[i],
        "text": new_docs[i],
        "subject": "batch"
    }
    for i in range(len(new_docs))
]

res = client.insert(collection_name=COLLECTION_NAME, data=data)
print(f"✓ 批量添加了 {res['insert_count']} 条新数据")
```

## 🎯 最佳实践

### 1. 使用独立的添加脚本

创建 `add_new_data.py`，专门用于添加新数据。

### 2. 使用时间戳作为 ID

```python
base_id = int(time.time() * 1000)
```

### 3. 检查集合是否存在

```python
if not client.has_collection(collection_name=COLLECTION_NAME):
    print("集合不存在")
    exit(1)
```

### 4. 等待索引完成

```python
time.sleep(2)  # 等待索引完成
```

### 5. 验证新数据

```python
# 插入后验证
stats = client.get_collection_stats(collection_name=COLLECTION_NAME)
print(f"当前数据量: {stats.get('row_count', 0)}")
```

## 📊 工作流程

```
1. 检查集合是否存在
   ↓
2. 准备新数据（文档列表）
   ↓
3. 生成向量（使用 embedding_fn）
   ↓
4. 生成唯一 ID（时间戳或 UUID）
   ↓
5. 构建数据对象（id, vector, text, ...）
   ↓
6. 插入数据（client.insert）
   ↓
7. 等待索引完成（time.sleep）
   ↓
8. 验证数据（可选）
```

## ⚠️ 注意事项

1. **ID 冲突**：确保使用唯一的 ID
2. **索引时间**：插入后需要等待索引完成
3. **数据格式**：新数据的格式必须与集合定义一致
4. **向量维度**：新数据的向量维度必须与集合定义一致

## 🔄 与现有代码的关系

- `use_milvus.py`：初始化集合和初始数据
- `add_new_data.py`：添加新数据
- `search_milvus.py`：搜索数据

三个脚本各司其职，互不干扰。

