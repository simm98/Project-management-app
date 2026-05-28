import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope='session')
def sign_in():
    user = 'user1'
    r = client.post("/auth", json={"login": f"{user}", "password": "1234", "repeat_password": "1234"})
    print("Auth response:", r.status_code, r.json())
    return r.json()

@pytest.fixture(scope='session')
def login(sign_in):
    user = sign_in
    response = client.post("/login", data={"username": f"{user["login"]}", "password": "1234"})
    yield response
    print("Login response:", response.status_code, response.json())

@pytest.fixture(scope='session')
def auth_token(login):
    response = login.json()
    return response["access_token"]