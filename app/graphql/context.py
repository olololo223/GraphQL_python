from dataclasses import dataclass

from fastapi import Request
from strawberry.fastapi import BaseContext

from app.database import SessionLocal
from app.models import User
from app.security import decode_token


@dataclass
class GraphQLContext(BaseContext):
    request: Request
    user: User | None = None
    db_session_factory = SessionLocal

    @property
    def is_authenticated(self) -> bool:
        return self.user is not None

    @property
    def is_admin(self) -> bool:
        return self.user is not None and self.user.role == "admin"


async def get_context(request: Request) -> GraphQLContext:
    """Извлекаем токен из заголовка Authorization: Bearer <token>."""
    ctx = GraphQLContext(request=request)

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            payload = decode_token(token)
            user_id = int(payload["sub"])
            with SessionLocal() as db:
                user = db.get(User, user_id)
                if user:
                    # Отсоединяем от сессии, чтобы использовать в resolver'ах
                    db.expunge(user)
                    ctx.user = user
        except (ValueError, KeyError):
            pass  # невалидный токен — просто аноним

    return ctx