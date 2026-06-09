import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
ORM_ENABLE = os.getenv("ORM_ENABLE")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está definido.")

if ORM_ENABLE == "DISABLED":
    parsed_url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(dbname=parsed_url.path[1:], user=parsed_url.username, password=parsed_url.password, host=parsed_url.hostname, port=parsed_url.port)
    cur = conn.cursor()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)