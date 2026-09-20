import strawberry
from typing import Optional
from app.graphql.types import BookType, AuthorType, AuthPayload, BookInput, AuthorInput
from app.graphql.queries import to_book, to_author
from app.services.book_service import BookService
from app.services.author_service import AuthorService
from app.security import create_token, hash_password, verify_password
from app.database import SessionLocal
from app.models import User

@strawberry.type
class Mutation:
    # ---- Auth ----
    @strawberry.mutation
    def register(self, email: str, password: str) -> AuthPayload:
        with SessionLocal() as db:
            if db.query(User).filter_by(email=email).first():
                raise Exception("Email already exists")
            user = User(email=email, hashed_password=hash_password(password), role="user")
            db.add(user)
            db.commit()
            db.refresh(user)
            return AuthPayload(token=create_token(user.id, user.role), role=user.role)

    @strawberry.mutation
    def login(self, email: str, password: str) -> AuthPayload:
        with SessionLocal() as db:
            user = db.query(User).filter_by(email=email).first()
            if not user or not verify_password(password, user.hashed_password):
                raise Exception("Invalid credentials")
            return AuthPayload(token=create_token(user.id, user.role), role=user.role)

    # ---- Authors ----
    @strawberry.mutation
    def add_author(self, data: AuthorInput) -> AuthorType:
        with SessionLocal() as db:
            a = AuthorService(db).create(data.name, data.country)
            return to_author(a)

    # ---- Books ----
    @strawberry.mutation
    def add_book(self, data: BookInput) -> BookType:
        with SessionLocal() as db:
            b = BookService(db).create(data.title, data.year, data.price, data.author_id)
            return to_book(b)

    @strawberry.mutation
    def update_price(self, id: int, new_price: float) -> Optional[BookType]:
        with SessionLocal() as db:
            b = BookService(db).update_price(id, new_price)
            return to_book(b) if b else None

    @strawberry.mutation
    def delete_book(self, id: int) -> bool:
        with SessionLocal() as db:
            return BookService(db).delete(id)