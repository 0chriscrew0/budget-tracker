from fastapi import FastAPI

from config import db
from routes import budget

app = FastAPI()

app.include_router(budget.router)


@app.get("/")
async def root():
    collections = await db.list_collection_names()
    return {"collections": collections}