import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    r = client.post("/auth", json={"login": "user1", "password": "1234", "repeat_password": "1234"})
    print("Auth response:", r.status_code, r.json())
    response = client.post("/login", data={"username": "user1", "password": "1234"})
    print("Login response:", response.status_code, response.json())
    data = response.json()
    return data["access_token"]

