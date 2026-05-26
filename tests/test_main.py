import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_projects_list(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/projects", json={
        "name": "Proyecto Demo",
        "description": "Este es un proyecto de prueba"
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Proyecto Demo"

def test_get_project_not_found(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/projects/999/info", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
