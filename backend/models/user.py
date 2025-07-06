# backend/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, Enum # Enum için import
from sqlalchemy.dialects.postgresql import UUID # UUID için
from sqlalchemy.sql import func
import uuid # uuid.uuid4 için
import enum # Python'ın kendi enum'u

from database import Base

# Kullanıcı rolleri için Python Enum'u
class UserRole(str, enum.Enum):
    BUSINESS_OWNER = "BUSINESS_OWNER"
    CUSTOMER = "CUSTOMER"

class User(Base):
    __tablename__ = "users" # Veritabanındaki tablo adı

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # Şifrenin hash'lenmiş hali
    role = Column(Enum(UserRole), nullable=False) # Kullanıcı rolü
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True) # Kullanıcının aktif olup olmadığı
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # Kayıt tarihi
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) # Son güncelleme tarihi

    # İlişkiler (şimdilik yorum satırı, ileride eklenecek)
    # resources = relationship("Resource", back_populates="owner")
    # bookings_as_customer = relationship("Booking", foreign_keys="[Booking.customer_id]", back_populates="customer")
    # bookings_as_owner = relationship("Booking", foreign_keys="[Booking.owner_id]", back_populates="owner")

    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"
