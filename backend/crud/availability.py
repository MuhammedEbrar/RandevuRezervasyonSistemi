# backend/crud/availability.py
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date, time

from models.availability import AvailabilitySchedule, ScheduleType, DayOfWeek # Müsaitlik modeli ve Enum'ları
from models.resource import Resource # İlişki için Resource modeli
from schemas.availability import AvailabilityScheduleCreate, AvailabilityScheduleUpdate # Girdi şemaları (ileride oluşturulacak)

# Müsaitlik takvimi girişini ID'ye göre getir
def get_availability_schedule_by_id(db: Session, schedule_id: UUID) -> Optional[AvailabilitySchedule]:
    return db.query(AvailabilitySchedule).filter(AvailabilitySchedule.schedule_id == schedule_id).first()

# Belirli bir kaynak için tüm müsaitlik takvimi girişlerini getir
def get_availability_schedules_for_resource(
    db: Session,
    resource_id: UUID,
    owner_id: UUID, # Multi-tenancy ve güvenlik için
    skip: int = 0,
    limit: int = 100
) -> List[AvailabilitySchedule]:
    return db.query(AvailabilitySchedule).filter(
        AvailabilitySchedule.resource_id == resource_id,
        AvailabilitySchedule.owner_id == owner_id # Sahip kimliği ile filtreleme
    ).offset(skip).limit(limit).all()

# Yeni bir müsaitlik takvimi girişi oluştur
def create_availability_schedule(
    db: Session,
    schedule_in: AvailabilityScheduleCreate,
    resource_id: UUID,
    owner_id: UUID
) -> AvailabilitySchedule:
    db_schedule = AvailabilitySchedule(
        **schedule_in.model_dump(),
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