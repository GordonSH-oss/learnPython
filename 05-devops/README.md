# 容器化和部署

Docker、docker-compose 等容器化相关的配置和数据。

## 目录结构

```
05-devops/
├── container/       # 容器相关文件
├── volumes/         # Docker 卷数据
└── milvus_data/     # Milvus 向量数据库数据
```

## Docker 基础

### 什么是 Docker？
Docker 是一个容器化平台，可以将应用及其依赖打包在一起，确保在任何环境都能一致运行。

### 核心概念
1. **镜像 (Image)**: 应用的只读模板
2. **容器 (Container)**: 镜像的运行实例
3. **卷 (Volume)**: 持久化数据存储
4. **网络 (Network)**: 容器间通信

## Docker Compose

### 用途
Docker Compose 用于定义和运行多容器 Docker 应用。

### 基础命令
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 查看运行状态
docker-compose ps

# 重启服务
docker-compose restart
```

## Milvus 容器化部署

### 启动 Milvus
如果根目录有 `docker-compose.yml`：

```bash
# 启动 Milvus
docker-compose up -d

# 检查运行状态
docker-compose ps

# 查看日志
docker-compose logs -f milvus-standalone
```

### 数据持久化
- `milvus_data/` 目录映射到容器内的数据目录
- 即使容器删除，数据仍然保留在主机上

### 端口映射
默认端口：
- Milvus: `19530`
- Etcd: `2379`
- MinIO: `9000`, `9001`

## Docker 卷 (Volumes)

### 类型
1. **命名卷**: Docker 管理的卷
   ```yaml
   volumes:
     milvus-data:
   ```

2. **绑定挂载**: 主机目录映射
   ```yaml
   volumes:
     - ./volumes:/var/lib/milvus
   ```

3. **匿名卷**: 临时数据
   ```yaml
   volumes:
     - /tmp/data
   ```

### 查看卷
```bash
# 列出所有卷
docker volume ls

# 查看卷详情
docker volume inspect <volume_name>

# 删除未使用的卷
docker volume prune
```

## 实践指南

### 1. 清理和重启
```bash
# 停止并删除容器、网络
docker-compose down

# 删除卷数据（谨慎！会丢失数据）
docker-compose down -v

# 重新启动
docker-compose up -d
```

### 2. 备份数据
```bash
# 备份 volumes 目录
tar -czf backup.tar.gz volumes/

# 或备份 Docker 卷
docker run --rm -v milvus-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/milvus-backup.tar.gz /data
```

### 3. 迁移数据
```bash
# 导出数据
docker-compose down
cp -r volumes/ backup/

# 在新环境恢复
cp -r backup/volumes/ .
docker-compose up -d
```

## 常见问题

### 端口被占用
```bash
# 查看端口占用
lsof -i :19530

# 修改 docker-compose.yml 中的端口映射
ports:
  - "19531:19530"  # 使用其他端口
```

### 容器无法启动
```bash
# 查看详细日志
docker-compose logs

# 检查容器状态
docker-compose ps

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 数据丢失
确保使用卷挂载：
```yaml
services:
  milvus:
    volumes:
      - ./volumes:/var/lib/milvus  # 绑定挂载
      # 或
      - milvus-data:/var/lib/milvus  # 命名卷

volumes:
  milvus-data:
```

## 最佳实践

1. **使用 .dockerignore** - 排除不需要的文件
2. **环境变量管理** - 使用 `.env` 文件
3. **定期备份** - 自动化备份重要数据
4. **资源限制** - 设置内存和 CPU 限制
5. **日志管理** - 配置日志轮转
6. **安全加固** - 不暴露不必要的端口

## 学习资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Milvus Docker 部署](https://milvus.io/docs/install_standalone-docker.md)
