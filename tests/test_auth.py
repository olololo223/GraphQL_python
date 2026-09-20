def gql(client, query, variables=None):
    return client.post("/graphql", json={"query": query, "variables": variables or {}}).json()

def test_register(client):
    res = gql(client, 'mutation { register(email:"a@b.c", password:"12345"){ token role } }')
    assert res["data"]["register"]["role"] == "user"
    assert len(res["data"]["register"]["token"]) > 10

def test_duplicate_register(client):
    gql(client, 'mutation { register(email:"a@b.c", password:"12345"){ token } }')
    res = gql(client, 'mutation { register(email:"a@b.c", password:"12345"){ token } }')
    assert "errors" in res

def test_login(client):
    gql(client, 'mutation { register(email:"a@b.c", password:"12345"){ token } }')
    res = gql(client, 'mutation { login(email:"a@b.c", password:"12345"){ token role } }')
    assert res["data"]["login"]["role"] == "user"