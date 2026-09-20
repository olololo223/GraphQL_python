from sqlalchemy.orm import Session

from app.models import Book


class BookService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, year_from: int | None = None, limit: int = 20, offset: int = 0):
        q = self.db.query(Book)
        if year_from:
            q = q.filter(Book.year >= year_from)
        return q.order_by(Book.id).offset(offset).limit(limit).all()

    def get(self, book_id: int) -> Book | None:
        return self.db.get(Book, book_id)

    def create(self, title: str, year: int, price: float, author_id: int) -> Book:
        book = Book(title=title, year=year, price=price, author_id=author_id)
        self.db.add(book)
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