# backend/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.user import UserOut, UserUpdate
from crud import user as crud_user
from core.security import get_current_user
from models.user import User

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Mevcut kullanıcının profil bilgilerini döner.

    JWT token gerektirir (Authorization: Bearer <token>)
    """
    return current_user


@router.put("/me", response_model=UserOut)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mevcut kullanıcının profil bilgilerini günceller.

    JWT token gerektirir (Authorization: Bearer <token>)

    Güncellenebilir alanlar:
    - **first_name**: Ad
    - **last_name**: Soyad
    - **phone_number**: Telefon numarası
    - **profile_picture_url**: Profil resmi URL'i

    Not: Şifre güncellemesi için ayrı bir endpoint kullanılmalıdır.
    """
    try:
        updated_user = crud_user.update_user(
            db=db,
            db_user=current_user,
            user_update=user_update
        )
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Profil güncellenirken hata oluştu: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserOut)
async def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Belirli bir kullanıcının profil bilgilerini döner.

    JWT token gerektirir (Authorization: Bearer <token>)

    - **user_id**: Kullanıcının UUID'si
    """
    from uuid import UUID

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz kullanıcı ID formatı"
        )

    user = crud_user.get_user_by_id(db, user_id=user_uuid)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )

    return user
