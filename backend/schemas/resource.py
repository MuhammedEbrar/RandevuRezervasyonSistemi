# backend/schemas/resource.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

# DÜZELTME: Import yolu 'backend.' olmadan, doğrudan 'models'den başlıyor.
from models.resource import ResourceType, BookingType

# Resource oluşturmak için girdi şeması
class ResourceCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: ResourceType
    capacity: Optional[int] = 1 # Varsayılan kapasite 1 olabilir
    location: Optional[dict] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    cancellation_policy: Optional[str] = None
    # YENİ EKLENEN ALANLAR
    booking_type: Optional[BookingType] = BookingType.SLOT_BASED
    max_bookings_per_day: Optional[int] = None
    max_bookings_per_customer: Optional[int] = None

# Resource güncellemek için girdi şeması (tüm alanlar isteğe bağlı)
class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: Optional[ResourceType] = None
    capacity: Optional[int] = None
    location: Optional[dict] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    cancellation_policy: Optional[str] = None
    # YENİ EKLENEN ALANLAR
    booking_type: Optional[BookingType] = None
    max_bookings_per_day: Optional[int] = None
    max_bookings_per_customer: Optional[int] = None

# Resource çıktısı (API yanıtı) şeması
class ResourceOut(BaseModel):
    resource_id: UUID
    owner_id: UUID
    name: str
    description: Optional[str] = None
    type: ResourceType
    capacity: Optional[int] = None
    location: Optional[dict] = None
    is_active: bool
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    cancellation_policy: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    # YENİ EKLENEN ALANLAR
    booking_type: BookingType
    max_bookings_per_day: Optional[int] = None
    max_bookings_per_customer: Optional[int] = None

    class Config:
        from_attributes = True # SQLAlchemy modellerinden Pydantic modeline dönüştürme için