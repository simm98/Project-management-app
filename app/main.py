import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import database, models, schemas, crud
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.services.s3_service import upload_file, download_file
from dotenv import load_dotenv
app = FastAPI()
load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
UPLOAD_DIR = os.getenv("UPLOAD_DIR")
SECRET_KEY = os.getenv("SECRET_KEY")  
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ORM_ENABLE = os.getenv("ORM_ENABLE")
os.makedirs(UPLOAD_DIR, exist_ok=True)

database.init_db()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido", headers={"WWW-Authenticate": "Bearer"})
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido", headers={"WWW-Authenticate": "Bearer"})
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado", headers={"WWW-Authenticate": "Bearer"})
    return user


@app.post("/auth", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Da de alta un usuario nuevo a la base de datos.
    
    -Parametros:

        user: datos de ususario a registrar con "nombre de usuario", "contraseña" y "contraseña repetida".

        db: llama a la sesión de la base de datos.

    """
    if user.password != user.repeat_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    db_user = crud.get_user_by_login(db, user.login)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db, user)


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login de usuario.

    -Parametros:

        from_data: datos de ususario para ingresar al login "nombre de usuario" y "contraseña".

        db: llama a la sesión de la base de datos.
    
    -Retorno: 

        retorna JSON con TOKEN de accesso para todas las operaciones.
    
    """
    user = db.query(models.User).filter(models.User.login == form_data.username).first()
    if not user or user.password != form_data.password:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/projects", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Creación de un proyecto nuevo.

    -Parametros:

        project: manda el esquema de creación de proyectos para un proyecto nuevo.

        db: llama a la sesión de la base de datos.

        current_user: llama al usuario activo para la base de datos.

    -Retorno: 

        retorna objeto de projecto creado con el esquema de respuesta del proyecto.
    """
    return crud.create_project(db, project, current_user)


@app.get("/projects", response_model=list[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Ver projectos disponibles para usuario.

    -Parametros:

        db: llama a la sesión de la base de datos.

        current_user: llama al usuario activo para la base de datos.

    -Retorno: 

        retorna lista de projectos disponibles para usuario.
    """
    return crud.get_projects_by_user(db, current_user.id)


@app.get("/projects/{project_id}/info", response_model=schemas.ProjectResponse)
def get_project_details(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Ver detalles de un projecto disponible para usuario.

    -Parametros:

        project_id: id del proyecto.

        db: llama a la sesión de la base de datos.

        current_user: llama al usuario activo para la base de datos.

    -Retorno: 

        retorna detalles de objeto de projecto disponible para usuario.
    """
    project = crud.get_projects_details_by_user(db, project_id)
    if not project :
        raise HTTPException(status_code=404, detail='Project not found')
    if current_user.id != project.owner_id:
        if current_user not in project.users:
            raise HTTPException(status_code=403, detail="Access denied")
    return project


@app.put("/projects/{project_id}/info", response_model=schemas.ProjectResponse)
def update_project_details(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Actualizar detalles de un projecto disponible para usuario.

    -Parametros:

        project_id: id del proyecto.

        project_update: cadena de detalles para actualziar de un proyecto con "nombre nuevo" y "descripción nueva".

        db: llama a la sesión de la base de datos.

        current_user: llama al usuario activo para la base de datos.

    -Retorno: 

        retorna proyecto actualizado disponible para usuario.
    """
    project = crud.update_projects_details_by_user(db, project_id, project_update, current_user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Borra un projecto.

    -Parametros:

        project_id: id del proyecto.

        db: llama a la sesión de la base de datos.

        current_user: llama al usuario activo para la base de datos.

    -Acción: 

        Borra proyecto si usuario es el owner del proyecto.
    """
    project = crud.get_projects_details_by_user(db, project_id)
    if not project :
        raise HTTPException(status_code=404, detail='Project not found')
    if current_user.id == project.owner_id: 
        crud.delete_project(db, project_id)
        return {"project_id": project_id, "status": "deleted"}
    else: 
        raise HTTPException(status_code=403, detail="Access denied")

   
@app.get("/projects/{project_id}/documents", response_model=schemas.ProjectDocumentsResponse)
def get_project_documents(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Ve documentos de un projecto disponible para usuario.

    -Parametros:

        project_id: id del proyecto.

        db: llama a la sesión de la base de datos.

        current_user: llama al usuario activo para la base de datos.

    -Retorno: 

        retorna JSON con documentos de proyecto disponible para usuario.
    """
    documents_content = crud.get_project_documents(db, project_id)
    owner_id_ver = crud.get_projects_details_by_user(db, project_id).owner_id
    if not documents_content:
        raise HTTPException(status_code=404, detail='Documents not found')
    if current_user.id != owner_id_ver:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"documents": documents_content}


@app.post("/projects/{project_id}/documents", response_model=schemas.DocumentResponse)
def upload_document(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Carga documento en projecto disponible para usuario.

    -Parametros:

        project_id: id del proyecto.

        file: Función para cargar archivo o documento a la base de datos (UploadFile de FastAPI).

        db: llama a la sesión de la base de datos.

        current_user: llama al usuario activo para la base de datos.

    -Retorno: 

        retorna objeto de documento cargado en proyecto.
    """
    project = crud.get_projects_details_by_user(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    document = crud.add_document_to_project(db, project_id, file.filename, file.content_type, file_path)
    if not document:
        raise HTTPException(status_code=400, detail="Could not add document")
    with open(file_path, "rb") as f:
        upload_file(f, f"uploads/project_{project_id}/document_{document.id}/{file.filename}")
    return document


@app.get("/document/{document_id}")
def get_download_document(document_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Descarga un documento de projecto disponible para usuario.

    -Parametros:

        document_id: id del documento.

        db: llama a la sesión de la base de datos.

        current_user: llama al usuario activo para la base de datos.

    -Retorno: 

        retorna descarga de documento cargado en proyecto.
    """
    document = crud.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    project = crud.get_project_id_by_document_id(db, document)
    if not project:  
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.id != project.owner_id:
        raise HTTPException(status_code=403, detail="Access denied")
    downloaded_file_path = download_file(f"uploads/project_{document.project_id}/document_{document.id}/{document.filename}")
    return FileResponse(path=downloaded_file_path, filename=document.filename, media_type=document.content_type)


@app.put("/document/{document_id}")
def update_document(document_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Actualiza documento en projecto disponible para usuario.

    -Parametros:

        document_id: id del documento a actualizar.

        file: Función para cargar archivo o documento a la base de datos (UploadFile de FastAPI).

        db: llama a la sesión de la base de datos.

        current_user: llama al usuario activo para la base de datos.

    -Retorno: 

        retorna objeto de documento actualizado cargado en proyecto, mantiene el id.
    """
    document = crud.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    project = crud.get_project_id_by_document_id(db, document)
    if not project:  
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.id != project.owner_id:
        raise HTTPException(status_code=403, detail="Access denied")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    document = crud.update_document_by_id(db, document_id, file.filename, file.content_type, file_path)
    if not document:
        raise HTTPException(status_code=400, detail="Could not update document")
    with open(file_path, "rb") as f:
        upload_file(f, f"uploads/project_{document.project_id}/document_{document.id}/{file.filename}")
    return document


@app.delete("/document/{document_id}")
def delete_document(document_id: int,db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    """
    Borra documento en projecto si usuario es el owner.

    -Parametros:

        document_id: id del documento a actualizar.

        db: llama a la sesión de la base de datos.

        current_user: llama al usuario activo para la base de datos.

    -Acción:

        Borra documento de proyecto si el usuario es el owner del proyecto.

    -Retorno: 

        retorna JSON de confirmación de que el documento en proyecto fue borrado exitosamente.
    """
    document = crud.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    project = crud.get_project_id_by_document_id(db, document)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.id != project.owner_id:
        raise HTTPException(status_code=403, detail="Access denied")
    crud.delete_document_by_id(db, document_id)
    return {"detail": "Document deleted successfully"}


@app.post("/project/{project_id}/invite", response_model=schemas.ProjectResponse)
def grant_access_to_project(project_id: int, user: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Invita a usuario a colaborar en projecto disponible para usuario si es owner del proyecto.

    -Parametros:

        project_id: id del proyecto.

        user: nombre de usuario al que se le darán permisos.

        db: llama a la sesión de la base de datos.

        current_user: llama al usuario activo para la base de datos.

    -Retorno: 
    
        retorna objeto del proyecto actualizado con lista de usuarios invitados al proyecto.
    """
    project = crud.get_projects_details_by_user(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.id != project.owner_id:
        raise HTTPException(status_code=403, detail="Access denied")
    updated_project = crud.add_user_to_project_by_name(db, project_id, user)
    if updated_project is None:
        raise HTTPException(status_code=404, detail="User not found")
    if isinstance(updated_project, dict) and "detail" in updated_project:
        raise HTTPException(status_code=400, detail=updated_project["detail"])
    return updated_project