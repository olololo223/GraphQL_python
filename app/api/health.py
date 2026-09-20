from fastapi import APIRouter
from sqlalchemy import text
from app.database import engine

router = APIRouter(tags=["system"])

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/ready")
def ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "db": "ok"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}