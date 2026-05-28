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
    assert response.json()["id"] == 1

def test_update_project(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.put("/projects/1/info", json={"name": "Proyecto Demo Update", "description": "Este es un proyecto de prueba actualizado"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Proyecto Demo Update"
    assert response.json()["description"] == "Este es un proyecto de prueba actualizado"

def test_delete_project(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/projects", json={"name": "Proyecto Demo Delete", "description": "Este es un proyecto de prueba para borrar"}, headers=headers)
    response = client.delete("/projects/2")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

def test_get_project_access(auth_token_other_user):
    headers = {"Authorization": f"Bearer {auth_token_other_user}"}
    response = client.get("/projects/1/info", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"