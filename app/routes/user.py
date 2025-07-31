from fastapi import APIRouter, HTTPException
import bcrypt
from models.user import UserIn, UserOut, LoginIn, Token
from config import db
from datetime import datetime, timezone
from auth.utils import create_access_token

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register_user(user: UserIn):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")
        
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    result = await db.users.insert_one(
        {"email": user.email,
         "username": user.username,
         "hashed_password": hashed_password,
         "created_at": datetime.now(timezone.utc)
    })
    new_user = await db.users.find_one({"_id": result.inserted_id})

    return UserOut(
        id=str(new_user["_id"]),
        username=new_user["username"],
        email=new_user["email"],
        created_at=new_user["created_at"]
    )

@router.post("/login", response_model=Token)
async def login_user(user: LoginIn):
    login_data = user.model_dump()
    existing_user = await db.users.find_one({"email": login_data["email"]})

    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not bcrypt.checkpw(user.password.encode("utf-8"), existing_user["hashed_password"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": str(existing_user["_id"])})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


    