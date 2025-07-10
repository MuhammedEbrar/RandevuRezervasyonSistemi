# backend/schemas/booking.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal # Total price ve deposit amount için

from models.booking import BookingStatus, PaymentStatus # Enum'ları import ediyoruz

# Booking oluşturmak için girdi şeması
class BookingCreate(BaseModel):
    resource_id: UUID
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None
    # customer_id otomatik auth'dan gelecek
    # total_price ve deposit_amount hesaplanacağı için burada yer almaz
    # status ve payment_status başlangıçta PENDING olarak ayarlanır

# Fiyat hesaplama isteği için şema (pricing router'da kullanılabilir)
class BookingCalculatePriceRequest(BaseModel):
    resource_id: UUID
    start_time: datetime
    end_time: datetime

# Fiyat yanıtı için şema (pricing router'dan dönecek)
class BookingCalculatePriceResponse(BaseModel):
    total_price: Decimal

# Booking çıktısı (API yanıtı) şeması
class BookingOut(BaseModel):
    booking_id: UUID
    resource_id: UUID
    customer_id: UUID
    owner_id: UUID
    start_time: datetime
    end_time: datetime
    total_price: Decimal
    deposit_amount: Optional[Decimal] = None
    status: BookingStatus
    payment_status: PaymentStatus
    is_recurring: bool
    parent_booking_id: Optional[UUID] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # SQLAlchemy modellerinden Pydantic modeline dönüştürme için
        json_encoders = {
            # Decimal tipini JSON'a düzgün çevirmek için
            Decimal: lambda v: float(v)
        }

# Rezervasyon durumu güncellemek için şema (admin/işletme sahibi için)
class BookingStatusUpdate(BaseModel):
    status: BookingStatus
    # payment_status: Optional[PaymentStatus] = None # Eğer ödeme durumu da güncellenecekse

# Rezervasyon ödeme durumu güncellemek için şema (webhook'lar için)
class BookingPaymentStatusUpdate(BaseModel):
    payment_status: PaymentStatus
    # status: Optional[BookingStatus] = None # Eğer ödeme durumu, rezervasyon durumunu da etkiliyorsa