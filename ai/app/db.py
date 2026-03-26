from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from pgvector.psycopg import register_vector
from app.settings import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    connect_args={
        "connect_timeout": 5,
    },
)


@event.listens_for(engine, "connect")
def _on_connect(dbapi_connection, _connection_record):
    register_vector(dbapi_connection)

    prev_autocommit = dbapi_connection.autocommit
    try:
        dbapi_connection.autocommit = True
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Seoul'")
    finally:
        dbapi_connection.autocommit = prev_autocommit


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
