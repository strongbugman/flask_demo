from openapi_spec_validator import validate_v3_spec

from app import models as m
from app.extensions import apiman


def test_apiman():
    validate_v3_spec(apiman.specification)


def test_cat(client, db):
    # create
    res = client.post(f"/api/cats/")
    assert res.status_code == 400
    data = dict(name="丁丁", age=1)
    res = client.post(f"/api/cats/", json=data)
    assert res.status_code == 201
    for k, v in data.items():
        assert res.json[k] == v
    cat1_id = res.json["id"]
    data = dict(name="当当", age=2)
    res = client.post(f"/api/cats/", json=data)
    for k, v in data.items():
        assert res.json[k] == v
    cat2_id = res.json["id"]
    assert db.fetch(f"SELECT COUNT(*) FROM {m.Cat.__name__.lower()}")[0][0] == 2
    # get
    res = client.get(f"/api/cat/?id=-1")
    assert res.status_code == 400
    res = client.get(f"/api/cat/?id=id")
    assert res.status_code == 400
    res = client.get(f"/api/cat/")
    assert res.status_code == 400
    res = client.get(f"/api/cat/?id=100")
    assert res.status_code == 404
    res = client.get(f"/api/cat/?id={cat2_id}")
    assert res.status_code == 200
    for k, v in data.items():
        assert res.json[k] == v
    # update
    data["id"] = cat2_id
    data["age"] += 1
    res = client.put(f"/api/cat/", json=data)
    assert res.status_code == 200
    assert res.json["age"] == data["age"]
    # list
    res = client.get(f"/api/cats/")
    assert res.status_code == 200
    assert len(res.json["objects"]) == 2
    assert res.json["page"] == 1
    assert res.json["count"] == 20
    # delete
    res = client.delete(f"/api/cat/?id={cat1_id}")
    assert res.status_code == 204
    res = client.get(f"/api/cat/?id={cat1_id}")
    assert res.status_code == 404
