
import strawberry
from strawberry.types import Info

from app.database import SessionLocal
from app.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from app.graphql.permissions import admin_required
from app.graphql.queries import to_author, to_book
from app.graphql.types import AuthorInput, AuthorType, AuthPayload, BookInput, BookType
from app.models import User
from app.security import create_token, hash_password, verify_password
from app.services.author_service import AuthorService
from app.services.book_service import BookService


@strawberry.type
class Mutation:
    # ============ AUTH (публичные) ============
    @strawberry.mutation
    def register(self, email: str, password: str) -> AuthPayload:
        with SessionLocal() as db:
            if db.query(User).filter_by(email=email).first():
                raise EmailAlreadyExistsError("Email already exists")
            # Первый пользователь — админ (удобно для демо)
            is_first = db.query(User).count() == 0
            role = "admin" if is_first else "user"
            user = User(
                email=email,
                hashed_password=hash_password(password),
                role=role,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return AuthPayload(token=create_token(user.id, user.role), role=user.role)

    @strawberry.mutation
    def login(self, email: str, password: str) -> AuthPayload:
        with SessionLocal() as db:
            user = db.query(User).filter_by(email=email).first()
            if not user or not verify_password(password, user.hashed_password):
                raise InvalidCredentialsError("Invalid credentials")
            return AuthPayload(token=create_token(user.id, user.role), role=user.role)

    # ============ AUTHORS (только admin) ============
    @strawberry.mutation
    @admin_required
    def add_author(self, info: Info, data: AuthorInput) -> AuthorType:
        with SessionLocal() as db:
            a = AuthorService(db).create(data.name, data.country)
            return to_author(a)

    @strawberry.mutation
    @admin_required
    def update_author(self, info: Info, id: int, data: AuthorInput) -> AuthorType | None:
        with SessionLocal() as db:
            a = AuthorService(db).update(id, data.name, data.country)
            return to_author(a) if a else None

    @strawberry.mutation
    @admin_required
    def delete_author(self, info: Info, id: int) -> bool:
        with SessionLocal() as db:
            return AuthorService(db).delete(id)

    # ============ BOOKS (только admin) ============
    @strawberry.mutation
    @admin_required
    def add_book(self, info: Info, data: BookInput) -> BookType:
        with SessionLocal() as db:
            b = BookService(db).create(data.title, data.year, data.price, data.author_id)
            return to_book(b)

    @strawberry.mutation
    @admin_required
    def update_book(self, info: Info, id: int, data: BookInput) -> BookType | None:
        with SessionLocal() as db:
            b = BookService(db).update(id, data.title, data.year, data.price, data.author_id)
            return to_book(b) if b else None

    @strawberry.mutation
    @admin_required
    def update_price(self, info: Info, id: int, new_price: float) -> BookType | None:
        with SessionLocal() as db:
            b = BookService(db).update_price(id, new_price)
            return to_book(b) if b else None

    @strawberry.mutation
    @admin_required
    def delete_book(self, info: Info, id: int) -> bool:
        with SessionLocal() as db:
            return BookService(db).delete(id)