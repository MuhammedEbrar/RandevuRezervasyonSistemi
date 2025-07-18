# backend/models/pricing.py
from sqlalchemy import Boolean, Column, String, Integer, DateTime, Enum, ForeignKey, Text, DECIMAL, Time
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from database import Base
# Modelleri models/__init__.py üzerinden import ettiğimiz için burada tek tek gerek yok
# from models.user import User
# from models.resource import Resource

class DurationType(str, enum.Enum):
    PER_HOUR = "PER_HOUR"
    PER_DAY = "PER_DAY"
    PER_ITEM = "PER_ITEM"
    FIXED_PRICE = "FIXED_PRICE"

class ApplicableDay(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    ALL = "ALL"

class PricingRule(Base):
    __tablename__ = "pricing_rules"

    price_rule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.resource_id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    duration_type = Column(Enum(DurationType), nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    min_duration = Column(Integer, nullable=True)
    max_duration = Column(Integer, nullable=True)
    applicable_days = Column(ARRAY(Enum(ApplicableDay)), nullable=True)
    start_time_of_day = Column(Time, nullable=True)
    end_time_of_day = Column(Time, nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler: back_populates'ların doğru ve eşleşen isimlere sahip olduğundan emin olun
    resource = relationship("Resource", back_populates="pricing_rules") # BURASI KRİTİK!
    owner = relationship("User", back_populates="pricing_rules") # BURASI KRİTİK!

    def __repr__(self):
        return f"<PricingRule(id='{self.price_rule_id}', resource='{self.resource_id}', price='{self.base_price}')>"