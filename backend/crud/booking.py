# backend/crud/booking.py
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.exc import IntegrityError # Veritabanı bütünlüğü hataları için

from models.booking import Booking, BookingStatus, PaymentStatus # Booking modeli ve Enum'ları
from models.resource import Resource # Kapasite ve varlık tipi için
# DÜZELTİLDİ: BookingCreate ve BookingUpdate şemaları eklendi
from schemas.booking import BookingCreate, BookingStatusUpdate, BookingPaymentStatusUpdate, BookingCalculatePriceRequest, BookingCalculatePriceResponse, BookingOut
from crud.pricing import get_applicable_pricing_rule # Fiyat hesaplama için
# from crud.availability import get_available_slots_for_resource # Müsaitlik kontrolü için (router'dan çağrılabilir)

# Booking'i ID'ye göre getir
def get_booking_by_id(db: Session, booking_id: UUID) -> Optional[Booking]:
    return db.query(Booking).filter(Booking.booking_id == booking_id).first()

# Bir müşterinin tüm rezervasyonlarını listele
def get_bookings_by_customer(db: Session, customer_id: UUID, skip: int = 0, limit: int = 100) -> List[Booking]:
    return db.query(Booking).filter(Booking.customer_id == customer_id).offset(skip).limit(limit).all()

# Bir işletme sahibinin varlıklarına yapılan tüm rezervasyonları listele
def get_bookings_by_owner(db: Session, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[Booking]:
    # Bu fonksiyon, işletme sahibinin sahibi olduğu kaynaklara yapılan tüm rezervasyonları listeler.
    return db.query(Booking).filter(Booking.owner_id == owner_id).offset(skip).limit(limit).all()

# Yeni bir rezervasyon oluştur
def create_booking(db: Session, booking_in: BookingCreate, customer_id: UUID, owner_id: UUID) -> Booking:
    # Fiyatlandırma kuralını bul ve toplam fiyatı hesapla
    # Bu kısım router'dan da çağrılabilir, ancak CRUD içinde de mantıklı olabilir
    pricing_rule = get_applicable_pricing_rule(
        db,
        resource_id=booking_in.resource_id,
        booking_start_time=booking_in.start_time,
        booking_end_time=booking_in.end_time,
        owner_id=owner_id # Opsiyonel: Kuralı sahibine göre de filtrelemek için
    )

    if not pricing_rule:
        raise ValueError("Belirtilen kaynak ve zaman için uygun fiyatlandırma kuralı bulunamadı.")

    # Basit fiyat hesaplama (pricing_rule modelinize göre uyarlayın)
    duration_hours = (booking_in.end_time - booking_in.start_time).total_seconds() / 3600
    total_price = duration_hours * pricing_rule.base_price # Örnek: base_price'ı kullanıyoruz
    
    # Müsaitlik kontrolü de burada veya router katmanında yapılabilir
    # Örneğin, crud_availability.get_available_slots_for_resource çağrılarak yerin müsait olup olmadığı kontrol edilebilir.
    # Bu kısım, henüz "available_slots" fonksiyonunu burada kullanmayız, sadece mantığını belirtiyoruz.

    db_booking = Booking(
        **booking_in.model_dump(),
        customer_id=customer_id,
        owner_id=owner_id,
        total_price=total_price,
        status=BookingStatus.PENDING, # Başlangıçta beklemede
        payment_status=PaymentStatus.PENDING # Başlangıçta ödeme beklemede
    )
    try:
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    except IntegrityError:
        db.rollback()
        raise ValueError("Rezervasyon oluşturulurken veritabanı hatası oluştu.")

# Rezervasyon durumunu güncelleme (Admin/işletme sahibi için)
def update_booking_status(db: Session, booking: Booking, status_update: BookingStatusUpdate) -> Booking:
    booking.status = status_update.status
    booking.updated_at = datetime.now() # Güncelleme tarihini manuel ayarla
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

# Rezervasyon ödeme durumunu güncelleme (Webhook/Ödeme sağlayıcısı için)
def update_booking_payment_status(db: Session, booking: Booking, payment_status_update: BookingPaymentStatusUpdate) -> Booking:
    booking.payment_status = payment_status_update.payment_status
    booking.updated_at = datetime.now() # Güncelleme tarihini manuel ayarla
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

# Rezervasyon silme
def delete_booking(db: Session, booking_id: UUID) -> Optional[UUID]:
    db_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if db_booking:
        db.delete(db_booking)
        db.commit()
        return booking_id
    return None