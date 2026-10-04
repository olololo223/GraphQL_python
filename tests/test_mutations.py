def gql(client, query, variables=None):
    return client.post("/graphql", json={"query": query, "variables": variables or {}}).json()


def test_add_author(admin_client):
    res = gql(admin_client, """
        mutation {
          addAuthor(data: {name: "Оруэлл", country: "UK"}) { id name }
        }
    """)
    assert res["data"]["addAuthor"]["name"] == "Оруэлл"


def test_update_price(admin_client):
    gql(admin_client, 'mutation { addAuthor(data:{name:"A",country:"X"}){id} }')
    gql(admin_client, 'mutation { addBook(data:{title:"B",year:2020,price:100,authorId:1}){id} }')
    res = gql(admin_client, 'mutation { updatePrice(id:1, newPrice:250){ price } }')
    assert res["data"]["updatePrice"]["price"] == 250.0


def test_delete_book(admin_client):
    gql(admin_client, 'mutation { addAuthor(data:{name:"A",country:"X"}){id} }')
    gql(admin_client, 'mutation { addBook(data:{title:"B",year:2020,price:100,authorId:1}){id} }')
    res = gql(admin_client, 'mutation { deleteBook(id:1) }')
    assert res["data"]["deleteBook"] is True


def test_add_book(admin_client):
    gql(admin_client, 'mutation { addAuthor(data:{name:"A",country:"X"}){id} }')
    res = gql(admin_client, """
        mutation {
          addBook(data: {title: "Test", year: 2020, price: 100.0, authorId: 1}) {
            id title
          }
        }
    """)
    assert res["data"]["addBook"]["title"] == "Test"


def test_add_book_requires_admin(user_client):
    """Обычный user не может добавить книгу."""
    res = gql(user_client, """
        mutation {
          addBook(data: {title: "X", year: 2020, price: 100.0, authorId: 1}) {
            id
          }
        }
    """)
    assert "errors" in res
    assert "Admin" in res["errors"][0]["message"]


def test_add_book_requires_auth(client):
    """Без токена — тоже отказ."""
    res = gql(client, """
        mutation {
          addBook(data: {title: "X", year: 2020, price: 100.0, authorId: 1}) {
            id
          }
        }
    """)
    assert "errors" in res
    assert "Authentication" in res["errors"][0]["message"] or "Admin" in res["errors"][0]["message"]