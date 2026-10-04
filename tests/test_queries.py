def gql(client, query, variables=None):
    return client.post("/graphql", json={"query": query, "variables": variables or {}}).json()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_books_empty(client):
    res = gql(client, "{ books { items { id title } total } }")
    assert res["data"]["books"]["items"] == []
    assert res["data"]["books"]["total"] == 0


def test_add_and_list_book(admin_client):
    gql(admin_client, 'mutation { addAuthor(data:{name:"Test",country:"RU"}){id} }')
    gql(admin_client, """
        mutation {
          addBook(data: {title: "T1", year: 2020, price: 100, authorId: 1}) { id }
        }
    """)
    res = gql(admin_client, "{ books { items { title year } total } }")
    assert res["data"]["books"]["total"] == 1
    assert res["data"]["books"]["items"][0]["title"] == "T1"