"""
Milvus 使用示例 - 使用 Docker 运行的 Milvus 服务器

启动 Milvus Docker 容器：
docker run -d --name milvus-standalone -p 19530:19530 milvusdb/milvus:v2.3.0 milvus run standalone

检查容器状态：
docker ps | grep milvus
"""

from pymilvus import MilvusClient

# 连接到 Docker 运行的 Milvus 服务器
print("正在连接到 Milvus 服务器...")
client = MilvusClient(uri="http://localhost:19530")
print("✓ 连接成功！")

# 创建集合（如果不存在）
COLLECTION_NAME = "demo_collection"
if client.has_collection(collection_name=COLLECTION_NAME):
    print(f"✓ 集合 '{COLLECTION_NAME}' 已存在，跳过创建")
    print("  提示：数据已持久化，无需重新加载")
else:
    print("创建集合...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=768,  # 向量维度
    )
    print("✓ 集合创建成功！")


import os

# 设置 HuggingFace 缓存目录到用户可写的目录
# 解决权限问题：/Users/admin/.cache 目录属于 root，无法写入
hf_cache_dir = os.path.expanduser('~/huggingface_cache')
os.makedirs(hf_cache_dir, exist_ok=True)
# 使用 HF_HOME（推荐，新版本）
os.environ['HF_HOME'] = hf_cache_dir
# HF_DATASETS_CACHE 用于数据集缓存
os.environ['HF_DATASETS_CACHE'] = hf_cache_dir

print(f"✓ 使用 HuggingFace 缓存目录: {hf_cache_dir}")

from pymilvus import model

embedding_fn = model.DefaultEmbeddingFunction()

docs = [
    "Artificial intelligence was founded as an academic discipline in 1956.",
    "Alan Turing was the first person to conduct substantial research in AI.",
    "Born in Maida Vale, London, Turing was raised in southern England.",
]

vectors = embedding_fn.encode_documents(docs)
print("Dim:", embedding_fn.dim, vectors[0].shape)  # Dim: 768 (768,)

data = [
    {"id": i, "vector": vectors[i], "text": docs[i], "subject": "history"}
    for i in range(len(vectors))
]

print("Data has", len(data), "entities, each with fields: ", data[0].keys())
print("Vector dim:", len(data[0]["vector"]))

# 检查是否需要插入数据（可选：只在首次运行时插入）
# 如果需要每次都重新加载数据，取消下面的注释
RELOAD_DATA = False  # 设置为 True 可以强制重新加载数据

if RELOAD_DATA or not client.has_collection(collection_name=COLLECTION_NAME):
    # 插入数据到 Milvus
    print("\n插入数据到 Milvus...")
    res = client.insert(collection_name=COLLECTION_NAME, data=data)
    print(f"✓ 插入成功！插入 ID 数量: {res['insert_count']}")
    
    # 等待数据索引完成（Milvus 需要时间索引数据）
    import time
    print("等待数据索引完成...")
    time.sleep(2)  # 等待2秒让数据完成索引
else:
    print(f"\n✓ 集合 '{COLLECTION_NAME}' 已有数据，跳过插入")
    print("  提示：如需重新加载数据，设置 RELOAD_DATA = True")

# 查询数据（示例）
print("\n查询数据（示例）...")
results = client.search(
    collection_name=COLLECTION_NAME,
    data=[vectors[0]],  # 使用第一个向量进行搜索
    limit=3
)
print(f"✓ 查询成功！找到 {len(results[0])} 条结果")
if len(results[0]) > 0:
    for i, result in enumerate(results[0], 1):
        print(f"  结果 {i}: id={result['id']}, distance={result['distance']:.4f}")
else:
    print("  注意：查询返回0条结果，可能需要更多时间索引数据")

# 基于查询文本的搜索
print("\n" + "="*60)
print("基于查询文本的搜索")
print("="*60)

# 编码查询文本
query_text = "Who is Alan Turing?"
print(f"\n查询问题: {query_text}")
query_vectors = embedding_fn.encode_queries([query_text])
print(f"✓ 查询向量已生成，维度: {len(query_vectors[0])}")

# 执行搜索
print("\n执行搜索...")
res = client.search(
    collection_name=COLLECTION_NAME,  # 目标集合
    data=query_vectors,  # 查询向量
    limit=2,  # 返回的实体数量
    output_fields=["text", "subject"],  # 指定要返回的字段
)

print(f"\n✓ 搜索完成！找到 {len(res[0])} 条结果\n")

# 格式化输出结果
for i, result in enumerate(res[0], 1):
    print(f"结果 {i}:")
    print(f"  ID: {result['id']}")
    print(f"  距离: {result['distance']:.4f} (距离越小越相似)")
    print(f"  文本: {result.get('text', 'N/A')}")
    print(f"  主题: {result.get('subject', 'N/A')}")
    print()

# 查看集合统计信息
print("\n集合统计信息:")
stats = client.get_collection_stats(collection_name=COLLECTION_NAME)
print(f"  总记录数: {stats.get('row_count', 'N/A')}")

print("\n✓ 所有操作完成！")
