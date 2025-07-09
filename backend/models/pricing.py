# backend/models/pricing.py
from sqlalchemy import  Boolean, Column, String, Integer, DateTime, Enum, ForeignKey, Text, DECIMAL, Time
from sqlalchemy.dialects.postgresql import UUID, ARRAY # UUID ve ARRAY için
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship # İlişkiler için
import uuid # uuid.uuid4 için
import enum # Python'ın kendi enum'u

from database import Base
from models.user import User
from models.resource import Resource


class DurationType(str, enum.Enum):
    PER_HOUR = "PER_HOUR"     # Saat başına
    PER_DAY = "PER_DAY"       # Gün başına
    PER_ITEM = "PER_ITEM"     # Öğe başına (örn: 1 seans)
    FIXED_PRICE = "FIXED_PRICE" # Sabit fiyat

class ApplicableDay(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
    ALL = "ALL" # Tüm günler

class PricingRule(Base):
    __tablename__ = "pricing_rules" # Veritabanındaki tablo adı 

    price_rule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.resource_id"), nullable=False) # Hangi varlığa ait 
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False) # Hangi işletme sahibine ait 
    duration_type = Column(Enum(DurationType), nullable=False) # Fiyatlandırma süresi tipi 
    base_price = Column(DECIMAL(10, 2), nullable=False) # Temel fiyat (örn: 50.00 TL) 
    min_duration = Column(Integer, nullable=True) # Minimum süre (örn: 1 saat, 3 gün) 
    max_duration = Column(Integer, nullable=True) # Maksimum süre 
    applicable_days = Column(ARRAY(Enum(ApplicableDay)), nullable=True) # Uygulanacağı günler (örn: ['MONDAY', 'WEDNESDAY']) 
    start_time_of_day = Column(Time, nullable=True) # Günün hangi saatinden itibaren geçerli 
    end_time_of_day = Column(Time, nullable=True) # Günün hangi saatine kadar geçerli 
    is_active = Column(Boolean, default=True) # Kuralın aktif olup olmadığı 
    description = Column(String, nullable=True) # Kural açıklaması (örn: "Hafta sonu indirimi") 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler
    resource = relationship("Resource", back_populates="pricing_rules")
    owner = relationship("User", back_populates="pricing_rules")

    def __repr__(self):
        return f"<PricingRule(id='{self.price_rule_id}', resource='{self.resource_id}', price='{self.base_price}')>"

# User modeline ilişki eklenmesi
# User.pricing_rules = relationship("PricingRule", back_populates="owner")

# Resource modeline ilişki eklenmesi
# Resource.pricing_rules = relationship("PricingRule", back_populates="resource")
