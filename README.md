# BookStore API

GraphQL API для управления книжным каталогом (FastAPI + Strawberry + SQLAlchemy + SQLite).

## Стек
- **API:** FastAPI + Strawberry GraphQL
- **БД:** SQLite (dev) / PostgreSQL (prod-ready)
- **ORM:** SQLAlchemy 2.0 + Alembic
- **Auth:** JWT (python-jose + passlib)
- **Tests:** pytest + coverage
- **CI:** GitHub Actions

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

cp .env.example .env
alembic upgrade head

uvicorn app.main:app --reload
```

- GraphiQL: http://127.0.0.1:8000/graphql
- Health:   http://127.0.0.1:8000/health
- Swagger:  http://127.0.0.1:8000/docs

## Тесты

```bash
pytest --cov=app
```

## Примеры запросов

```graphql
query {
  books(yearFrom: 1900) {
    title price
    author { name country }
  }
}
```

## Архитектура

Presentation (GraphQL) → Services → Models (SQLAlchemy) → SQLite/Postgres