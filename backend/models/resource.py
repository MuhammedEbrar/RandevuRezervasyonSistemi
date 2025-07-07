# backend/models/resource.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, Text, ForeignKey # Integer eklendi
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
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False) # İşletme sahibinin ID'si (Tenant ID)
    name = Column(String, index=True, nullable=False) # Varlığın adı (örn: "Toplantı Odası A", "Saç Kesimi")
    description = Column(String, nullable=True) # Varlığın açıklaması
    type = Column(Enum(ResourceType), nullable=False) # Varlık tipi (SERVICE veya SPACE)
    capacity = Column(Integer, nullable=True) # Eğer bir alan ise kapasitesi
    location = Column(JSONB, nullable=True) # JSON formatında konum bilgisi (adres, koordinatlar vb.)
    is_active = Column(Boolean, default=True) # Varlığın aktif olup olmadığı
    tags = Column(ARRAY(Text), nullable=True) # Varlığı tanımlayan etiketler (örn: ['wi-fi', 'projektör'])
    images = Column(ARRAY(Text), nullable=True) # Varlık resimlerinin URL'leri
    cancellation_policy = Column(String, nullable=True) # İptal politikası açıklaması
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # Oluşturulma tarihi
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) # Son güncelleme tarihi ve ilk oluşturmada boş kalmaması için

    # İlişkiler
    owner = relationship("User", back_populates="resources")
    availability_schedules = relationship("AvailabilitySchedule", back_populates="resource")
    # pricing_rules = relationship("PricingRule", back_populates="resource")
    # bookings = relationship("Booking", back_populates="resource")

    def __repr__(self):
        return f"<Resource(name='{self.name}', type='{self.type}', owner_id='{self.owner_id}')>"

