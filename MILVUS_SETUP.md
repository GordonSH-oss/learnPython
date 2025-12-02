# Milvus Docker 使用指南

## ✅ 已成功设置

Milvus 已通过 Docker Compose 成功运行！

## 服务状态

使用以下命令查看服务状态：

```bash
docker-compose ps
```

## 启动/停止服务

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看日志
docker-compose logs -f milvus-standalone
```

## 服务端口

- **Milvus**: `localhost:19530` (gRPC)
- **Milvus**: `localhost:9091` (HTTP)
- **MinIO**: `localhost:9000` (API), `localhost:9001` (Console)
- **etcd**: `localhost:2379` (内部使用)

## 代码使用

```python
from pymilvus import MilvusClient

# 连接到 Milvus
client = MilvusClient(uri="http://localhost:19530")

# 创建集合
client.create_collection(
    collection_name="demo_collection",
    dimension=768,
)

# 插入数据
data = [{"id": 0, "vector": [0.1] * 768, "text": "example"}]
client.insert(collection_name="demo_collection", data=data)

# 搜索
results = client.search(
    collection_name="demo_collection",
    data=[[0.1] * 768],
    limit=5
)
```

## 数据持久化

数据存储在 `./volumes/` 目录下：
- `volumes/etcd/` - etcd 数据
- `volumes/minio/` - MinIO 对象存储
- `volumes/milvus/` - Milvus 数据

## 清理数据

如果需要清理所有数据：

```bash
docker-compose down -v
```

## 故障排查

1. **检查服务状态**：
   ```bash
   docker-compose ps
   ```

2. **查看日志**：
   ```bash
   docker-compose logs milvus-standalone
   ```

3. **重启服务**：
   ```bash
   docker-compose restart
   ```

