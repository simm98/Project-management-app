import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def users():
    return {'user' : '-'}

@pytest.fixture(scope='session')
def sign_in(users):
    r = client.post("/auth", json={"login": f"{users["user"]}", "password": "1234", "repeat_password": "1234"})
    print("Auth response:", r.status_code, r.json())
    return r.json()

@pytest.fixture(scope='session')
def login(users):
    response = client.post("/login", data={"username": f"{users["user"]}", "password": "1234"})
    yield response
    print("Login response:", response.status_code, response.json())

@pytest.fixture(scope='session')
def auth_token(login):
    response = login.json()
    return response["access_token"]