from fastapi import FastAPI

from config import db
from routes import budget, user

app = FastAPI()

app.include_router(budget.router)
app.include_router(user.router)


@app.get("/")
async def root():
    collections = await db.list_collection_names()
    return {"collections": collections}