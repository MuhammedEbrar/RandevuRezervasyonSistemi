# backend/models/user.py (Example - adjust to your actual User model file)
from sqlalchemy import Column, String, Boolean, DateTime, Enum # Make sure Enum is imported
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum # For UserRole enum

from database import Base # Assuming Base is imported

class UserRole(str, enum.Enum): # Your UserRole enum
    BUSINESS_OWNER = "BUSINESS_OWNER"
    CUSTOMER = "CUSTOMER"

class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler
    resources = relationship("Resource", back_populates="owner")
    pricing_rules = relationship("PricingRule", back_populates="owner") 
    availability_schedules = relationship("AvailabilitySchedule", back_populates="owner") 
    
    
    # Booking ilişkileri eklendi
    bookings_as_customer = relationship("Booking", foreign_keys="[Booking.customer_id]", back_populates="customer")
    bookings_as_owner = relationship("Booking", foreign_keys="[Booking.owner_id]", back_populates="owner")

    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"