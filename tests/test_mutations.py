def gql(client, query, variables=None):
    r = client.post("/graphql", json={"query": query, "variables": variables or {}})
    return r.json()

def test_add_author(client):
    res = gql(client, """
        mutation {
          addAuthor(data: {name: "Оруэлл", country: "UK"}) { id name }
        }
    """)
    assert res["data"]["addAuthor"]["name"] == "Оруэлл"

def test_update_price(client):
    gql(client, 'mutation { addAuthor(data:{name:"A",country:"X"}){id} }')
    gql(client, 'mutation { addBook(data:{title:"B",year:2020,price:100,authorId:1}){id} }')
    res = gql(client, 'mutation { updatePrice(id:1, newPrice:250){ price } }')
    assert res["data"]["updatePrice"]["price"] == 250.0

def test_delete_book(client):
    gql(client, 'mutation { addAuthor(data:{name:"A",country:"X"}){id} }')
    gql(client, 'mutation { addBook(data:{title:"B",year:2020,price:100,authorId:1}){id} }')
    res = gql(client, 'mutation { deleteBook(id:1) }')
    assert res["data"]["deleteBook"] is True

def test_add_book(admin_client):
    admin_client.post("/graphql", json={
        "query": 'mutation { addAuthor(data:{name:"A", country:"X"}){id} }'
    })
    res = admin_client.post("/graphql", json={
        "query": 'mutation { addBook(data:{title:"B", year:2020, price:100, authorId:1}){id} }'
    }).json()
    assert res["data"]["addBook"]["id"] == 1
     