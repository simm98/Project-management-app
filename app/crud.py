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

def create_project(db:Session, project: schemas.ProjectCreate, user_id:int):
        db_project = models.Project(name = project.name, description = project.description, owner_id = user_id)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

def get_projects_by_user(db: Session, user_id: int):
    return db.query(models.Project).filter(models.Project.owner_id == user_id).all()