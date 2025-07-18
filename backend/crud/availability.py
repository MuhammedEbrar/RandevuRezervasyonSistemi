# backend/crud/availability.py
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date, time, timedelta, datetime # timedelta ve datetime eklendi
from sqlalchemy import or_, and_ # or_ ve and_ eklendi

from models import AvailabilitySchedule, ScheduleType, DayOfWeek, Resource
from schemas.availability import AvailabilityScheduleCreate, AvailabilityScheduleUpdate # Girdi şemaları

# Müsaitlik takvimi girişini ID'ye göre getir
def get_availability_schedule_by_id(db: Session, schedule_id: UUID) -> Optional[AvailabilitySchedule]:
    return db.query(AvailabilitySchedule).filter(AvailabilitySchedule.schedule_id == schedule_id).first()

# Belirli bir kaynak için tüm müsaitlik takvimi girişlerini getir
# Tarih filtreleme mantığı güncellendi
def get_availability_schedules_for_resource(
    db: Session,
    resource_id: UUID,
    owner_id: Optional[UUID] = None, # DÜZELTİLDİ: owner_id Optional yapıldı
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[AvailabilitySchedule]:
    query = db.query(AvailabilitySchedule).filter(
        AvailabilitySchedule.resource_id == resource_id
    )

    if owner_id: # Eğer owner_id belirtilmişse filtrele
        query = query.filter(AvailabilitySchedule.owner_id == owner_id)

    # Tarih filtrelerini uygula:
    # Hem specific_date olan EXCEPTIONAL kuralları hem de REGULAR kuralları hesaba katmalıyız.
    # Bu kısım, hangi tarih aralığındaki müsaitlik kurallarını döndüreceğimizin ana mantığıdır.
    if start_date and end_date:
        query = query.filter(
            or_(
                # REGULAR kurallar (day_of_week'e göre geçerli olanlar) her zaman geçerli sayılır,
                # ancak eğer specific_date kısıtı yoksa. Bu kısım daha sonra 'available_slots' içinde
                # her gün için day_of_week ile filtrelenecektir.
                # Bu nedenle, burada sadece specific_date'i olan EXCEPTION kurallarını filtreleyelim:
                and_(
                    AvailabilitySchedule.type == ScheduleType.EXCEPTION,
                    AvailabilitySchedule.specific_date >= start_date,
                    AvailabilitySchedule.specific_date <= end_date
                ),
                # VEYA REGULAR tipli kurallar için specific_date'in None olduğu durumlar
                # Bu, REGULAR kuralların tarih aralığından bağımsız olarak her zaman döndürülmesini sağlar.
                # (DayOfWeek filtresi router'da yapılacak)
                AvailabilitySchedule.type == ScheduleType.REGULAR
            )
        )
    elif start_date: # Sadece başlangıç tarihi belirtilmişse
         query = query.filter(
            or_(
                and_(
                    AvailabilitySchedule.type == ScheduleType.EXCEPTION,
                    AvailabilitySchedule.specific_date >= start_date
                ),
                AvailabilitySchedule.type == ScheduleType.REGULAR
            )
        )
    elif end_date: # Sadece bitiş tarihi belirtilmişse
        query = query.filter(
            or_(
                and_(
                    AvailabilitySchedule.type == ScheduleType.EXCEPTION,
                    AvailabilitySchedule.specific_date <= end_date
                ),
                AvailabilitySchedule.type == ScheduleType.REGULAR
            )
        )

    query = query.offset(skip).limit(limit)
    return query.all()

# Yeni bir müsaitlik takvimi girişi oluştur
def create_availability_schedule(
    db: Session,
    schedule_in: AvailabilityScheduleCreate,
    resource_id: UUID,
    owner_id: UUID
) -> AvailabilitySchedule:
    schedule_data = schedule_in.model_dump()
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
    for key, value in schedule_update.model_dump(exclude_unset=True).items():
        setattr(db_schedule, key, value)
    db.add(db_schedule)
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