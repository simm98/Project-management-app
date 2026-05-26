import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    r = client.post("/auth", data={"login": "user", "password": "1234", "repeat_password": "1234"})
    print("Auth response:", r.status_code, r.json())
    response = client.post("/login", data={"username": "user", "password": "1234"})
    data = response.json()
    print(data)
    return data["access_token"]

