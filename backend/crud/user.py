# backend/crud/user.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # E-posta tekilliği için
from typing import Optional
from uuid import UUID # UUID tipi için

from models.user import User, UserRole # Modeli ve Enum'ı import ediyoruz
from schemas.user import UserCreate, UserUpdate
from core.security import get_password_hash # Şifre hashleme için


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        password_hash=hashed_password,
        role=user_in.role,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        phone_number=user_in.phone_number
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        # E-posta zaten mevcutsa hata fırlat (FastAPI router'da yakalarız)
        db.rollback()
        raise ValueError("Email already registered")

def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    # exclude_unset=True: Sadece gönderilen alanları günceller, gönderilmeyenleri olduğu gibi bırakır
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Diğer CRUD operasyonları (silme vb.) buraya eklenebilir.
