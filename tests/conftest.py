import os

import pytest


def pytest_configure():
    os.environ["FLASK_ENV"] = "testing"
    os.environ["DEBUG"] = "True"


@pytest.fixture()
def app():
    from app import app

    yield app


@pytest.fixture()
def client(app):
    yield app.test_client()


@pytest.fixture(autouse=True)
def db(app):
    from app.extensions import db
    from app.models import MODELS

    for M in MODELS:
        db.execute(M.__db_define__)
    yield db
    for M in MODELS:
        db.execute(f"DROP TABLE {M.__name__.lower()}")
