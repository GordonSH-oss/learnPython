# Milvus 数据持久化机制详解

## 📦 持久化原理

Milvus 通过 **Docker Volumes（数据卷）** 实现数据持久化。数据存储在**宿主机**的文件系统中，而不是容器内部，因此即使容器停止或删除，数据也会保留。

## 🔍 持久化配置

### docker-compose.yml 中的配置

```yaml
volumes:
  - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/etcd:/etcd        # etcd 数据
  - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/minio:/minio_data # MinIO 数据
  - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/milvus:/var/lib/milvus # Milvus 数据
```

### 配置说明

| 服务 | 容器内路径 | 宿主机路径 | 存储内容 |
|------|-----------|-----------|---------|
| **etcd** | `/etcd` | `./volumes/etcd` | 元数据（集合定义、索引信息等） |
| **MinIO** | `/minio_data` | `./volumes/minio` | 向量数据文件（实际存储） |
| **Milvus** | `/var/lib/milvus` | `./volumes/milvus` | Milvus 配置和日志 |

### 路径映射格式

```
宿主机路径:容器内路径
```

- **左侧**：宿主机（你的电脑）上的路径
- **右侧**：容器内的路径
- **作用**：将容器内的数据**映射**到宿主机，实现持久化

## 📁 数据存储结构

### 1. etcd 数据（元数据存储）

```
volumes/etcd/
├── member/          # etcd 成员数据
│   ├── snap/        # 快照文件
│   └── wal/         # 预写日志
└── ...
```

**存储内容**：
- 集合（Collection）定义
- 字段（Field）定义
- 索引（Index）信息
- 分区（Partition）信息

### 2. MinIO 数据（向量数据存储）

```
volumes/minio/
└── a-bucket/        # 默认存储桶
    └── files/
        ├── insert_log/    # 插入日志（向量数据）
        ├── stats_log/     # 统计日志
        └── ...
```

**存储内容**：
- 实际的向量数据
- 插入日志
- 索引文件

### 3. Milvus 数据（配置和日志）

```
volumes/milvus/
├── logs/            # 日志文件
└── ...
```

## 🔄 持久化工作流程

### 数据写入流程

```
1. Python 代码插入数据
   ↓
2. Milvus 接收数据
   ↓
3. 数据写入 MinIO（对象存储）
   ├─→ volumes/minio/  ← 持久化到宿主机
   ↓
4. 元数据写入 etcd
   ├─→ volumes/etcd/   ← 持久化到宿主机
   ↓
5. 数据完成持久化 ✅
```

### 容器重启流程

```
1. docker-compose down（停止容器）
   ↓
2. 容器删除，但 volumes 保留 ✅
   ↓
3. docker-compose up（启动容器）
   ↓
4. 容器挂载 volumes
   ├─→ volumes/etcd   → /etcd
   ├─→ volumes/minio  → /minio_data
   └─→ volumes/milvus → /var/lib/milvus
   ↓
5. Milvus 读取持久化数据 ✅
```

## 💾 为什么数据会持久化？

### Docker Volumes 的特性

1. **独立于容器生命周期**
   - 容器删除 → 数据保留
   - 容器重启 → 数据保留
   - 只有**显式删除 volume** 才会丢失数据

2. **映射到宿主机文件系统**
   - 数据实际存储在宿主机上
   - 容器只是"挂载"这些目录
   - 类似 Linux 的 mount 操作

3. **跨容器共享**
   - 多个容器可以共享同一个 volume
   - 适合微服务架构

## 🧪 验证持久化

### 测试1：停止并重启容器

```bash
# 停止容器
docker-compose down

# 检查数据是否还在
ls -la volumes/

# 重启容器
docker-compose up -d

# 数据应该还在 ✅
```

### 测试2：查看数据大小

```bash
# 查看数据大小
du -sh volumes/*

# 插入数据后，大小会增加
# 重启容器后，大小保持不变
```

### 测试3：代码验证

```python
# 第一次运行：插入数据
python use_milvus.py

# 停止容器
docker-compose down

# 重启容器
docker-compose up -d

# 第二次运行：数据还在，无需重新插入
python search_milvus.py  # ✅ 可以查询到数据
```

## 🗑️ 如何删除数据？

### 方法1：删除 volumes（完全清理）

```bash
# 停止并删除容器和 volumes
docker-compose down -v

# 这会删除所有数据！
```

### 方法2：只删除容器（保留数据）

```bash
# 只删除容器，保留 volumes
docker-compose down

# 数据仍然保留在 volumes/ 目录中
```

### 方法3：手动删除 volumes 目录

```bash
# 停止容器
docker-compose down

# 删除 volumes 目录
rm -rf volumes/

# 数据被删除
```

## 📊 当前数据状态

查看当前存储的数据：

```bash
# 查看数据大小
du -sh volumes/*

# 查看 etcd 数据
ls -la volumes/etcd/

# 查看 MinIO 数据
ls -la volumes/minio/
```

## 🔐 数据安全

### 备份数据

```bash
# 备份 volumes 目录
tar -czf milvus_backup_$(date +%Y%m%d).tar.gz volumes/

# 恢复数据
tar -xzf milvus_backup_YYYYMMDD.tar.gz
```

### 迁移数据

```bash
# 1. 停止容器
docker-compose down

# 2. 复制 volumes 目录到新位置
cp -r volumes/ /backup/location/

# 3. 在新位置启动容器
# 修改 docker-compose.yml 中的路径
```

## 📝 总结

### 持久化的关键点

1. **Docker Volumes**：数据存储在宿主机，不依赖容器
2. **路径映射**：`宿主机路径:容器内路径` 实现数据映射
3. **自动持久化**：写入操作自动保存到 volumes
4. **跨容器持久**：容器重启、删除都不影响数据

### 数据生命周期

```
创建数据 → 写入 volumes → 持久化到宿主机
    ↓
容器重启 → 挂载 volumes → 数据恢复 ✅
    ↓
删除容器 → volumes 保留 → 数据保留 ✅
    ↓
删除 volumes → 数据丢失 ❌
```

### 最佳实践

- ✅ **开发环境**：使用 volumes 持久化数据
- ✅ **生产环境**：使用命名 volumes 或外部存储
- ✅ **备份**：定期备份 volumes 目录
- ✅ **迁移**：通过复制 volumes 目录迁移数据

