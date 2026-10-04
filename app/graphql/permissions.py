from functools import wraps

from graphql import GraphQLError
from strawberry.types import Info


def login_required(func):
    """Только для авторизованных."""
    @wraps(func)
    def wrapper(self, info: Info, *args, **kwargs):
        if not info.context.is_authenticated:
            raise GraphQLError("Authentication required")
        return func(self, info, *args, **kwargs)
    return wrapper


def admin_required(func):
    """Только для админов."""
    @wraps(func)
    def wrapper(self, info: Info, *args, **kwargs):
        if not info.context.is_admin:
            raise GraphQLError("Admin rights required")
        return func(self, info, *args, **kwargs)
    return wrapper