import os

os.environ["DATABASE_URL"] = "sqlite://"  # in-memory, isolated from dev data

import pytest
from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import User
from app.security import auth_limiter, submit_limiter
from app.services.lessons import seed_lessons


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    auth_limiter.reset()
    submit_limiter.reset()
    with TestClient(app) as c:  # startup seeds the curriculum
        yield c


@pytest.fixture()
def auth(client):
    r = client.post("/api/v1/auth/register", json={"username": "ada", "email": "ada@example.com", "password": "password123"})
    assert r.status_code == 201
    return {"Authorization": "Bearer " + r.json()["access_token"]}


@pytest.fixture()
def admin(client):
    r = client.post("/api/v1/auth/register", json={"username": "boss", "email": "boss@example.com", "password": "password123"})
    with SessionLocal() as db:
        u = db.query(User).filter_by(username="boss").one()
        u.role = "admin"
        db.commit()
    return {"Authorization": "Bearer " + r.json()["access_token"]}
