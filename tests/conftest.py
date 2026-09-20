import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.database as db_module
from app.database import Base
from app.main import app


@pytest.fixture(scope="function")
def client(monkeypatch):
    """Изолированная SQLite in-memory на каждый тест."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    # подменяем SessionLocal во всех модулях, где он используется
    monkeypatch.setattr(db_module, "SessionLocal", TestingSession)
    import app.graphql.mutations as m
    import app.graphql.queries as q
    monkeypatch.setattr(q, "SessionLocal", TestingSession)
    monkeypatch.setattr(m, "SessionLocal", TestingSession)

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(engine)
    engine.dispose()