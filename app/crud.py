from . import schemas, models   
from sqlalchemy.orm import Session

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(login=user.login, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()

def create_project(db:Session, project: schemas.ProjectCreate, current_user: models.User):
    db_project = models.Project(name = project.name, description = project.description, owner_id = current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects_by_user(db: Session, user_id: int):
    return db.query(models.Project).filter(models.Project.owner_id == user_id).all()

def get_projects_details_by_user(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def update_projects_details_by_user(db:Session, project_id: int, project_update: schemas.ProjectUpdate, current_user: models.User):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project.name is not None:
        db_project.name = project_update.name
    if db_project.description is not None:
        db_project.description = project_update.description
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db:Session, project_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    db.delete(db_project)
    db.commit()

def get_project_documents(db:Session, project_id: int):
    return db.query(models.Document).filter(models.Document.project_id == project_id).all()

def add_document_to_project(db:Session, project_id: int, filename: str, content_type: str, file_path: str):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        return None
    document = models.Document(filename=filename, content_type=content_type, project=db_project, file_path=file_path)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

def get_document_by_id(db:Session, document_id: int):
    return db.query(models.Document).filter(models.Document.id == document_id).first()
