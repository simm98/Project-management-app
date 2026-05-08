from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import database, models, schemas, crud

app = FastAPI()

# Crear tablas
models.Base.metadata.create_all(bind=database.engine)

# Dependencia para obtener sesión
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.password != user.repeat_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    db_user = crud.get_user_by_login(db, user.login)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db, user)

@app.post("/login")
def login_user(login_req: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, login_req.login)
    if not db_user or db_user.password != login_req.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": f"Welcome {db_user.login}!"}
