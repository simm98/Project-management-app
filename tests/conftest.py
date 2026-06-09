import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="session")
def user_data():
    return {"username": 'default_user', "password": "1234"}


@pytest.fixture(scope="session")
def sign_in(user_data):
    def _register():
        r = client.post(
            "/auth", 
            json={"login": user_data["username"], 
                  "password": user_data["password"], 
                  "repeat_password": user_data["password"]}
                  )
        print("Auth response:", r.status_code, r.json())
        return r
    return _register


@pytest.fixture(scope="session")
def login(user_data):
    def _login():
        response = client.post(
            "/login", 
            data={"username": user_data["username"],
                  "password": user_data["password"]}
                  )
        print("Login response:", response.status_code, response.json())
        return response
    return _login


@pytest.fixture(scope="session")
def auth_token(login):
    response = login()
    data = response.json()
    return data["access_token"]
