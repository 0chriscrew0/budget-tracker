from fastapi import FastAPI
from config import db

app = FastAPI()


@app.get("/")
async def root():
    collections = await db.list_collection_names()
    return {"collections": collections}