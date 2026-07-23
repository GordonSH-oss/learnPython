"""A transaction either transfers the complete amount or changes nothing."""

import sqlite3
from tempfile import TemporaryDirectory


def main() -> None:
    with TemporaryDirectory() as directory, sqlite3.connect(f"{directory}/bank.db") as db:
        db.executescript(
            """
            CREATE TABLE accounts(id INTEGER PRIMARY KEY, balance INTEGER NOT NULL CHECK(balance >= 0));
            INSERT INTO accounts VALUES (1, 1000), (2, 500);
            """
        )
        try:
            with db:
                db.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (200, 1))
                db.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (200, 2))
                db.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (9999, 2))
        except sqlite3.IntegrityError as error:
            print("rolled back:", error)
        print(db.execute("SELECT id, balance FROM accounts ORDER BY id").fetchall())


if __name__ == "__main__":
    main()

