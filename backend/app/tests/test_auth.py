def test_login_requires_valid_credentials(client, db):
    r = client.post("/api/v1/auth/login", json={"email": "no@existe.com", "password": "x" * 12})
    assert r.status_code == 401
