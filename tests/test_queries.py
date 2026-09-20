def gql(client, query, variables=None):
    r = client.post("/graphql", json={"query": query, "variables": variables or {}})
    return r.json()

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_books_empty(client):
    res = gql(client, "{ books { id title } }")
    assert res["data"]["books"] == []

def test_add_and_list_book(client):
    gql(client, """
        mutation {
          addAuthor(data: {name: "Test", country: "RU"}) { id }
        }
    """)
    gql(client, """
        mutation {
          addBook(data: {title: "T1", year: 2020, price: 100, authorId: 1}) { id }
        }
    """)
    res = gql(client, "{ books { title year } }")
    assert res["data"]["books"] == [{"title": "T1", "year": 2020}]