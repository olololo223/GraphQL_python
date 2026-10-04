from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter

# Импортируем модели, чтобы Base их увидел (для create_all при DEBUG)
from app import models  # noqa
from app.api.health import router as health_router
from app.config import settings
from app.database import Base, engine
from app.graphql.context import get_context
from app.graphql.schema import schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.DEBUG:
        # автосоздание таблиц в dev (в prod — только alembic)
        Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")



app.include_router(
    GraphQLRouter(
        schema,
        context_getter=get_context,
        graphql_ide="graphiql" if settings.DEBUG else None,
    ),
    prefix="/graphql",
)
app.include_router(health_router)

@app.get("/")
def root():
    return FileResponse("app/static/index.html")
