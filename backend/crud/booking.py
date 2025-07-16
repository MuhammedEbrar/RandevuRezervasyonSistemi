# backend/crud/booking.py
from decimal import Decimal
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.exc import IntegrityError # Veritabanı bütünlüğü hataları için

from models.booking import Booking, BookingStatus, PaymentStatus # Booking modeli ve Enum'ları
from models.resource import Resource # Kapasite ve varlık tipi için
from schemas.booking import BookingCreate, BookingStatusUpdate, BookingPaymentStatusUpdate, BookingUpdate # Girdi şemaları
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
    pricing_rule = get_applicable_pricing_rule(
        db,
        resource_id=booking_in.resource_id,
        booking_start_time=booking_in.start_time,
        booking_end_time=booking_in.end_time,
        owner_id=owner_id
    )

    if not pricing_rule:
        raise ValueError("Belirtilen kaynak ve zaman için uygun fiyatlandırma kuralı bulunamadı.")

    duration_hours = (booking_in.end_time - booking_in.start_time).total_seconds() / 3600

    # Booking modelinde total_price DECIMAL olduğu için, sonucu Decimal'e dönüştürmek en tutarlı olur.
    total_price = Decimal(str(duration_hours * float(pricing_rule.base_price)))


    db_booking = Booking(
        **booking_in.model_dump(),
        customer_id=customer_id,
        owner_id=owner_id,
        total_price=total_price, # Decimal objesi olarak atıyoruz
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
    
def update_booking(
    db: Session,
    db_booking: Booking, # Veritabanından çekilmiş mevcut Booking objesi
    booking_update: BookingUpdate # Güncelleme için Pydantic şeması
) -> Booking:
    """
    Bir rezervasyonun belirli alanlarını günceller.
    """
    # Sadece Pydantic şemasında set edilmiş (yani JSON'da gönderilmiş) alanları al.
    update_data = booking_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        # Eğer güncellenen alan total_price ise ve Decimal ise, tip dönüşümüne dikkat edin
        if key == "total_price" and isinstance(value, float):
            setattr(db_booking, key, Decimal(str(value)))
        else:
            setattr(db_booking, key, value)

    # updated_at'ı manuel olarak da güncelleyebilirsiniz, ancak modelde onupdate=func.now() varsa otomatik olur.
    # db_booking.updated_at = datetime.now() 

    db.add(db_booking) # Değişiklikleri session'a ekle (objenin zaten bağlı olması durumunda sorun yaratmaz)
    db.commit() # Değişiklikleri veritabanına kaydet
    db.refresh(db_booking) # Güncellenmiş verilerle objeyi yenile
    return db_booking

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