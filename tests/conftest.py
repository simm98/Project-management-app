import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    client.post("/auth", json={
        "login": "user",
        "password": "1234",
        "repeat_password": "1234"
    })
    response = client.post("/login", json={
        "login": "user",
        "password": "1234"
    })
    data = response.json()
    return data["access_token"]

