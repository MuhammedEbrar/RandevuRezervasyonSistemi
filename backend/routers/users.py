# backend/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from schemas.user import UserCreate, UserUpdate, UserOut # Pydantic şemalarınız
from crud import user as crud_user # CRUD fonksiyonlarını kullanmak için
# from auth import get_current_user, get_current_active_user # Kimlik doğrulama fonksiyonlarınız

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    # Kullanıcı oluşturma mantığı
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    # Eğer password_hash'i crud_user'da yapmıyorsanız burada yapmalısınız
    # hashed_password = auth.get_password_hash(user_in.password) 
    return crud_user.create_user(db=db, user_in=user_in) # Veya user_in'i işleyerek


@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: UUID, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Diğer user endpoint'leriniz (GET all, PUT, DELETE vb.)