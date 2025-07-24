# backend/crud/payments.py

from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from decimal import Decimal
from datetime import datetime

from models.payment import Payment # Payment modelini import edin
from models.booking import Booking, PaymentStatus # Booking modeli ve PaymentStatus enum'ını import edin
from schemas.payment import PaymentInitiateRequest # Şemayı import edin

# Yeni bir ödeme kaydı oluştur
def create_payment(
    db: Session,
    booking_id: UUID,
    customer_id: UUID, # Ödemeyi yapan müşteri
    amount: Decimal,
    currency: str,
    status: PaymentStatus,
    transaction_id: str,
    payment_method_last_four: str,
    is_successful: bool
) -> Payment:
    db_payment = Payment(
        booking_id=booking_id,
        customer_id=customer_id,
        amount=amount,
        currency=currency,
        status=status,
        transaction_id=transaction_id,
        payment_method_last_four=payment_method_last_four,
        is_successful=is_successful
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

# Ödeme kaydını güncelle (özellikle status için)
def update_payment_status(
    db: Session,
    db_payment: Payment,
    new_status: PaymentStatus,
    transaction_id: Optional[str] = None # Eğer işlem ID'si güncelleniyorsa
) -> Payment:
    db_payment.status = new_status
    db_payment.updated_at = datetime.now()
    if transaction_id:
        db_payment.transaction_id = transaction_id
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

# Ödeme kaydını booking_id'ye göre getir
def get_payment_by_booking_id(db: Session, booking_id: UUID) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.booking_id == booking_id).first()