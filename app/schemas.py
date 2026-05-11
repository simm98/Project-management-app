from pydantic import BaseModel

class UserCreate(BaseModel):
    login: str
    password: str
    repeat_password: str

class UserLogin(BaseModel):
    login: str
    password: str

class UserResponse(BaseModel):
    id: int
    login: str
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    description: str

class ProjectUpdate(BaseModel):
    name: str = None
    description: str = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    users: list[UserLogin] = []
    class Config:
        from_attributes = True