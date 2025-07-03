# backend/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID

from backend.core.settings import ALGORITHM, JWT_SECRET_KEY
from config import settings # settings objesini import ediyoruz
from database import get_db
from crud import user as crud_user # user crud modülünü import ediyoruz
from models.user import User, UserRole # User modelini ve UserRole enum'unu import ediyoruz

# Şifre hashleme için context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Şifreyi hashleme
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Şifreyi doğrulama
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT token oluşturma
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# OAuth2PasswordBearer, FastAPI'nin security schemes için kullandığı bir mekanizma
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login") # Login endpoint'inin yolu

# JWT token'ı doğrulama ve veri alma
def verify_token(token: str, credentials_exception: HTTPException) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload 
    except JWTError:
        raise credentials_exception

# FastAPI bağımlılığı olarak kullanılacak: Geçerli kullanıcıyı getirir
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulama bilgileri geçersiz.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token, credentials_exception) # Ham payload'ı alıyoruz

    user_id_str: Optional[str] = payload.get("sub") # JWT standartlarında subject (kullanıcı kimliği) için 'sub' kullanılır

    if user_id_str is None: # veya diğer gerekli alanlar eksikse
        raise credentials_exception

    # UUID'yi doğrulamak için
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception # Geçersiz UUID formatı

    # Veritabanından kullanıcıyı çekiyoruz
    db_user = crud_user.get_user_by_id(db, user_id)
    if db_user is None:
        raise credentials_exception

    return db_user # Doğrudan veritabanından çekilmiş User objesini döndür

# Rol bazlı yetkilendirme için helper fonksiyonu
def check_user_role(required_roles: list[UserRole]): # Artık bir UserRole listesi bekliyor
    def role_checker(current_user: User = Depends(get_current_user)): # current_user bir User objesi

        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için yetki gerekli. Gerekli roller: {[role.value for role in required_roles]}."
            )
        return current_user
    return role_checker
