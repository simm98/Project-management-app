from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

project_users = Table("project_users", Base.metadata, Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True), Column("user_id", Integer, ForeignKey("users.id"), primary_key=True))
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    projects = relationship("Project", secondary=project_users, back_populates="users")
    owned_projects = relationship("Project", back_populates="owner")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content_type = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="documents")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")
    users = relationship("User", secondary=project_users, back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")