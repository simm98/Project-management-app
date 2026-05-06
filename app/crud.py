from .database import database
from .models import notes

async def create_note(text: str):
    query = notes.insert().values(text=text)
    return await database.execute(query)

async def get_notes():
    query = notes.select()
    return await database.fetch_all(query)
