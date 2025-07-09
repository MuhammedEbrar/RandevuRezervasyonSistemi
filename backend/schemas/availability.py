# backend/schemas/availability.py
from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional
from uuid import UUID

from models.availability import ScheduleType, DayOfWeek # Enum'ları import ediyoruz

# Müsaitlik takvimi oluşturmak için girdi şeması
class AvailabilityScheduleCreate(BaseModel):
    day_of_week: Optional[DayOfWeek] = None # Haftanın günü (REGULAR için)
    specific_date: Optional[date] = None # Belirli bir tarih (EXCEPTION için)
    start_time: time # Başlangıç saati
    end_time: time # Bitiş saati
    type: ScheduleType # Müsaitlik tipi (REGULAR veya EXCEPTION)
    is_available: bool = True # Müsaitlik durumu (varsayılan olarak müsait)

# Müsaitlik takvimi güncellemek için girdi şeması (tüm alanlar isteğe bağlı)
class AvailabilityScheduleUpdate(BaseModel):
    day_of_week: Optional[DayOfWeek] = None
    specific_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    type: Optional[ScheduleType] = None
    is_available: Optional[bool] = None

# Müsaitlik takvimi çıktısı (API yanıtı) şeması
class AvailabilityScheduleOut(BaseModel):
    schedule_id: UUID
    resource_id: UUID
    owner_id: UUID
    day_of_week: Optional[DayOfWeek] = None
    specific_date: Optional[date] = None
    start_time: time
    end_time: time
    type: ScheduleType
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # SQLAlchemy modellerinden Pydantic modeline dönüştürme için