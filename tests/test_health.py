import settings


def test_health(client):
    res = client.get(f"/{settings.PROJECT_NAME}/health/")
    assert res.status_code == 200
