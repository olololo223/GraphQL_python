import strawberry

from app.database import SessionLocal
from app.graphql.types import AuthorListResult, AuthorType, BookListResult, BookType
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
    def books(
        self,
        year_from: int | None = None,
        year_to: int | None = None,
        search: str | None = None,
        author_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = "id",
        limit: int = 20,
        offset: int = 0,
    ) -> BookListResult:
        filters = {
            "year_from": year_from,
            "year_to": year_to,
            "search": search,
            "author_id": author_id,
            "min_price": min_price,
            "max_price": max_price,
        }
        with SessionLocal() as db:
            svc = BookService(db)
            items = svc.list(**filters, sort_by=sort_by, limit=limit, offset=offset)
            total = svc.count(**filters)
            return BookListResult(
                items=[to_book(b) for b in items],
                total=total,
                limit=limit,
                offset=offset,
            )

    @strawberry.field
    def book(self, id: int) -> BookType | None:
        with SessionLocal() as db:
            b = BookService(db).get(id)
            return to_book(b) if b else None

    @strawberry.field
    def authors(
        self,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AuthorListResult:
        with SessionLocal() as db:
            svc = AuthorService(db)
            items = svc.list(search=search, limit=limit, offset=offset)
            total = svc.count(search=search)
            return AuthorListResult(
                items=[to_author(a) for a in items],
                total=total,
                limit=limit,
                offset=offset,
            )

    @strawberry.field
    def author(self, id: int) -> AuthorType | None:
        with SessionLocal() as db:
            a = AuthorService(db).get(id)
            return to_author(a) if a else None