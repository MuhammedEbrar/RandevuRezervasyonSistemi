# backend/models/payment.py
from sqlalchemy import Column, String, DateTime, ForeignKey, DECIMAL, Boolean, Enum # <-- 'Enum'u buradan import edin
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from database import Base
from models.user import User
from models.booking import Booking, PaymentStatus # PaymentStatus enum'ını import edin (artık Python'ın enum'ını değil, sizin tanımladığınızı import ettik)

class Payment(Base):
    __tablename__ = "payments" # Veritabanındaki tablo adı

    payment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.booking_id"), nullable=False, unique=True) # Bir rezervasyona bir ödeme
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False) # Ödemeyi yapan müşteri
    amount = Column(DECIMAL(10, 2), nullable=False) # Ödenen miktar
    currency = Column(String(3), nullable=False) # Para birimi (örn: "TRY", "USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False) #ödeme durumu
    transaction_id = Column(String, nullable=True, unique=True) # Ödeme sağlayıcısının verdiği işlem ID'si
    payment_method_last_four = Column(String(4), nullable=True) # Kartın son 4 hanesi (mock için)
    is_successful = Column(Boolean, nullable=False) # Ödeme başarılı mı?
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler
    booking = relationship("Booking", back_populates="payment")
    customer = relationship("User", back_populates="payments_made")

    def __repr__(self):
        return f"<Payment(id='{self.payment_id}', booking='{self.booking_id}', status='{self.status}')>"
