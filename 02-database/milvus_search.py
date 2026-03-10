"""
Milvus 搜索脚本 - 只用于查询，不需要重新加载数据

数据已持久化在 Docker volumes 中，无需每次重新加载
"""

import os

# ⚠️ 重要：必须在导入 model 之前设置环境变量
# 设置 HuggingFace 缓存目录到用户可写的目录
hf_cache_dir = os.path.expanduser('~/huggingface_cache')
os.makedirs(hf_cache_dir, exist_ok=True)
os.environ['HF_HOME'] = hf_cache_dir
os.environ['HF_DATASETS_CACHE'] = hf_cache_dir

# 现在可以安全导入 model
from pymilvus import MilvusClient, model

# 连接到 Milvus
print("正在连接到 Milvus 服务器...")
client = MilvusClient(uri="http://localhost:19530")
print("✓ 连接成功！\n")

COLLECTION_NAME = "demo_collection"

# 检查集合是否存在
if not client.has_collection(collection_name=COLLECTION_NAME):
    print(f"❌ 错误：集合 '{COLLECTION_NAME}' 不存在！")
    print("   请先运行 use_milvus.py 初始化数据")
    exit(1)

# 初始化嵌入函数
embedding_fn = model.DefaultEmbeddingFunction()

# 搜索函数
def search(query_text: str, limit: int = 3):
    """执行向量搜索"""
    print(f"查询: {query_text}")
    print("-" * 60)
    
    # 编码查询文本
    query_vectors = embedding_fn.encode_queries([query_text])
    
    # 执行搜索
    results = client.search(
        collection_name=COLLECTION_NAME,
        data=query_vectors,
        limit=limit,
        output_fields=["text", "subject"],
    )
    
    # 显示结果
    if len(results[0]) > 0:
        print(f"找到 {len(results[0])} 条结果:\n")
        for i, result in enumerate(results[0], 1):
            print(f"结果 {i}:")
            print(f"  ID: {result['id']}")
            print(f"  相似度: {1 - result['distance']:.4f} (距离: {result['distance']:.4f})")
            print(f"  文本: {result.get('text', 'N/A')}")
            print(f"  主题: {result.get('subject', 'N/A')}")
            print()
    else:
        print("未找到相关结果")
    
    return results


if __name__ == "__main__":
    # 示例查询
    queries = [
        "谁是戈登?",
        "Who is Alan Turing?",
        "What is artificial intelligence?",
        "Where was Turing born?",
    ]
    
    for query in queries:
        search(query, limit=2)
        print("\n" + "="*60 + "\n")
    
    # 交互式查询（可选）
    print("提示：可以修改 queries 列表添加更多查询")
    print("或者调用 search('你的问题') 函数进行搜索")

