
import strawberry


@strawberry.type
class AuthorType:
    id: int
    name: str
    country: str
    books: list["BookType"]

@strawberry.type
class BookType:
    id: int
    title: str
    year: int
    price: float
    author: AuthorType

@strawberry.type
class AuthPayload:
    token: str
    role: str

@strawberry.input
class BookInput:
    title: str
    year: int
    price: float
    author_id: int

@strawberry.input
class AuthorInput:
    name: str
    country: str

@strawberry.type
class BookListResult:
    items: list[BookType]
    total: int
    limit: int
    offset: int

@strawberry.type
class AuthorListResult:
    items: list[AuthorType]
    total: int
    limit: int
    offset: int