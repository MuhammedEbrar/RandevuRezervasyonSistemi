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

# Ödeme kaydını payment_id'ye göre getir
def get_payment_by_id(db: Session, payment_id: UUID) -> Optional[Payment]:
    """ID'ye göre tek bir ödeme kaydı getirir."""
    return db.query(Payment).filter(Payment.payment_id == payment_id).first()

# Müşteriye ait tüm ödemeleri listele
def get_payments_by_customer(db: Session, customer_id: UUID, skip: int = 0, limit: int = 100) -> list[Payment]:
    """Bir müşteriye ait tüm ödeme kayıtlarını listeler."""
    return db.query(Payment).filter(Payment.customer_id == customer_id).offset(skip).limit(limit).all()

# Tarih aralığına göre ödemeleri listele
def get_payments_by_date_range(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100
) -> list[Payment]:
    """Belirli bir tarih aralığındaki ödemeleri listeler."""
    return db.query(Payment).filter(
        Payment.created_at >= start_date,
        Payment.created_at <= end_date
    ).offset(skip).limit(limit).all()

# Ödeme durumuna göre ödemeleri listele
def get_payments_by_status(
    db: Session,
    status: PaymentStatus,
    skip: int = 0,
    limit: int = 100
) -> list[Payment]:
    """Belirli bir durumdaki ödemeleri listeler (PAID, FAILED, PENDING, REFUNDED)."""
    return db.query(Payment).filter(Payment.status == status).offset(skip).limit(limit).all()

# Ödeme kaydını sil (hard delete - gerçek uygulamada soft delete tercih edilmeli)
def delete_payment(db: Session, payment_id: UUID) -> Optional[UUID]:
    """
    Bir ödeme kaydını veritabanından siler.
    NOT: Gerçek uygulamada soft delete (is_deleted flag) kullanılmalıdır.
    """
    db_payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if db_payment:
        db.delete(db_payment)
        db.commit()
        return payment_id
    return None

# Tüm ödemeleri listele (admin için)
def get_all_payments(db: Session, skip: int = 0, limit: int = 100) -> list[Payment]:
    """Tüm ödeme kayıtlarını listeler (admin/yönetici için)."""
    return db.query(Payment).offset(skip).limit(limit).all()