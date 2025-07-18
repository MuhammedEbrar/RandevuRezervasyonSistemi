# backend/routers/availability.py
from fastapi import APIRouter, Depends, HTTPException, status, Path as FastAPIPath, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date, time, datetime, timedelta

from database import get_db # Veritabanı oturumu için bağımlılık
from core.security import get_current_user, check_user_role # Mevcut kullanıcıyı ve yetkilendirmeyi almak için
from crud import availability as crud_availability # Müsaitlik CRUD
from crud import resource as crud_resource # Kaynak CRUD (kapasite için)
from schemas.availability import AvailabilityScheduleCreate, AvailabilityScheduleUpdate, AvailabilityScheduleOut # Müsaitlik şemaları
from models import User, UserRole, Resource, AvailabilitySchedule, ScheduleType, DayOfWeek
router = APIRouter(prefix="/resources/{resource_id}/availability", tags=["Availability Schedules"]) # /resources/{resource_id}/availability ile başlayan endpointler

# Helper fonksiyon: Kaynağın mevcut kullanıcıya ait olup olmadığını kontrol etmek için
def check_resource_ownership(
    db: Session,
    current_user: User,
    resource_id: UUID
):
    db_resource = crud_resource.get_resource_by_id(db, resource_id)
    if not db_resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kaynak bulunamadı."
        )
    if db_resource.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu kaynağa erişim yetkiniz yok."
        )
    return db_resource

# Müsaitlik takvimi kuralı oluşturma (sadece işletme sahibi)
@router.post("/", response_model=AvailabilityScheduleOut, status_code=status.HTTP_201_CREATED)
async def create_availability_schedule(
    schedule_in: AvailabilityScheduleCreate, # DÜZELTİLDİ: Body parametresi öne alındı
    resource_id: UUID = FastAPIPath(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # JWT token ile kimlik doğrulama
):
    # Sadece BUSINESS_OWNER rolündeki kullanıcılar müsaitlik kuralı oluşturabilir
    if current_user.role != UserRole.BUSINESS_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sadece işletme sahipleri müsaitlik kuralı oluşturabilir."
        )
    # Kaynağın işletme sahibine ait olduğunu kontrol et
    check_resource_ownership(db, current_user, resource_id)

    # Eğer kural REGULAR ise day_of_week olmalı, EXCEPTION ise specific_date olmalı
    if schedule_in.type == ScheduleType.REGULAR and schedule_in.day_of_week is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="REGULAR tipindeki müsaitlik için day_of_week gereklidir.")
    if schedule_in.type == ScheduleType.EXCEPTION and schedule_in.specific_date is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="EXCEPTION tipindeki müsaitlik için specific_date gereklidir.")
    if schedule_in.start_time >= schedule_in.end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Başlangıç saati bitiş saatinden önce olmalıdır.")

    return crud_availability.create_availability_schedule(
        db=db,
        schedule_in=schedule_in,
        resource_id=resource_id,
        owner_id=current_user.user_id
    )

# Belirli bir kaynak için müsaitlik takvimi kurallarını listeleme
@router.get("/", response_model=List[AvailabilityScheduleOut])
async def get_resource_availability_schedules(
    resource_id: UUID = FastAPIPath(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), # Güvenlik için
    skip: int = 0,
    limit: int = 100
):
    # Kaynağın mevcut kullanıcıya ait olup olmadığını kontrol et (hem sahibi hem de müşteri görebilir, sadece sahibi düzenleyebilir)
    # Sadece sahibi görmek isterse owner_id filtrelemesi kullanılır.
    # Müşteriler de görebilir, bu yüzden burada 403 vermeyelim, sadece filtreleme yapalım
    resources = crud_availability.get_availability_schedules_for_resource(
        db=db, resource_id=resource_id, owner_id=current_user.user_id, skip=skip, limit=limit
    )
    return resources

# Müsaitlik takvimi kuralını güncelleme
@router.put("/{schedule_id}", response_model=AvailabilityScheduleOut)
async def update_availability_schedule(
    schedule_update: AvailabilityScheduleUpdate, # DÜZELTİLDİ: Body parametresi öne alındı
    resource_id: UUID = FastAPIPath(...),
    schedule_id: UUID = FastAPIPath(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_schedule = crud_availability.get_availability_schedule_by_id(db, schedule_id)
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Müsaitlik kuralı bulunamadı."
        )
    # Sadece kuralın sahibinin güncellemesine izin ver
    if db_schedule.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu müsaitlik kuralını güncelleme yetkiniz yok."
        )
    
    # Güncelleme sırasında başlangıç/bitiş saati tutarlılığını kontrol et
    if schedule_update.start_time is not None and schedule_update.end_time is not None:
        if schedule_update.start_time >= schedule_update.end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Başlangıç saati bitiş saatinden önce olmalıdır.")
    elif schedule_update.start_time is not None and db_schedule.end_time is not None:
        if schedule_update.start_time >= db_schedule.end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Başlangıç saati bitiş saatinden önce olmalıdır.")
    elif schedule_update.end_time is not None and db_schedule.start_time is not None:
        if db_schedule.start_time >= schedule_update.end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Başlangıç saati bitiş saatinden önce olmalıdır.")

    updated_schedule = crud_availability.update_availability_schedule(db=db, db_schedule=db_schedule, schedule_update=schedule_update)
    return updated_schedule

# Müsaitlik takvimi kuralını silme
@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_availability_schedule(
    resource_id: UUID = FastAPIPath(...),
    schedule_id: UUID = FastAPIPath(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_schedule = crud_availability.get_availability_schedule_by_id(db, schedule_id)
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Müsaitlik kuralı bulunamadı."
        )
    if db_schedule.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu müsaitlik kuralını silme yetkiniz yok."
        )
    
    deleted_schedule_id = crud_availability.delete_availability_schedule(db=db, schedule_id=schedule_id)
    if not deleted_schedule_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Müsaitlik kuralı silinemedi."
        )
    return {"message": "Müsaitlik kuralı başarıyla silindi."}

# /resources/{resource_id}/availability/available_slots endpoint'i - Burası kompleks kısım!
@router.get("/available_slots", response_model=List[dict])
async def get_available_slots_for_resource(
    resource_id: UUID = FastAPIPath(...),
    start_date: date = Query(..., description="Müsait slotları aramak için başlangıç tarihi"),
    end_date: date = Query(..., description="Müsait slotları aramak için bitiş tarihi"),
    db: Session = Depends(get_db) # DÜZELTİLDİ: current_user bağımlılığı kaldırıldı, böylece halka açık oldu
):
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Başlangıç tarihi bitiş tarihinden sonra olamaz."
        )

    # 1. Kaynak ve sahibini al
    db_resource = crud_resource.get_resource_by_id(db, resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı.")
    

    # DÜZELTİLDİ: crud_availability.get_availability_schedules_for_resource fonksiyonunun owner_id parametresinin Optional olduğunu varsayıyoruz.
    all_schedules = crud_availability.get_availability_schedules_for_resource(
        db,
        resource_id=resource_id,
        owner_id=None, # Bu endpoint'i public yapmak için owner_id'yi None geçiyoruz
        start_date=start_date,
        end_date=end_date
    )

    # Sadece aktif ve müsait olan kuralları dikkate al
    all_schedules = [s for s in all_schedules if s.is_available]

    # 3. Mevcut rezervasyonları al (Hafta 4'te Bookings tablosu eklenecek)
    # Şimdilik Bookings tablosu olmadığı için boş bir liste varsayıyoruz.
    booked_slots = [] # Şimdilik boş


    # 4. Müsait slotları hesapla - Bu kısım bolca iş mantığı içerecektir!
    available_slots = []
    current_date = start_date
    while current_date <= end_date:
        # Haftanın gününü al
        day_of_week_enum = DayOfWeek(current_date.strftime('%A').upper()) # 'MONDAY', 'TUESDAY' vb.

        # Bu güne ait REGULAR müsaitlik kurallarını filtrele
        regular_schedules = [
            s for s in all_schedules
            if s.type == ScheduleType.REGULAR and s.day_of_week == day_of_week_enum
        ]
        
        # Bu tarihe ait EXCEPTION kurallarını filtrele (bloklama ve ek müsaitlik)
        exception_schedules = [
            s for s in all_schedules
            if s.type == ScheduleType.EXCEPTION and s.specific_date == current_date
        ]

        # Günlük müsaitlik slotlarını oluştur (başlangıçta tüm gün boş varsayılır)
        daily_potential_slots = []
        
        # REGULAR kuralları işle
        for rs in regular_schedules:
            current_slot_start = datetime.combine(current_date, rs.start_time)
            slot_end = datetime.combine(current_date, rs.end_time)
            
            slot_duration_minutes = 30 # Sabit 30 dakikalık slotlar varsayımı
            while current_slot_start + timedelta(minutes=slot_duration_minutes) <= slot_end:
                daily_potential_slots.append({
                    "start_time": current_slot_start,
                    "end_time": current_slot_start + timedelta(minutes=slot_duration_minutes),
                    "capacity_available": db_resource.capacity
                })
                current_slot_start += timedelta(minutes=slot_duration_minutes)
        
        # EXCEPTION kurallarını uygula (bloklama ve ek müsaitlik)
        # EXCEPTION tipindeki müsaitlik kurallarını işlerken, eğer is_available=False ise bloklama yapar.
        # Eğer is_available=True ise ek müsaitlik slotları ekler.
        for es in exception_schedules:
            exception_start_dt = datetime.combine(current_date, es.start_time)
            exception_end_dt = datetime.combine(current_date, es.end_time)

            if not es.is_available: # Bloklama kuralı: Bu zaman aralığını müsait slotlardan çıkar
                daily_potential_slots = [
                    slot for slot in daily_potential_slots
                    if not (
                        (slot["start_time"] < exception_end_dt and slot["end_time"] > exception_start_dt)
                    )
                ]
            else: # Ek müsaitlik kuralı: Bu zaman aralığını ek slot olarak ekle
                # Eklenen slotların mevcutlarla çakışmaması ve mükerrer olmaması için mantık eklenebilir.
                # Şimdilik basitçe ekleyelim.
                current_slot_start = exception_start_dt
                slot_duration_minutes = 30
                while current_slot_start + timedelta(minutes=slot_duration_minutes) <= exception_end_dt:
                    new_slot = {
                        "start_time": current_slot_start,
                        "end_time": current_slot_start + timedelta(minutes=slot_duration_minutes),
                        "capacity_available": db_resource.capacity
                    }
                    # Eğer bu slot zaten yoksa ekle (mükerrerliği önlemek için)
                    if new_slot not in daily_potential_slots:
                         daily_potential_slots.append(new_slot)
                    current_slot_start += timedelta(minutes=slot_duration_minutes)

        # Booked slotları dikkate al (Hafta 4'te eklenecek)
        # Şimdilik booked_slots boş olduğu için kapasiteyi düşürme işlemi yapmıyoruz.
        # booked_slots listesini kullanarak capacity_available'ı düşürebiliriz.

        available_slots.extend(daily_potential_slots) # Günlük slotları ana listeye ekle

        current_date += timedelta(days=1) # Sonraki güne geç

    # Slotları başlangıç zamanına göre sırala ve mükerrerleri temizle
    # Datetime objelerini set'e koyabilmek için tuple'a çevirelim
    unique_slots = set()
    for slot in available_slots:
        unique_slots.add(
            (slot["start_time"].isoformat(), slot["end_time"].isoformat(), slot["capacity_available"])
        )
    
    # Tekrarsız ve sıralı hale getir
    final_slots = []
    for start_iso, end_iso, capacity in sorted(list(unique_slots)):
        final_slots.append({
            "start_time": datetime.fromisoformat(start_iso),
            "end_time": datetime.fromisoformat(end_iso),
            "capacity_available": capacity
        })
    
    # Son olarak, datetime objelerini string'e çevirerek Pydantic uyumlu hale getir
    formatted_slots = [
        {
            "start_time": slot["start_time"].isoformat(),
            "end_time": slot["end_time"].isoformat(),
            "capacity_available": slot["capacity_available"]
        } for slot in final_slots
    ]

    return formatted_slots