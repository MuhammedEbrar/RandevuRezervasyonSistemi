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

class Resource(Base):
    __tablename__ = "resources"

    resource_id = Column(UUID(as_uuid=True), primary_key = True, default= uuid.uuid4)
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
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # İlişkiler
    owner = relationship("User", back_populates="resources")
    availability_schedules = relationship("AvailabilitySchedule", back_populates="resource")
    pricing_rules = relationship("PricingRule", back_populates="resource") # <--- UNCOMMENT THIS LINE
    bookings = relationship("Booking", back_populates="resource")
    def __repr__(self):
        return f"<Resource(name='{self.name}', type='{self.type}', owner_id='{self.owner_id}')>"