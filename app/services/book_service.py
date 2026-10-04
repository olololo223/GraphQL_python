from sqlalchemy.orm import Session

from app.models import Book


class BookService:
    def __init__(self, db: Session):
        self.db = db

    def list(
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
    ):
        q = self.db.query(Book)
        if year_from:
            q = q.filter(Book.year >= year_from)
        if year_to:
            q = q.filter(Book.year <= year_to)
        if search:
            q = q.filter(Book.title.ilike(f"%{search}%"))
        if author_id:
            q = q.filter(Book.author_id == author_id)
        if min_price is not None:
            q = q.filter(Book.price >= min_price)
        if max_price is not None:
            q = q.filter(Book.price <= max_price)

        sort_column = {
            "id": Book.id,
            "title": Book.title,
            "year": Book.year,
            "price": Book.price,
        }.get(sort_by, Book.id)
        q = q.order_by(sort_column)

        return q.offset(offset).limit(limit).all()

    def count(self, **filters) -> int:
        # упрощённо — тот же запрос без offset/limit
        return len(self.list(**{**filters, "limit": 100000, "offset": 0}))

    def get(self, book_id: int) -> Book | None:
        return self.db.get(Book, book_id)

    def create(self, title: str, year: int, price: float, author_id: int) -> Book:
        book = Book(title=title, year=year, price=price, author_id=author_id)
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def update(self, book_id: int, title: str, year: int, price: float, author_id: int) -> Book | None:
        book = self.get(book_id)
        if not book:
            return None
        book.title = title
        book.year = year
        book.price = price
        book.author_id = author_id
        self.db.commit()
        self.db.refresh(book)
        return book

    def update_price(self, book_id: int, new_price: float) -> Book | None:
        book = self.get(book_id)
        if not book:
            return None
        book.price = new_price
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book_id: int) -> bool:
        book = self.get(book_id)
        if not book:
            return False
        self.db.delete(book)
        self.db.commit()
        return True