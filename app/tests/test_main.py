import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


client = TestClient(app)

def test_get_projects_list():
    response = client.get("/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_project_not_found():
    response = client.get("/projects/999/info")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
