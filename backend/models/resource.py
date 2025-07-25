# backend/models/resource.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from database import Base

class ResourceType(str, enum.Enum):
    HIZMET = "HIZMET"
    MEKAN = "MEKAN"

class BookingType(str, enum.Enum):
    SLOT_BASED = "SLOT_BASED"     # Sabit slotlar (örn: 14:00, 14:30, 15:00)
    DURATION_BASED = "DURATION_BASED" # Esnek başlangıç (örn: 14:21'de başla, 3 saat sürsün)

class Resource(Base):
    __tablename__ = "resources"

    resource_id = Column(UUID(as_uuid=True), primary_key = True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    type = Column(Enum(ResourceType), nullable=False)
    capacity = Column(Integer, nullable=True)
    location = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True)
    tags = Column(ARRAY(Text), nullable=True)
    images = Column(ARRAY(Text), nullable=True)
    cancellation_policy = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    booking_type = Column(Enum(BookingType), nullable=False, server_default=BookingType.SLOT_BASED.value)
    max_bookings_per_day = Column(Integer, nullable=True) # Bir günde en fazla kiralama sayısı
    max_bookings_per_customer = Column(Integer, nullable=True) # Bir müşterinin en fazla kiralama sayısı


    # İlişkiler: back_populates'ların doğru ve eşleşen isimlere sahip olduğundan emin olun
    owner = relationship("User", back_populates="resources")
    availability_schedules = relationship("AvailabilitySchedule", back_populates="resource", cascade="all, delete-orphan") # BURASI KRİTİK!
    pricing_rules = relationship("PricingRule", back_populates="resource", cascade="all, delete-orphan") # BURASI KRİTİK!
    bookings = relationship("Booking", back_populates="resource", cascade="all, delete-orphan") # BURASI KRİTİK!

    def __repr__(self):
        return f"<Resource(name='{self.name}', type='{self.type}', owner_id='{self.owner_id}')>"
    

