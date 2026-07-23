"""
Milvus 使用示例 - 使用 Collection 和 Schema（完整版）

对比：使用 Schema 定义的方式
"""

from pymilvus import (
    Collection, FieldSchema, CollectionSchema,
    DataType, connections, utility
)
import os
import time

# ⚠️ 重要：必须在导入 model 之前设置环境变量
hf_cache_dir = os.path.expanduser('~/huggingface_cache')
os.makedirs(hf_cache_dir, exist_ok=True)
os.environ['HF_HOME'] = hf_cache_dir
os.environ['HF_DATASETS_CACHE'] = hf_cache_dir

from pymilvus import model

# 连接到 Milvus
print("正在连接到 Milvus 服务器...")
connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)
print("✓ 连接成功！")

COLLECTION_NAME = "demo_collection_with_schema"

# 检查集合是否存在
if utility.has_collection(COLLECTION_NAME):
    print(f"✓ 集合 '{COLLECTION_NAME}' 已存在")
    collection = Collection(COLLECTION_NAME)
else:
    print("创建集合（使用 Schema）...")
    
    # ============================================================
    # 定义 Schema（必须）
    # ============================================================
    
    # 1. 定义主键字段
    id_field = FieldSchema(
        name="id",
        dtype=DataType.INT64,
        is_primary=True,
        auto_id=False  # 手动指定 ID
    )
    
    # 2. 定义向量字段
    vector_field = FieldSchema(
        name="vector",
        dtype=DataType.FLOAT_VECTOR,
        dim=768  # 向量维度
    )
    
    # 3. 定义文本字段
    text_field = FieldSchema(
        name="text",
        dtype=DataType.VARCHAR,
        max_length=65535  # 最大长度
    )
    
    # 4. 定义主题字段
    subject_field = FieldSchema(
        name="subject",
        dtype=DataType.VARCHAR,
        max_length=100
    )
    
    # 5. 创建 Schema
    schema = CollectionSchema(
        fields=[id_field, vector_field, text_field, subject_field],
        description="Demo collection with explicit schema definition"
    )
    
    # 6. 创建集合
    collection = Collection(
        name=COLLECTION_NAME,
        schema=schema
    )
    
    print("✓ 集合创建成功！")
    print(f"  Schema: {collection.schema}")

# 准备数据
embedding_fn = model.DefaultEmbeddingFunction()

docs = [
    "Artificial intelligence was founded as an academic discipline in 1956.",
    "Alan Turing was the first person to conduct substantial research in AI.",
    "Born in Maida Vale, London, Turing was raised in southern England.",
]

vectors = embedding_fn.encode_documents(docs)
print(f"\n向量维度: {embedding_fn.dim}")

# 准备数据（必须匹配 Schema 定义的字段）
data = [
    {
        "id": i,
        "vector": vectors[i].tolist(),  # 转换为列表
        "text": docs[i],
        "subject": "history"
    }
    for i in range(len(vectors))
]

print(f"\n准备插入 {len(data)} 条数据...")

# 插入数据
print("\n插入数据到 Milvus...")
res = collection.insert(data)
collection.flush()  # 确保数据写入
print(f"✓ 插入成功！插入 ID 数量: {len(res.primary_keys)}")

# 创建索引（可选，但推荐）
print("\n创建索引...")
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128}
}
collection.create_index(field_name="vector", index_params=index_params)
print("✓ 索引创建成功！")

# 加载集合到内存
print("\n加载集合到内存...")
collection.load()
print("✓ 集合已加载！")

# 等待索引完成
time.sleep(2)

# 搜索数据
print("\n" + "="*60)
print("搜索数据")
print("="*60)

query_text = "Who is Alan Turing?"
print(f"\n查询问题: {query_text}")

query_vectors = embedding_fn.encode_queries([query_text])
query_vector = query_vectors[0].tolist()

# 执行搜索
search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
results = collection.search(
    data=[query_vector],
    anns_field="vector",
    param=search_params,
    limit=2,
    output_fields=["text", "subject"]
)

print(f"\n✓ 搜索完成！找到 {len(results[0])} 条结果\n")

for i, result in enumerate(results[0], 1):
    print(f"结果 {i}:")
    print(f"  ID: {result.id}")
    print(f"  距离: {result.distance:.4f}")
    print(f"  文本: {result.entity.get('text', 'N/A')}")
    print(f"  主题: {result.entity.get('subject', 'N/A')}")
    print()

# 查看集合统计信息
print("\n集合统计信息:")
stats = collection.num_entities
print(f"  总记录数: {stats}")

print("\n✓ 所有操作完成！")

# 断开连接
connections.disconnect("default")
print("✓ 已断开连接")

