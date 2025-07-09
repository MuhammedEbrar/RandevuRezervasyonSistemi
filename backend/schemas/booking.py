# backend/schemas/booking.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime # datetime kullanıyoruz çünkü bookings_start_time ve bookings_end_time tam zaman damgalarıdır.
from typing import Optional

# Booking oluşturmak için şema
class BookingCreate(BaseModel):
    resource_id: UUID
    # schedule_id: UUID # Eğer bir müsaitlik takvimi kaydına referans verecekseniz
    start_time: datetime # datetime olarak tutulması daha mantıklı
    end_time: datetime   # datetime olarak tutulması daha mantıklı
    notes: Optional[str] = None
    # customer_id otomatik auth'dan gelecek

# Fiyat hesaplama isteği için şema (bu hatayı çözmek için gerekli olan)
class BookingCalculatePriceRequest(BaseModel):
    resource_id: UUID
    start_time: datetime
    end_time: datetime

# Booking çıktısı (API yanıtı) şeması
class BookingOut(BaseModel):
    booking_id: UUID
    customer_id: UUID
    resource_id: UUID
    start_time: datetime
    end_time: datetime
    status: str # BookingStatus enum'ınız varsa str(BookingStatus) olarak dönüştürülmeli
    total_price: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # Pydantic v2 için