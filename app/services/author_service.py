from sqlalchemy.orm import Session
from app.models import Author

class AuthorService:
    def __init__(self, db: Session):
        self.db = db

    def list(self):
        return self.db.query(Author).order_by(Author.id).all()

    def get(self, author_id: int) -> Author | None:
        return self.db.get(Author, author_id)

    def create(self, name: str, country: str) -> Author:
        author = Author(name=name, country=country)
        self.db.add(author)
        self.db.commit()
        self.db.refresh(author)
        return author