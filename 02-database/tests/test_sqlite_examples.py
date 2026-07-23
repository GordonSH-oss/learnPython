import sqlite3


def test_foreign_key_and_unique_constraints_are_enforced():
    with sqlite3.connect(":memory:") as db:
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL)")
        db.execute("CREATE TABLE posts(id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id))")
        db.execute("INSERT INTO users(email) VALUES (?)", ("a@example.com",))
        try:
            db.execute("INSERT INTO users(email) VALUES (?)", ("a@example.com",))
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("duplicate email should fail")
        try:
            db.execute("INSERT INTO posts(user_id) VALUES (?)", (999,))
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("invalid foreign key should fail")


def test_context_manager_rolls_back_an_failed_transaction():
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE accounts(balance INTEGER NOT NULL CHECK(balance >= 0))")
        db.execute("INSERT INTO accounts VALUES (100)")
        db.commit()
        try:
            with db:
                db.execute("UPDATE accounts SET balance = balance - 50")
                db.execute("UPDATE accounts SET balance = balance - 100")
        except sqlite3.IntegrityError:
            pass
        assert db.execute("SELECT balance FROM accounts").fetchone()[0] == 100
