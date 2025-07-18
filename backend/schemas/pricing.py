from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from models import DurationType, ApplicableDay

class PricingRuleCreate(BaseModel):
    duration_type: DurationType # Fiyatlandırma süresi tipi
    base_price: Decimal = Field(..., gt=0) # Temel fiyat, 0'dan büyük olmalı
    min_duration: Optional[int] = Field(None, ge=0) # Minimum süre, 0'dan büyük eşit olmalı
    max_duration: Optional[int] = Field(None, gt=0) # Maksimum süre, 0'dan büyük olmalı
    applicable_days: Optional[List[ApplicableDay]] = None # Uygulanacağı günler
    start_time_of_day: Optional[time] = None # Günün başlangıç saati
    end_time_of_day: Optional[time] = None # Günün bitiş saati
    is_active: bool = True # Kuralın aktif olup olmadığı
    description: Optional[str] = Field(None, max_length=255) # Kural açıklaması


# Fiyatlandırma kuralı güncellemek için girdi şeması (tüm alanlar isteğe bağlı)
class PricingRuleUpdate(BaseModel):
    duration_type: Optional[DurationType] = None
    base_price: Optional[Decimal] = Field(None, gt=0)
    min_duration: Optional[int] = Field(None, ge=0)
    max_duration: Optional[int] = Field(None, gt=0)
    applicable_days: Optional[List[ApplicableDay]] = None
    start_time_of_day: Optional[time] = None
    end_time_of_day: Optional[time] = None
    is_active: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=255)

# Fiyatlandırma kuralı çıktısı (API yanıtı) şeması
class PricingRuleOut(BaseModel):
    price_rule_id: UUID
    resource_id: UUID
    owner_id: UUID
    duration_type: DurationType
    base_price: Decimal
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    applicable_days: Optional[List[ApplicableDay]] = None
    start_time_of_day: Optional[time] = None
    end_time_of_day: Optional[time] = None
    is_active: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # SQLAlchemy modellerinden Pydantic modeline dönüştürme için
        json_encoders = {
            # Decimal tipini JSON'a düzgün çevirmek için
            Decimal: lambda v: float(v)
        }