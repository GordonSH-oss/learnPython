"""使用 Python 标准库 sqlite3 练习连接和操作数据库。

运行：
    python3 playground.py

脚本会在当前目录创建 example.db。重复运行时会清空练习表中的旧数据，
因此每次都能看到相同的结果。
"""

import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("example.db")


def connect_database(database_path: str | Path = DATABASE_PATH) -> sqlite3.Connection:
    """创建数据库连接，并让查询结果支持按列名访问。"""
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables(connection: sqlite3.Connection) -> None:
    """创建用户表；IF NOT EXISTS 让该操作可以重复执行。"""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            age INTEGER NOT NULL CHECK (age >= 0),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()


def reset_users(connection: sqlite3.Connection) -> None:
    """只清空练习数据，保留表结构。"""
    connection.execute("DELETE FROM users")
    connection.commit()


def create_user(
    connection: sqlite3.Connection, name: str, email: str, age: int
) -> int:
    """插入用户并返回数据库生成的主键。"""
    cursor = connection.execute(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        (name, email, age),
    )
    connection.commit()
    return int(cursor.lastrowid)


def list_users(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    """按主键顺序查询所有用户。"""
    cursor = connection.execute(
        "SELECT id, name, email, age, created_at FROM users ORDER BY id"
    )
    return cursor.fetchall()


def find_user_by_email(
    connection: sqlite3.Connection, email: str
) -> sqlite3.Row | None:
    """使用参数化查询按邮箱查找用户。"""
    return connection.execute(
        "SELECT id, name, email, age FROM users WHERE email = ?",
        (email,),
    ).fetchone()


def update_user_age(
    connection: sqlite3.Connection, user_id: int, new_age: int
) -> bool:
    """更新年龄，返回是否找到了指定用户。"""
    cursor = connection.execute(
        "UPDATE users SET age = ? WHERE id = ?",
        (new_age, user_id),
    )
    connection.commit()
    return cursor.rowcount > 0


def delete_user(connection: sqlite3.Connection, user_id: int) -> bool:
    """删除用户，返回是否实际删除了一行。"""
    cursor = connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
    connection.commit()
    return cursor.rowcount > 0


def demonstrate_transaction(connection: sqlite3.Connection) -> None:
    """演示事务失败时回滚，避免只写入一半数据。"""
    try:
        with connection:
            connection.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                ("事务用户 A", "transaction@example.com", 20),
            )
            # email 有 UNIQUE 约束，第二次插入会失败，with 会自动回滚事务。
            connection.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                ("事务用户 B", "transaction@example.com", 21),
            )
    except sqlite3.IntegrityError as error:
        print(f"事务失败，已自动回滚: {error}")

    saved = find_user_by_email(connection, "transaction@example.com")
    assert saved is None, "事务没有完整回滚"


def print_users(connection: sqlite3.Connection) -> None:
    """输出当前用户列表。"""
    for user in list_users(connection):
        print(
            f"id={user['id']}, name={user['name']}, "
            f"email={user['email']}, age={user['age']}"
        )


def main() -> None:
    print(f"连接数据库: {DATABASE_PATH}")

    # context manager 负责异常时回滚事务；连接仍需在 finally 中显式关闭。
    connection = connect_database()
    try:
        create_tables(connection)
        reset_users(connection)

        alice_id = create_user(connection, "Alice", "alice@example.com", 25)
        bob_id = create_user(connection, "Bob", "bob@example.com", 30)

        print("\n创建后的数据:")
        print_users(connection)

        alice = find_user_by_email(connection, "alice@example.com")
        assert alice is not None
        print(f"\n按邮箱查询: {dict(alice)}")

        assert update_user_age(connection, alice_id, 26)
        assert delete_user(connection, bob_id)

        print("\n更新 Alice、删除 Bob 后:")
        print_users(connection)

        print("\n事务练习:")
        demonstrate_transaction(connection)

        users = list_users(connection)
        assert len(users) == 1
        assert users[0]["age"] == 26
        print("\n所有练习验证通过。")
    finally:
        connection.close()
        print("数据库连接已关闭。")


if __name__ == "__main__":
    main()
