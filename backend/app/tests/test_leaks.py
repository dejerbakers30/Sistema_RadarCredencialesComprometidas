def test_kpis_endpoint_requires_permission(client):
    r = client.get("/api/v1/leaks/kpis")
    assert r.status_code == 401  # sin token
