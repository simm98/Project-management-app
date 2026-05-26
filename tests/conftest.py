import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    client.post("/auth", data={"login": "user", "password": "1234", "repeat_password": "1234"})
    response = client.post("/login", data={"username": "user", "password": "1234"})
    print(response)
    data = response.json()
    print(data)
    return data["access_token"]

