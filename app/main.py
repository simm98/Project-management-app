from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import database, metadata, engine
from .crud import create_note, get_notes

metadata.create_all(engine)

app = FastAPI()

# Crear tablas al inicio
metadata.create_all(engine)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await database.connect()
    yield
    # Shutdown
    await database.disconnect()

@app.get('/')
async def read_root():
    return {'message':'FastAPI + PostgreSQL desde contenedor Docker sencillo'}

@app.get('/items/{item_id}')
async def read_item(item_id: int, q: str=None):
    return {'item_id': item_id, 'q': q}

@app.post("/notes/")
async def add_note(text: str):
    note_id = await create_note(text)
    return {"id": note_id, "text": text}

@app.get("/notes/")
async def list_notes():
    return await get_notes()