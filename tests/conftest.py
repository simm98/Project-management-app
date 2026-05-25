# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.main import app, get_db
# from app.database import Base

# # Usamos SQLite en memoria para pruebas rápidas
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Crear las tablas en la DB de prueba
# Base.metadata.create_all(bind=engine)

# # Fixture de sesión de DB
# @pytest.fixture(scope="function")
# def db_session():
#     session = TestingSessionLocal()
#     try:
#         yield session
#     finally:
#         session.close()

# # Override de la dependencia get_db para usar la DB de prueba
# @pytest.fixture(scope="function")
# def client(db_session):
#     def override_get_db():
#         try:
#             yield db_session
#         finally:
#             db_session.close()

#     app.dependency_overrides[get_db] = override_get_db
#     yield TestClient(app)
#     app.dependency_overrides.clear()
