# backend/schemas/booking.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, time, date
from typing import Optional, List
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

# Rezervasyon güncellemek için şema
class BookingUpdate(BaseModel):
    # Tüm alanlar isteğe bağlıdır, sadece güncellenecek olanları gönderin
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    # status: Optional[BookingStatus] = None # Durum güncellemesi ayrı şemalarla yapıldığı için genellikle burada yer almaz
    # payment_status: Optional[PaymentStatus] = None # Ödeme durumu güncellemesi ayrı şemalarla yapıldığı için genellikle burada yer almaz
    # total_price: Optional[Decimal] = None # Bu genellikle otomatik hesaplanır, doğrudan güncellenmez
    # deposit_amount: Optional[Decimal] = None # Bu da doğrudan güncellenmeyebilir


# Tekrarlayan rezervasyon oluşturur
class RecurringBookingCreate(BaseModel):
    resource_id: UUID
    start_time_of_day: time
    end_time_of_day: time
    day_of_week: str
    start_date: date
    end_date: date

# Tekrarlayan rezervasyon endpoint'inin yanıtı için şema
class RecurringBookingResponse(BaseModel):
    message: str
    created_bookings_count: int
    total_price_for_all_bookings: float
    booking_ids: List[UUID] = [] # Oluşturulan rezervasyonların ID'leri