from sqlalchemy.orm import Session

from app.models import Author


class AuthorService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, search: str | None = None, limit: int = 50, offset: int = 0):
        q = self.db.query(Author)
        if search:
            q = q.filter(Author.name.ilike(f"%{search}%"))
        return q.order_by(Author.id).offset(offset).limit(limit).all()

    def count(self, search: str | None = None) -> int:
        q = self.db.query(Author)
        if search:
            q = q.filter(Author.name.ilike(f"%{search}%"))
        return q.count()

    def get(self, author_id: int) -> Author | None:
        return self.db.get(Author, author_id)

    def create(self, name: str, country: str) -> Author:
        author = Author(name=name, country=country)
        self.db.add(author)
        self.db.commit()
        self.db.refresh(author)
        return author

    def update(self, author_id: int, name: str, country: str) -> Author | None:
        author = self.get(author_id)
        if not author:
            return None
        author.name = name
        author.country = country
        self.db.commit()
        self.db.refresh(author)
        return author

    def delete(self, author_id: int) -> bool:
        author = self.get(author_id)
        if not author:
            return False
        self.db.delete(author)
        self.db.commit()
        return True