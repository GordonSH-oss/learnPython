"""
演示 Docker Volumes 持久化 vs 数据库持久化的区别

这个脚本展示了两种持久化方式的不同使用场景
"""

import json
import os
from datetime import datetime

# ============================================================================
# 方式1：Docker Volumes 持久化（文件系统级别）
# ============================================================================

def save_to_file(data, filename):
    """使用文件系统持久化数据"""
    os.makedirs('volumes/file_storage', exist_ok=True)
    filepath = os.path.join('volumes/file_storage', filename)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ 数据已保存到文件: {filepath}")


def load_from_file(filename):
    """从文件加载数据"""
    filepath = os.path.join('volumes/file_storage', filename)
    
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        print(f"✅ 从文件加载数据: {filepath}")
        return data
    else:
        print(f"❌ 文件不存在: {filepath}")
        return None


def search_in_files(keyword):
    """在文件中搜索（需要手动实现）"""
    results = []
    dir_path = 'volumes/file_storage'
    
    if not os.path.exists(dir_path):
        return results
    
    # ❌ 需要遍历所有文件，性能差
    for filename in os.listdir(dir_path):
        if filename.endswith('.json'):
            data = load_from_file(filename)
            if data and keyword.lower() in str(data).lower():
                results.append(data)
    
    print(f"🔍 搜索 '{keyword}'，找到 {len(results)} 条结果")
    return results


# ============================================================================
# 方式2：数据库持久化（应用级别）
# ============================================================================

def demo_database_persistence():
    """
    演示数据库持久化的优势
    
    注意：这只是一个概念演示，实际需要使用真实的数据库连接
    """
    print("\n" + "="*70)
    print("数据库持久化示例（概念演示）")
    print("="*70)
    
    # 假设的数据库操作（实际需要使用 psycopg2 等库）
    print("""
    # ✅ 使用 SQL 查询，简单高效
    SELECT * FROM users WHERE name = 'Alice';
    
    # ✅ 复杂查询也很简单
    SELECT u.name, COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.age BETWEEN 25 AND 35
    GROUP BY u.id
    HAVING COUNT(o.id) > 5
    ORDER BY order_count DESC;
    
    # ✅ 事务支持（要么全部成功，要么全部回滚）
    BEGIN;
    INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
    UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
    COMMIT;  -- 如果任何一步失败，自动回滚
    
    # ✅ 并发控制（数据库自动处理）
    -- 多个进程同时更新，数据库保证数据一致性
    """)
    
    print("\n数据库持久化的优势：")
    print("  ✅ SQL 查询语言（简单、强大）")
    print("  ✅ 事务支持（ACID 特性）")
    print("  ✅ 并发控制（自动处理）")
    print("  ✅ 索引支持（快速查询）")
    print("  ✅ 数据完整性约束（外键、检查等）")


# ============================================================================
# 对比演示
# ============================================================================

def compare_persistence_methods():
    """对比两种持久化方式"""
    
    print("="*70)
    print("Docker Volumes 持久化 vs 数据库持久化")
    print("="*70)
    
    # 示例数据
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 25},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 30},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 35},
    ]
    
    print("\n1️⃣ Docker Volumes 持久化（文件系统级别）")
    print("-" * 70)
    
    # 保存数据到文件
    for user in users:
        save_to_file(user, f"user_{user['id']}.json")
    
    # 搜索数据（需要手动实现）
    print("\n搜索用户 'Alice'：")
    results = search_in_files("Alice")
    for result in results:
        print(f"  找到: {result}")
    
    print("\n❌ 问题：")
    print("  • 需要遍历所有文件，性能差")
    print("  • 无事务支持，可能数据不一致")
    print("  • 无并发控制，可能数据竞争")
    print("  • 需要手动实现查询逻辑")
    
    print("\n" + "="*70)
    print("2️⃣ 数据库持久化（应用级别）")
    print("-" * 70)
    
    demo_database_persistence()
    
    print("\n" + "="*70)
    print("总结对比")
    print("="*70)
    
    comparison = {
        "持久化层次": {
            "Docker Volumes": "文件系统级别",
            "数据库": "应用/数据级别"
        },
        "数据格式": {
            "Docker Volumes": "原始文件（JSON、二进制等）",
            "数据库": "结构化数据（表、行、列）"
        },
        "访问方式": {
            "Docker Volumes": "文件系统 API（open、read、write）",
            "数据库": "SQL 查询语言"
        },
        "查询能力": {
            "Docker Volumes": "❌ 无，需要手动实现",
            "数据库": "✅ 强大，SQL 查询"
        },
        "事务支持": {
            "Docker Volumes": "❌ 无",
            "数据库": "✅ 有（ACID 特性）"
        },
        "并发控制": {
            "Docker Volumes": "❌ 无，需要应用自己处理",
            "数据库": "✅ 有，数据库自动处理"
        },
        "适用场景": {
            "Docker Volumes": "文件存储、应用数据文件、日志",
            "数据库": "结构化数据、需要查询和事务的场景"
        }
    }
    
    for key, value in comparison.items():
        print(f"\n{key}:")
        print(f"  Docker Volumes: {value['Docker Volumes']}")
        print(f"  数据库:         {value['数据库']}")


if __name__ == "__main__":
    compare_persistence_methods()
    
    print("\n" + "="*70)
    print("实际应用中的组合使用")
    print("="*70)
    print("""
    在实际应用中，两者经常组合使用：
    
    1. Milvus（向量数据库）
       - 使用 Docker Volumes 持久化向量数据文件
       - 用于相似度搜索
    
    2. PostgreSQL（关系数据库）
       - 使用数据库持久化存储元数据
       - 用于精确查询和事务处理
    
    3. 组合使用
       - Milvus 找到相似的向量
       - PostgreSQL 查询详细的元数据
       - 两者互补，发挥各自优势
    """)

