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
    owned_projects = db.query(models.Project).filter(models.Project.owner_id == user_id).all()
    invited_projects = db.query(models.Project).join(models.project_users).filter(models.project_users.c.user_id == user_id).all()
    projects = list({p.id: p for p in owned_projects + invited_projects}.values())
    return projects


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
    response = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not response:
        response = None
    return response


def get_project_id_by_document_id(db:Session, document: schemas.DocumentResponse):
    response = db.query(models.Project).filter(models.Project.id == document.project_id).first()
    if not response:
        response = None
    return response


def update_document_by_id(db:Session, document_id: int, filename: str, content_type: str, file_path: str):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        return None
    if document.filename is not None:
        document.filename = filename
    if document.content_type is not None:
        document.content_type = content_type
    if document.file_path is not None:
        document.file_path = file_path
    db.commit()
    db.refresh(document)
    return document


def delete_document_by_id(db:Session, document_id: int):
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    db.delete(document)
    db.commit()


def add_user_to_project_by_name(db:Session, project_id: int, username: str):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        return None
    user = db.query(models.User).filter(models.User.login == username).first()
    if not user:
        return None
    exists = db.execute(models.project_users.select().where((models.project_users.c.project_id == project_id) &(models.project_users.c.user_id == user.id))).first()
    if exists:
        return {"detail": "User already in project"}
    db.execute(models.project_users.insert().values(project_id=project_id, user_id=user.id))
    db.commit()
    db.refresh(db_project)
    return db_project