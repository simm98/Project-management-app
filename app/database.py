import databases
import sqlalchemy

DATABASE_URL = "postgresql://admin:root123@db:5432/postgres"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(DATABASE_URL)
