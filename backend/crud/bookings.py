# backend/crud/bookings.py

from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

# Modeller
from models.booking import Booking, BookingStatus, PaymentStatus

# Şemalar (DÜZELTME: Eksik olan şemaları da import ediyoruz)
from schemas.booking import BookingCreate, BookingUpdate, BookingOut, BookingStatusUpdate, BookingPaymentStatusUpdate

# DÜZELTME: pricing import'u burada olmamalı.
# from .pricing import get_applicable_pricing_rule, calculate_price_from_rule

def get_booking_by_id(db: Session, booking_id: UUID) -> Optional[Booking]:
    """ID'ye göre tek bir rezervasyon getirir."""
    return db.query(Booking).filter(Booking.booking_id == booking_id).first()

def get_bookings_by_customer(db: Session, customer_id: UUID, skip: int = 0, limit: int = 100) -> List[Booking]:
    """Bir müşteriye ait tüm rezervasyonları listeler."""
    return db.query(Booking).filter(Booking.customer_id == customer_id).offset(skip).limit(limit).all()

def get_bookings_by_owner(db: Session, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[Booking]:
    """Bir işletme sahibine ait tüm rezervasyonları listeler."""
    return db.query(Booking).filter(Booking.owner_id == owner_id).offset(skip).limit(limit).all()

def create_booking(db: Session, booking_in: BookingCreate, customer_id: UUID, owner_id: UUID, total_price: Decimal) -> Booking:
    """
    Yeni bir rezervasyon oluşturur. Toplam fiyatı parametre olarak alır, kendi hesaplamaz.
    """
    db_booking = Booking(
        resource_id=booking_in.resource_id,
        customer_id=customer_id,
        owner_id=owner_id,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time,
        notes=booking_in.notes,
        total_price=total_price,
        status=BookingStatus.PENDING,
        payment_status=PaymentStatus.PENDING
    )
    try:
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    except IntegrityError:
        db.rollback()
        raise ValueError("Rezervasyon oluşturulurken veritabanı hatası oluştu.")

def update_booking_status(db: Session, booking: Booking, status_update: BookingStatusUpdate) -> Booking:
    """Bir rezervasyonun durumunu günceller."""
    booking.status = status_update.status
    booking.updated_at = datetime.now()
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def update_booking_payment_status(db: Session, booking: Booking, payment_status_update: BookingPaymentStatusUpdate) -> Booking:
    """Bir rezervasyonun ödeme durumunu günceller."""
    booking.payment_status = payment_status_update.payment_status
    booking.updated_at = datetime.now()
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def delete_booking(db: Session, booking_id: UUID) -> Optional[UUID]:
    """Bir rezervasyonu veritabanından siler."""
    db_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if db_booking:
        db.delete(db_booking)
        db.commit()
        return booking_id
    return None

def check_booking_conflicts(
    db: Session,
    resource_id: UUID,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: Optional[UUID] = None
) -> List[Booking]:
    """
    Belirli bir kaynak ve zaman dilimi için çakışan rezervasyonları kontrol eder.

    Args:
        db: Veritabanı oturumu
        resource_id: Kontrol edilecek kaynak ID'si
        start_time: Başlangıç zamanı
        end_time: Bitiş zamanı
        exclude_booking_id: İsteğe bağlı - güncelleme sırasında hariç tutulacak rezervasyon ID'si

    Returns:
        Çakışan rezervasyonların listesi
    """
    query = db.query(Booking).filter(
        Booking.resource_id == resource_id,
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
        # Zaman çakışması kontrolü: yeni rezervasyonun başlangıcı mevcut bir rezervasyonun içinde
        # VEYA yeni rezervasyonun bitişi mevcut bir rezervasyonun içinde
        # VEYA yeni rezervasyon mevcut rezervasyonu tamamen kapsıyor
        (
            (Booking.start_time < end_time) & (Booking.end_time > start_time)
        )
    )

    # Güncelleme durumunda mevcut rezervasyonu hariç tut
    if exclude_booking_id:
        query = query.filter(Booking.booking_id != exclude_booking_id)

    return query.all()

def get_bookings_by_resource(
    db: Session,
    resource_id: UUID,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
) -> List[Booking]:
    """
    Belirli bir kaynağa ait rezervasyonları listeler.

    Args:
        db: Veritabanı oturumu
        resource_id: Kaynak ID'si
        skip: Kaç kayıt atlanacak
        limit: Maksimum kaç kayıt döndürülecek
        active_only: Sadece aktif (CONFIRMED, PENDING) rezervasyonlar mı?

    Returns:
        Rezervasyon listesi
    """
    query = db.query(Booking).filter(Booking.resource_id == resource_id)

    if active_only:
        query = query.filter(Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]))

    return query.offset(skip).limit(limit).all()

def get_booking_by_resource_and_timerange(
    db: Session,
    resource_id: UUID,
    start_time: datetime,
    end_time: datetime
) -> List[Booking]:
    """
    Belirli bir kaynak ve zaman aralığındaki rezervasyonları getirir.

    Args:
        db: Veritabanı oturumu
        resource_id: Kaynak ID'si
        start_time: Başlangıç zamanı
        end_time: Bitiş zamanı

    Returns:
        Belirtilen zaman aralığındaki rezervasyonlar
    """
    return db.query(Booking).filter(
        Booking.resource_id == resource_id,
        Booking.start_time >= start_time,
        Booking.end_time <= end_time
    ).all()