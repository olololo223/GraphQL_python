import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app
import app.database as db_module
from app.models import User


@pytest.fixture(scope="function")
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    # Только эта подмена нужна — всё остальное берёт SessionLocal из app.database
    monkeypatch.setattr(db_module, "SessionLocal", TestingSession)

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def admin_client(client):
    """Регистрируем юзера и принудительно делаем его админом."""
    res = client.post("/graphql", json={
        "query": 'mutation { register(email:"admin@t.c", password:"12345"){ token role } }'
    }).json()
    token = res["data"]["register"]["token"]

    # Явно повышаем роль в БД
    with db_module.SessionLocal() as db:
        user = db.query(User).filter_by(email="admin@t.c").first()
        user.role = "admin"
        db.commit()

    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
def user_client(client):
    """Обычный user (не админ)."""
    # Первый — admin (регистрируем, но не используем)
    client.post("/graphql", json={
        "query": 'mutation { register(email:"admin@t.c", password:"12345"){ token } }'
    })
    # Второй — user
    res = client.post("/graphql", json={
        "query": 'mutation { register(email:"user@t.c", password:"12345"){ token role } }'
    }).json()
    token = res["data"]["register"]["token"]

    # Явно фиксируем роль user
    with db_module.SessionLocal() as db:
        u = db.query(User).filter_by(email="user@t.c").first()
        u.role = "user"
        db.commit()

    client.headers["Authorization"] = f"Bearer {token}"
    return client