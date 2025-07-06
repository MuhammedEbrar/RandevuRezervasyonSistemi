# backend/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

from backend.models.user import UserRole # UserRole enum'unu import ediyoruz

# Kullanıcı kaydı için girdi şeması
class UserCreate(BaseModel):
    email: EmailStr # Geçerli bir e-posta formatı
    password: str = Field(min_length=8) # Şifre en az 8 karakter olmalı
    role: UserRole # Kullanıcı rolü (BUSINESS_OWNER veya CUSTOMER)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

# Kullanıcı girişi için girdi şeması
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Kullanıcı profili güncelleme için girdi şeması
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None
    # Şifre güncelleme burada olmaz, ayrı bir endpoint ile yapılmalı.

# Kullanıcı çıktısı (API yanıtı) şeması
class UserOut(BaseModel):
    user_id: UUID
    email: EmailStr
    role: UserRole
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None # Güncellenmemişse boş olabilir

    class Config:
        from_attributes = True # SQLAlchemy modellerinden Pydantic modeline dönüştürme için
