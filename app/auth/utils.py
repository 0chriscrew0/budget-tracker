from jose import jwt
import os
from dotenv import load_dotenv


load_dotenv()

def create_access_token(data, expires_delta=os.getenv("JWT_EXPIRATION_MINUTES")):
    copied_data = data.copy()

    copied_data["exp"] = expires_delta

    return jwt.encode(copied_data, os.getenv("JWT_SECRET_KEY"), os.getenv("JWT_ALGORITHM"))