from fastapi import FastAPI
from auth.docs import setup_custom_openapi

from config import db
from routes import budget, user

app = FastAPI()
setup_custom_openapi(app)

app.include_router(budget.router)
app.include_router(user.router)


@app.get("/")
async def root():
    collections = await db.list_collection_names()
    return {"collections": collections}