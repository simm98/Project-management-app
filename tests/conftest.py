import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def user_data():
    return {"username" : 'default_user', "password": "1234"}

@pytest.fixture
def sign_in(user_data):
    def _register():
        r = client.post("/auth", json={"login": f"{user_data["username"]}", "password": f"{user_data["password"]}", "repeat_password": f"{user_data["password"]}"})
        print("Auth response:", r.status_code, r.json())
        return r.json
    return _register

@pytest.fixture
def login(user_data):
    def _login():
        response = client.post("/login", data={"username": f"{user_data["username"]}", "password": f"{user_data["password"]}"})
        print("Login response:", response.status_code, response.json())
        return response
    return _login

@pytest.fixture(scope='session')
def auth_token(login):
    response = login().json()
    return response["access_token"]