from pydantic import BaseModel
from datetime import datetime

class UserIn(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

class UserDB(BaseModel):
    id: str
    username: str
    email: str
    hashed_password: str
    created_at: datetime

class LoginIn(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    