# backend/crud/availability.py
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date, time, datetime

from models.booking import Booking, BookingStatus 
from models.availability import AvailabilitySchedule, ScheduleType, DayOfWeek # Müsaitlik modeli ve Enum'ları
from models.resource import Resource # İlişki için Resource modeli (Resource modelinin import edildiğinden emin olun)
from schemas.availability import AvailabilityScheduleCreate, AvailabilityScheduleUpdate # Girdi şemaları

# Müsaitlik takvimi girişini ID'ye göre getir
def get_availability_schedule_by_id(db: Session, schedule_id: UUID) -> Optional[AvailabilitySchedule]:
    return db.query(AvailabilitySchedule).filter(AvailabilitySchedule.schedule_id == schedule_id).first()

# Belirli bir kaynak için tüm müsaitlik takvimi girişlerini getir
def get_availability_schedules_for_resource(
    db: Session,
    resource_id: UUID,
    owner_id: UUID, # Multi-tenancy ve güvenlik için
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None, # <-- Yeni eklenen parametre
    end_date: Optional[date] = None    # <-- Yeni eklenen parametre
) -> List[AvailabilitySchedule]:
    query = db.query(AvailabilitySchedule).filter(
        AvailabilitySchedule.resource_id == resource_id,
        AvailabilitySchedule.owner_id == owner_id # Sahip kimliği ile filtreleme
    )

    # Tarih filtrelerini uygula
    if start_date:
        # specific_date üzerinde filtreleme yapıyoruz.
        # REGULAR müsaitliklerin belirli bir tarihi yoksa,
        # bu filtreleme sadece EXCEPTION tipli müsaitlikler için anlamlı olacaktır.
        # Eğer REGULAR müsaitlikler için de bir geçerlilik_başlangıç_tarihi veya benzeri bir alanınız varsa,
        # o alanı kullanmalısınız.
        query = query.filter(AvailabilitySchedule.specific_date >= start_date)

    if end_date:
        query = query.filter(AvailabilitySchedule.specific_date <= end_date)
            
    query = query.offset(skip).limit(limit)
    return query.all()

# Yeni bir müsaitlik takvimi girişi oluştur
def create_availability_schedule(
    db: Session,
    schedule_in: AvailabilityScheduleCreate,
    resource_id: UUID,
    owner_id: UUID
) -> AvailabilitySchedule:
    # schedule_in.model_dump() çağrısının ScheduleType ve DayOfWeek enum'larını doğru işlediğinden emin olun.
    # Pydantic ve SQLAlchemy uyumluluğu için gerekebilir.
    schedule_data = schedule_in.model_dump()
    
    # Enum değerlerini doğrudan aktarmak için:
    # Eğer schedule_in.day_of_week bir Enum üyesi ise, direkt kullanabilirsiniz.
    # Eğer string olarak geliyorsa, DayOfWeek(schedule_data.pop('day_of_week')) gibi dönüştürmeniz gerekebilir.

    db_schedule = AvailabilitySchedule(
        **schedule_data,
        resource_id=resource_id,
        owner_id=owner_id
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

# Müsaitlik takvimi girişini güncelle
def update_availability_schedule(
    db: Session,
    db_schedule: AvailabilitySchedule,
    schedule_update: AvailabilityScheduleUpdate
) -> AvailabilitySchedule:
    # exclude_unset=True, sadece ayarlanmış alanları günceller.
    for key, value in schedule_update.model_dump(exclude_unset=True).items():
        setattr(db_schedule, key, value)
    db.add(db_schedule) # Session'a zaten ekli olabilir, emin olmak için tekrar ekleyebiliriz.
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

# Müsaitlik takvimi girişini sil
def delete_availability_schedule(db: Session, schedule_id: UUID) -> Optional[UUID]:
    db_schedule = db.query(AvailabilitySchedule).filter(AvailabilitySchedule.schedule_id == schedule_id).first()
    if db_schedule:
        db.delete(db_schedule)
        db.commit()
        return schedule_id
    return None

def check_availability(
    db: Session,
    resource_id: UUID,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: Optional[UUID] = None # Güncelleme yaparken kendini hariç tutmak için
) -> bool:

    query = db.query(Booking).filter(
        Booking.resource_id == resource_id,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]) # Sadece aktif/beklemedeki rezervasyonları kontrol et
    )

    if exclude_booking_id:
        query = query.filter(Booking.booking_id != exclude_booking_id)

    query = query.filter(
        Booking.start_time < end_time, # Mevcut rezervasyonun başlangıcı, yeni rezervasyonun bitişinden önce olmalı
        Booking.end_time > start_time  # Mevcut rezervasyonun bitişi, yeni rezervasyonun başlangıcından sonra olmalı
    )
    
    # Çakışan bir rezervasyon varsa, müsait değiliz demektir.
    conflicting_booking = query.first()
    
    return conflicting_booking is None