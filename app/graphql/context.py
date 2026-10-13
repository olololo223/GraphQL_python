from dataclasses import dataclass
from typing import Optional
from fastapi import Request
from strawberry.fastapi import BaseContext
from app.security import decode_token
import app.database
from app.models import User


@dataclass
class GraphQLContext(BaseContext):
    request: Request
    user: Optional[User] = None

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
            with app.database.SessionLocal() as db:
                user = db.get(User, user_id)
                if user:
                    db.expunge(user)
                    ctx.user = user
        except (ValueError, KeyError):
            pass

    return ctx