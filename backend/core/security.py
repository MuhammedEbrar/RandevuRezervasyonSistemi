# backend/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID


from core.settings import settings 
from database import get_db 
from crud import user as crud_user 
from models.user import User, UserRole 

# Değişkenlere doğrudan settings objesi üzerinden erişiyoruz, ayrıca atamaya gerek yok.
# JWT_SECRET_KEY = settings.JWT_SECRET_KEY  # Bu atamalara gerek yok, doğrudan kullanacağız.
# ALGORITHM = settings.ALGORITHM            # Bu atamalara gerek yok, doğrudan kullanacağız.
# ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES # Bu atamaya gerek yok, create_access_token içinde kullanılıyor.

# Şifre hashleme için context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Şifre hashleme
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
    # Doğrudan settings objesinden erişim
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# OAuth2PasswordBearer, FastAPI'nin security schemes için kullandığı bir mekanizma
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login") 

# JWT token'ı doğrulama ve veri alma
def verify_token(token: str, credentials_exception: HTTPException) -> dict:
    try:
        # Doğrudan settings objesinden erişim
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]) # <-- BURAYI DÜZELTİN
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

    user_id_str: Optional[str] = payload.get("sub") 

    if user_id_str is None:
        raise credentials_exception

    # UUID'yi doğrulamak için
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception 

    # Veritabanından kullanıcıyı çekiyoruz
    db_user = crud_user.get_user_by_id(db, user_id)
    if db_user is None:
        raise credentials_exception

    return db_user 

# Rol bazlı yetkilendirme için helper fonksiyonu
def check_user_role(required_roles: list[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için yetki gerekli. Gerekli roller: {[role.value for role in required_roles]}."
            )
        return current_user
    return role_checker