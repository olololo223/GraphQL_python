
import strawberry

from app.database import SessionLocal
from app.graphql.types import AuthorType, BookType
from app.services.author_service import AuthorService
from app.services.book_service import BookService


def to_author(a, include_books: bool = True) -> AuthorType:
    return AuthorType(
        id=a.id,
        name=a.name,
        country=a.country,
        books=[to_book(b) for b in a.books] if include_books else [],
    )

def to_book(b) -> BookType:
    return BookType(
        id=b.id,
        title=b.title,
        year=b.year,
        price=b.price,
        author=to_author(b.author, include_books=False),
    )

@strawberry.type
class Query:
    @strawberry.field
    def books(self, year_from: int | None = None, limit: int = 20, offset: int = 0) -> list[BookType]:
        with SessionLocal() as db:
            return [to_book(b) for b in BookService(db).list(year_from, limit, offset)]

    @strawberry.field
    def book(self, id: int) -> BookType | None:
        with SessionLocal() as db:
            b = BookService(db).get(id)
            return to_book(b) if b else None

    @strawberry.field
    def authors(self) -> list[AuthorType]:
        with SessionLocal() as db:
            return [to_author(a) for a in AuthorService(db).list()]

    @strawberry.field
    def author(self, id: int) -> AuthorType | None:
        with SessionLocal() as db:
            a = AuthorService(db).get(id)
            return to_author(a) if a else None