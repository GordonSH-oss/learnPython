"""
测试 Milvus 重复插入的行为

演示如果多次运行 insert() 会发生什么
"""

import os

# ⚠️ 重要：必须在导入 model 之前设置环境变量
# 设置 HuggingFace 缓存
hf_cache_dir = os.path.expanduser('~/huggingface_cache')
os.makedirs(hf_cache_dir, exist_ok=True)
os.environ['HF_HOME'] = hf_cache_dir
os.environ['HF_DATASETS_CACHE'] = hf_cache_dir

# 现在可以安全导入 model
from pymilvus import MilvusClient, model

client = MilvusClient(uri="http://localhost:19530")
COLLECTION_NAME = "test_duplicate_collection"

# 创建测试集合（如果不存在）
if not client.has_collection(collection_name=COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=768,
    )
    print(f"✓ 创建测试集合: {COLLECTION_NAME}")

# 准备测试数据
embedding_fn = model.DefaultEmbeddingFunction()
docs = [
    "This is a test document.",
    "Another test document.",
]

vectors = embedding_fn.encode_documents(docs)

# 第一次插入
print("\n" + "="*70)
print("第一次插入（使用 id=0, id=1）")
print("="*70)

data1 = [
    {"id": 0, "vector": vectors[0], "text": docs[0]},
    {"id": 1, "vector": vectors[1], "text": docs[1]},
]

res1 = client.insert(collection_name=COLLECTION_NAME, data=data1)
print(f"插入记录数: {res1['insert_count']}")

stats1 = client.get_collection_stats(collection_name=COLLECTION_NAME)
print(f"当前总记录数: {stats1.get('row_count', 0)}")

# 第二次插入 - 相同的内容，相同的 ID
print("\n" + "="*70)
print("第二次插入（相同内容，相同 id=0, id=1）")
print("="*70)

data2 = [
    {"id": 0, "vector": vectors[0], "text": docs[0]},  # 相同的 id 和内容
    {"id": 1, "vector": vectors[1], "text": docs[1]},  # 相同的 id 和内容
]

try:
    res2 = client.insert(collection_name=COLLECTION_NAME, data=data2)
    print(f"插入记录数: {res2['insert_count']}")
    
    stats2 = client.get_collection_stats(collection_name=COLLECTION_NAME)
    print(f"当前总记录数: {stats2.get('row_count', 0)}")
    print("⚠️  注意：如果 ID 已存在，Milvus 可能会更新记录或报错")
except Exception as e:
    print(f"❌ 插入失败: {e}")

# 第三次插入 - 相同的内容，不同的 ID
print("\n" + "="*70)
print("第三次插入（相同内容，不同 id=2, id=3）")
print("="*70)

data3 = [
    {"id": 2, "vector": vectors[0], "text": docs[0]},  # 相同内容，不同 ID
    {"id": 3, "vector": vectors[1], "text": docs[1]},  # 相同内容，不同 ID
]

res3 = client.insert(collection_name=COLLECTION_NAME, data=data3)
print(f"插入记录数: {res3['insert_count']}")

stats3 = client.get_collection_stats(collection_name=COLLECTION_NAME)
print(f"当前总记录数: {stats3.get('row_count', 0)}")
print("✅ 相同内容但不同 ID 会插入为新记录")

# 第四次插入 - 相同的内容，相同的 ID（再次尝试）
print("\n" + "="*70)
print("第四次插入（再次使用 id=0, id=1）")
print("="*70)

data4 = [
    {"id": 0, "vector": vectors[0], "text": docs[0]},
    {"id": 1, "vector": vectors[1], "text": docs[1]},
]

try:
    res4 = client.insert(collection_name=COLLECTION_NAME, data=data4)
    print(f"插入记录数: {res4['insert_count']}")
    
    stats4 = client.get_collection_stats(collection_name=COLLECTION_NAME)
    print(f"当前总记录数: {stats4.get('row_count', 0)}")
except Exception as e:
    print(f"❌ 插入失败: {e}")

# 最终统计
print("\n" + "="*70)
print("最终统计")
print("="*70)

final_stats = client.get_collection_stats(collection_name=COLLECTION_NAME)
print(f"最终总记录数: {final_stats.get('row_count', 0)}")

# 查询所有记录（使用 search 来查看实际数据）
print("\n查询所有记录（使用 search）:")
import time
time.sleep(1)  # 等待索引完成

# 使用第一个向量搜索，limit 设置大一些来查看所有数据
results = client.search(
    collection_name=COLLECTION_NAME,
    data=[vectors[0]],
    limit=10,  # 设置较大的 limit
    output_fields=["id", "text"]
)

if results and len(results[0]) > 0:
    print(f"找到 {len(results[0])} 条记录:")
    seen_ids = set()
    for i, result in enumerate(results[0], 1):
        record_id = result['id']
        if record_id not in seen_ids:
            seen_ids.add(record_id)
            print(f"  记录 {i}: id={record_id}, text={result.get('text', 'N/A')[:50]}...")
else:
    print("  未找到记录（可能需要等待索引完成）")

print("\n" + "="*70)
print("结论")
print("="*70)
print("""
1. ✅ 相同内容 + 不同 ID → 会插入为新记录（重复数据）
2. ⚠️  相同内容 + 相同 ID → 取决于 Milvus 配置：
   - 可能更新现有记录（upsert）
   - 可能报错（不允许重复 ID）
3. 💡 建议：
   - 使用唯一 ID 避免重复插入
   - 插入前检查数据是否已存在
   - 使用 upsert() 而不是 insert() 如果需要更新
""")

# 清理测试集合（可选）
print("\n是否删除测试集合？(y/n): ", end="")
# 取消注释下面的代码来清理
# client.drop_collection(collection_name=COLLECTION_NAME)
# print("✓ 测试集合已删除")

