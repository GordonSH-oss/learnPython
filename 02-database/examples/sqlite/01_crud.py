"""SQLite DB-API: schema, parameterized CRUD, joins and row factories."""

import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory


SCHEMA = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0)
);
"""


def main() -> None:
    with TemporaryDirectory() as directory:
        database = Path(directory) / "lesson.db"
        with sqlite3.connect(database) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript(SCHEMA)
            connection.execute("INSERT INTO users(email) VALUES (?)", ("a@example.com",))
            user_id = connection.execute("SELECT last_insert_rowid()").fetchone()[0]
            connection.executemany(
                "INSERT INTO orders(user_id, amount_cents) VALUES (?, ?)",
                [(user_id, 1200), (user_id, 800)],
            )
            row = connection.execute(
                """
                SELECT users.email, COUNT(orders.id) AS order_count,
                       COALESCE(SUM(orders.amount_cents), 0) AS total_cents
                FROM users LEFT JOIN orders ON orders.user_id = users.id
                WHERE users.id = ? GROUP BY users.id, users.email
                """,
                (user_id,),
            ).fetchone()
            print(dict(row))


if __name__ == "__main__":
    main()

