# backend/models/booking.py
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from database import Base # SQLAlchemy Base objesini import ediyoruz
from models.user import User # customer_id ve owner_id ilişkileri için
from models.resource import Resource # resource_id ilişkisi için

# Rezervasyon durumu için Python Enum'u
class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"       # Beklemede (Ödeme bekleniyor, onay bekleniyor)
    CONFIRMED = "CONFIRMED"   # Onaylandı (Rezervasyon tamamlandı)
    CANCELLED = "CANCELLED"   # İptal edildi (Kullanıcı tarafından veya işletme tarafından)
    COMPLETED = "COMPLETED"   # Tamamlandı (Hizmet verildi, kira süresi doldu)
    REJECTED = "REJECTED"     # Reddedildi (İşletme tarafından reddedildi)

# Ödeme durumu için Python Enum'u
class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"       # Ödeme bekleniyor
    PAID = "PAID"             # Ödendi
    REFUNDED = "REFUNDED"     # İade edildi
    FAILED = "FAILED"         # Ödeme başarısız oldu

class Booking(Base):
    __tablename__ = "bookings" # Veritabanındaki tablo adı

    booking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.resource_id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False) # Multi-tenancy için kritik!
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    deposit_amount = Column(DECIMAL(10, 2), nullable=True) # Kapora miktarı
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    is_recurring = Column(Boolean, default=False) # Tekrarlayan rezervasyon mu? [cite: 3556]
    parent_booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.booking_id"), nullable=True) # Tekrarlayan rezervasyonlar için ana rezervasyon ID'si [cite: 3556]
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler
    resource = relationship("Resource", back_populates="bookings")
    customer = relationship("User", foreign_keys=[customer_id], back_populates="bookings_as_customer")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="bookings_as_owner")
    parent_booking = relationship("Booking", remote_side=[booking_id]) # Self-referencing ilişki [cite: 3556]

    def __repr__(self):
        return f"<Booking(id='{self.booking_id}', resource='{self.resource_id}', customer='{self.customer_id}')>"