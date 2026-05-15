import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import database, models, schemas, crud
from jose import JWTError, jwt
from datetime import datetime, timedelta
app = FastAPI()
database.init_db()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
UPLOAD_DIR = '/uploads'
SECRET_KEY = "supersecretkey"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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

###########################################################################################################################################
######################################################Endpoints############################################################################
###########################################################################################################################################
@app.post("/auth", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.password != user.repeat_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    db_user = crud.get_user_by_login(db, user.login)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db, user)

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.login == form_data.username).first()
    if not user or user.password != form_data.password:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/projects", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_project(db, project, current_user)

@app.get("/projects", response_model=list[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_projects_by_user(db, current_user.id)

@app.get("/projects/{project_id}/info", response_model=schemas.ProjectResponse)
def get_project_details(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = crud.get_projects_details_by_user(db, project_id)
    if not project :
        raise HTTPException(status_code=404, detail='Project not found')
    if current_user.id != project.owner_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return schemas.ProjectResponse.from_orm(project)

@app.put("/projects/{project_id}/info", response_model=schemas.ProjectResponse)
def update_project_details(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = crud.update_projects_details_by_user(db, project_id, project_update, current_user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
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
    documents_content = crud.get_project_documents(db, project_id)
    owner_id_ver = crud.get_projects_details_by_user(db, project_id).owner_id
    if not documents_content:
        raise HTTPException(status_code=404, detail='Documents not found')
    if current_user.id != owner_id_ver:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"documents": documents_content}


@app.post("/projects/{project_id}/documents", response_model=schemas.DocumentResponse)
def upload_document(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = crud.get_projects_details_by_user(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    document = crud.add_document_to_project(db, project_id, file.filename, file.content_type, file_path)
    if not document:
        raise HTTPException(status_code=400, detail="Could not add document")
    return document

@app.get("/document/{document_id}")
def get_download_document(document_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    document = crud.get_document_by_id(db, document_id)
    project = db.query(models.Project).filter(models.Project.id == document.project_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if not project:  
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.id != project.owner_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return FileResponse(path=document.file_path, filename=document.filename, media_type=document.content_type)

@app.put("/document/{document_id}")
def update_document(document_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    document = crud.get_document_by_id(db, document_id)
    project = db.query(models.Project).filter(models.Project.id == document.project_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
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
    return document

@app.delete("/document/{document_id}", status_code=204)
def delete_document(document_id: int,db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    document = crud.get_document_by_id(db, document_id)
    project = db.query(models.Project).filter(models.Project.id == document.project_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.id != project.owner_id:
        raise HTTPException(status_code=403, detail="Access denied")
    crud.delete_document_by_id(db, document_id)
    return {"detail": "Document deleted successfully"}