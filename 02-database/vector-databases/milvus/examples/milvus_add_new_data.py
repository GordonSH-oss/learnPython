"""
Milvus 添加新数据示例

演示如何向已存在的集合中添加新数据
"""

import os
import time

# ⚠️ 重要：必须在导入 model 之前设置环境变量
hf_cache_dir = os.path.expanduser('~/huggingface_cache')
os.makedirs(hf_cache_dir, exist_ok=True)
os.environ['HF_HOME'] = hf_cache_dir
os.environ['HF_DATASETS_CACHE'] = hf_cache_dir

# 现在可以安全导入 model
from pymilvus import MilvusClient, model

# 连接到 Milvus
client = MilvusClient(uri="http://localhost:19530")
COLLECTION_NAME = "demo_collection"

# 检查集合是否存在
if not client.has_collection(collection_name=COLLECTION_NAME):
    print(f"❌ 集合 '{COLLECTION_NAME}' 不存在")
    print("   请先运行 use_milvus.py 创建集合并插入初始数据")
    exit(1)

print(f"✓ 集合 '{COLLECTION_NAME}' 已存在")

# 查看当前数据量
stats = client.get_collection_stats(collection_name=COLLECTION_NAME)
current_count = stats.get('row_count', 0)
print(f"✓ 当前数据量: {current_count} 条记录")

# 准备新数据
embedding_fn = model.DefaultEmbeddingFunction()

new_docs = [
    "Machine learning is a subset of artificial intelligence.",
    "Deep learning uses neural networks with multiple layers.",
    "Natural language processing enables computers to understand human language.",
    "Gordon is a good man."
]

print(f"\n准备添加 {len(new_docs)} 条新数据...")

# 生成向量
new_vectors = embedding_fn.encode_documents(new_docs)

# 准备数据（使用时间戳作为 ID，避免冲突）
base_id = int(time.time() * 1000)  # 使用时间戳

new_data = [
    {
        "id": base_id + i,
        "vector": new_vectors[i],
        "text": new_docs[i],
        "subject": "technology"  # 新数据的主题
    }
    for i in range(len(new_vectors))
]

print(f"新数据 ID 范围: {new_data[0]['id']} - {new_data[-1]['id']}")

# 插入新数据
print("\n插入新数据到 Milvus...")
res = client.insert(collection_name=COLLECTION_NAME, data=new_data)
print(f"✓ 插入成功！插入 ID 数量: {res['insert_count']}")

# 等待索引完成
print("等待数据索引完成...")
time.sleep(2)

# 查看更新后的数据量
stats_after = client.get_collection_stats(collection_name=COLLECTION_NAME)
new_count = stats_after.get('row_count', 0)
print(f"\n✓ 更新后数据量: {new_count} 条记录")
print(f"  新增: {new_count - current_count} 条记录")

# 验证新数据是否可以搜索到
print("\n" + "="*60)
print("验证新数据（搜索测试）")
print("="*60)

query_text = "What is machine learning?"
print(f"\n查询问题: {query_text}")

query_vectors = embedding_fn.encode_queries([query_text])
results = client.search(
    collection_name=COLLECTION_NAME,
    data=query_vectors,
    limit=3,
    output_fields=["id", "text", "subject"]
)

print(f"\n✓ 搜索完成！找到 {len(results[0])} 条结果\n")

for i, result in enumerate(results[0], 1):
    print(f"结果 {i}:")
    print(f"  ID: {result['id']}")
    print(f"  距离: {result['distance']:.4f}")
    print(f"  文本: {result.get('text', 'N/A')[:60]}...")
    print(f"  主题: {result.get('subject', 'N/A')}")
    print()

print("✓ 新数据添加完成！")
