import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_project(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/projects", json={"name": "Proyecto Demo", "description": "Este es un proyecto de prueba"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Proyecto Demo"

def test_get_project_not_found(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/projects/999/info", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_get_proyect_list_status_code(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/projects", headers=headers)
    assert response.status_code == 200

def test_get_project_by_id(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/projects/1/info", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == "1"
