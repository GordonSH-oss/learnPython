"""SQLAlchemy 2.x Core: typed table description and explicit transactions."""

from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, insert, select


def main() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    metadata = MetaData()
    users = Table(
        "users", metadata,
        Column("id", Integer, primary_key=True),
        Column("email", String(320), unique=True, nullable=False),
    )
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(insert(users), [{"email": "a@example.com"}, {"email": "b@example.com"}])
    with engine.connect() as connection:
        statement = select(users).where(users.c.email.like("%@example.com")).order_by(users.c.id)
        print([dict(row._mapping) for row in connection.execute(statement)])


if __name__ == "__main__":
    main()

