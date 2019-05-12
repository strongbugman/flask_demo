def test_health(client):
    res = client.get(f"/health/")
    assert res.status_code == 200
