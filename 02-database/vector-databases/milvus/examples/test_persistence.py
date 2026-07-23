"""
测试 Milvus 数据持久化

演示数据如何在容器重启后仍然保留
"""

import os
import time
from pymilvus import MilvusClient, model

# 设置 HuggingFace 缓存
hf_cache_dir = os.path.expanduser('~/huggingface_cache')
os.makedirs(hf_cache_dir, exist_ok=True)
os.environ['HF_HOME'] = hf_cache_dir
os.environ['HF_DATASETS_CACHE'] = hf_cache_dir

print("=" * 70)
print("Milvus 数据持久化测试")
print("=" * 70)

# 连接到 Milvus
client = MilvusClient(uri="http://localhost:19530")
COLLECTION_NAME = "demo_collection"

# 检查集合是否存在
if client.has_collection(collection_name=COLLECTION_NAME):
    print(f"\n✓ 集合 '{COLLECTION_NAME}' 已存在")
    
    # 获取集合统计信息
    stats = client.get_collection_stats(collection_name=COLLECTION_NAME)
    row_count = stats.get('row_count', 0)
    print(f"✓ 当前数据量: {row_count} 条记录")
    
    if row_count > 0:
        print("\n" + "-" * 70)
        print("数据持久化验证：")
        print("-" * 70)
        print("✅ 数据已持久化！即使容器重启，数据仍然保留。")
        print("\n数据存储位置：")
        print("  • etcd 元数据: ./volumes/etcd/")
        print("  • MinIO 向量数据: ./volumes/minio/")
        print("  • Milvus 配置: ./volumes/milvus/")
        
        # 执行一次搜索验证数据可用
        print("\n" + "-" * 70)
        print("验证数据可用性（执行搜索测试）：")
        print("-" * 70)
        
        embedding_fn = model.DefaultEmbeddingFunction()
        query_vectors = embedding_fn.encode_queries(["Alan Turing"])
        
        results = client.search(
            collection_name=COLLECTION_NAME,
            data=query_vectors,
            limit=1,
            output_fields=["text"]
        )
        
        if len(results[0]) > 0:
            print(f"✅ 搜索成功！找到数据：{results[0][0].get('text', 'N/A')[:50]}...")
            print("\n结论：数据持久化正常工作！")
        else:
            print("⚠️  搜索未找到结果（可能需要等待索引完成）")
    else:
        print("\n⚠️  集合存在但数据为空")
        print("   提示：运行 use_milvus.py 初始化数据")
else:
    print(f"\n❌ 集合 '{COLLECTION_NAME}' 不存在")
    print("   提示：运行 use_milvus.py 创建集合并插入数据")

print("\n" + "=" * 70)
print("持久化机制说明：")
print("=" * 70)
print("""
1. Docker Volumes 映射：
   volumes/etcd      → 容器内 /etcd
   volumes/minio     → 容器内 /minio_data
   volumes/milvus    → 容器内 /var/lib/milvus

2. 数据存储：
   • 元数据（集合定义、索引）→ etcd
   • 向量数据（实际内容）→ MinIO
   • 配置和日志 → Milvus

3. 持久化保证：
   • 容器停止 → 数据保留 ✅
   • 容器重启 → 数据恢复 ✅
   • 容器删除 → 数据保留 ✅
   • 只有删除 volumes 才会丢失数据 ❌

4. 验证方法：
   docker-compose down    # 停止容器
   docker-compose up -d   # 重启容器
   python search_milvus.py  # 数据应该还在 ✅
""")

