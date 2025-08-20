from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from bson.errors import InvalidId
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from bson import ObjectId
from app.config import db


load_dotenv()

EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))
JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM=os.getenv("JWT_ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def create_access_token(data, expires_delta=EXPIRATION_MINUTES):
    copied_data = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    copied_data["exp"] = int(expire.timestamp())

    return jwt.encode(copied_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        print("Decoded token payload:", payload)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except InvalidId:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
