# backend/core/security.py
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.user import UserRole, User 
from core.settings import settings 

# Değişkenleri settings objesinden kullanın
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 

# JWT token'ı doğrulama ve veri alma
def verify_token(token: str, credentials_exception: HTTPException) -> dict:
    try:
        # Şimdi JWT_SECRET_KEY ve ALGORITHM settings objesinden doğru bir şekilde alınmış olmalı
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM]) 
        return payload
    except JWTError:
        raise credentials_exception