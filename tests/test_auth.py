def gql(client, query, variables=None):
    return client.post("/graphql", json={"query": query, "variables": variables or {}}).json()


def test_register(client):
    """Первый зарегистрированный — admin."""
    res = gql(client, 'mutation { register(email:"a@b.c", password:"12345"){ token role } }')
    assert res["data"]["register"]["role"] == "admin"   # ← было "user"
    assert len(res["data"]["register"]["token"]) > 10


def test_second_register_is_user(client):
    """Второй зарегистрированный — user."""
    gql(client, 'mutation { register(email:"a@b.c", password:"12345"){ token } }')
    res = gql(client, 'mutation { register(email:"b@b.c", password:"12345"){ token role } }')
    assert res["data"]["register"]["role"] == "user"


def test_duplicate_register(client):
    gql(client, 'mutation { register(email:"a@b.c", password:"12345"){ token } }')
    res = gql(client, 'mutation { register(email:"a@b.c", password:"12345"){ token } }')
    assert "errors" in res


def test_login(client):
    gql(client, 'mutation { register(email:"a@b.c", password:"12345"){ token } }')
    res = gql(client, 'mutation { login(email:"a@b.c", password:"12345"){ token role } }')
    assert res["data"]["login"]["role"] == "admin"   # ← было "user"