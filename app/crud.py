import schemas, models   
from sqlalchemy.orm import Session

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(login=user.login, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()