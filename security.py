import token
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
import jwt
from settings import settings
from fastapi import Depends, HTTPException
from database import get_db, AsyncSession
from models import Users
from sqlalchemy import select

# Security utilities for password hashing and token management
password_hash = PasswordHash.recommended()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Hash a plain password
def hash_password(password: str) -> str:
    return password_hash.hash(password)

# Verify a plain password against a hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

# Create a JWT token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
             expire = datetime.now(timezone.utc) + expires_delta
        else:
             expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm="HS256")
        return token

# Get the current user from the token
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
         decoded_token = jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=["HS256"])
         db_result = await db.execute(select(Users).filter(Users.id == int(decoded_token["sub"])))
         user = db_result.scalar_one_or_none()
         if not user:
             raise HTTPException(status_code=404, detail="User not found")
         return user
    except jwt.ExpiredSignatureError:
         raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
         raise HTTPException(status_code=401, detail="Invalid token.")

# Generate a password reset token
def reset_password_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm="HS256")
    return token
          