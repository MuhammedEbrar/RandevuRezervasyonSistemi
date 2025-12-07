# backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from schemas.user import UserCreate, UserOut
from crud import user as crud_user
from core.security import verify_password, create_access_token
from config import settings

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Yeni kullanıcı kaydı oluşturur.

    - **email**: Geçerli bir e-posta adresi
    - **password**: En az 8 karakter
    - **role**: CUSTOMER veya BUSINESS_OWNER
    - **first_name, last_name, phone_number**: Opsiyonel
    """
    # E-posta zaten kayıtlı mı kontrol et
    db_user = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta adresi zaten kayıtlı."
        )

    try:
        # Yeni kullanıcı oluştur
        new_user = crud_user.create_user(db=db, user_in=user_in)
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Kullanıcı girişi yapar ve JWT access token döner.

    OAuth2 standardına uygun olarak:
    - **username**: E-posta adresi (OAuth2 standardı gereği 'username' field'ı kullanılır)
    - **password**: Kullanıcı şifresi

    Başarılı girişte access_token, token_type ve kullanıcı bilgileri döner.
    """
    # Kullanıcıyı e-posta ile bul
    user = crud_user.get_user_by_email(db, email=form_data.username)

    # Kullanıcı bulunamadı veya şifre yanlış
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya şifre hatalı.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Kullanıcı aktif değilse
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hesabınız aktif değil. Lütfen yönetici ile iletişime geçin."
        )

    # JWT token oluştur
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": str(user.user_id),
            "sub": user.email,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": str(user.user_id),
            "email": user.email,
            "role": user.role.value,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "profile_picture_url": user.profile_picture_url,
            "is_active": user.is_active
        }
    }
