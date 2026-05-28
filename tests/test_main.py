import pytest
from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_sign_in(user_data, sign_in):
    user_data["username"] = 'user1'
    response = sign_in()
    assert response.json()["login"] == "user1"

def test_login(user_data, login):
    user_data["username"] = 'user1'
    response = login()
    assert response.status_code == 200
    assert "access_token" in response.json()

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
    assert response.status_code == 200
    project_id = response.json()["id"]
    response_del = client.delete(f"/projects/{project_id}", headers=headers)
    assert response_del.status_code == 200
    assert response_del.json()["status"] == "deleted"

def test_get_project_documents_not_found(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/projects/1/documents",headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Documents not found"

def test_sign_in_other_user(user_data, sign_in):
    user_data["username"] = 'user2'
    response = sign_in()
    assert response.json()["login"] == "user2"

def test_login_other_user(user_data, login):
    user_data["username"] = 'user2'
    response = login()
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_proyect_list_status_code(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/projects", headers=headers)
    assert response.status_code == 200

def test_create_project_other_user(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/projects", json={"name": "Proyecto Demo User 2", "description": "Este es un proyecto de prueba"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Proyecto Demo User 2"

def test_upload_document(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    file_content = b"Contenido de prueba"
    file = io.BytesIO(file_content)
    response = client.post("/projects/1/documents",headers=headers,files={"file": ("test.txt", file, "text/plain")})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["filename"] == "test.txt"

def test_get_project_documents(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/projects/1/documents",headers=headers)
    assert response.status_code == 200
    data = response.json()
    documents = data["documents"]
    assert documents["filename"] == "test.txt"

def test_download_project_document_by_id(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    download_resp = client.get("/document/1",headers=headers)
    file_content = b"Contenido de prueba"
    assert download_resp.status_code == 200
    assert download_resp.content == file_content