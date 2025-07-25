# backend/routers/availability.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path as FastAPIPath
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date, datetime, time, timedelta, timezone

# Proje içi importlar
from database import get_db
from crud import availability as crud_availability
from crud import resource as crud_resource
from crud import bookings as crud_bookings
from schemas.availability import AvailabilityScheduleCreate, AvailabilityScheduleUpdate, AvailabilityScheduleOut
from models import User, Resource, Booking, BookingStatus, DayOfWeek, ScheduleType, BookingType, AvailabilitySchedule
from core.security import get_current_user

router = APIRouter(prefix="/resources/{resource_id}/availability", tags=["Availability & Slots"])

# --- YARDIMCI FONKSİYONLAR ---
def check_resource_ownership(db: Session, current_user: User, resource_id: UUID):
    db_resource = crud_resource.get_resource_by_id(db, resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı.")
    if db_resource.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu kaynağa erişim yetkiniz yok.")
    return db_resource

# --- MÜSAİTLİK KURALI YÖNETİMİ ---

@router.post("/", response_model=AvailabilityScheduleOut, status_code=status.HTTP_201_CREATED)
async def create_availability_schedule(
    resource_id: UUID = FastAPIPath(...),
    schedule_in: AvailabilityScheduleCreate = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Belirli bir kaynak için yeni bir müsaitlik kuralı oluşturur."""
    check_resource_ownership(db, current_user, resource_id)
    if schedule_in.start_time >= schedule_in.end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Başlangıç saati bitiş saatinden önce olmalıdır.")
    return crud_availability.create_availability_schedule(
        db=db, schedule_in=schedule_in, resource_id=resource_id, owner_id=current_user.user_id
    )

# --- MÜSAİT ZAMAN ARALIĞI HESAPLAMA (ANA FONKSİYON) ---

@router.get("/available_slots", response_model=List[dict])
async def get_available_slots_for_resource(
    resource_id: UUID = FastAPIPath(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    if start_date > end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Başlangıç tarihi bitiş tarihinden sonra olamaz.")

    db_resource = crud_resource.get_resource_by_id(db, resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı.")

    all_schedules = crud_availability.get_availability_schedules_for_resource(db, resource_id=resource_id, start_date=start_date, end_date=end_date)
    relevant_bookings = db.query(Booking).filter(
        Booking.resource_id == resource_id,
        Booking.end_time > datetime.combine(start_date, time.min, tzinfo=timezone.utc),
        Booking.start_time < datetime.combine(end_date, time.max, tzinfo=timezone.utc),
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING])
    ).all()

    # --- REZERVASYON TİPİNE GÖRE MANTIK AYRIMI ---
    if db_resource.booking_type == BookingType.SLOT_BASED:
        # --- 1. SLOT TABANLI MANTIK (Kütüphane Senaryosu) ---
        potential_slots = {}
        slot_duration_minutes = 30
        
        current_date_iter = start_date
        while current_date_iter <= end_date:
            day_of_week_enum = DayOfWeek(current_date_iter.strftime('%A').upper())
            daily_rules = [s for s in all_schedules if s.is_available and ((s.type == ScheduleType.REGULAR and s.day_of_week == day_of_week_enum) or (s.type == ScheduleType.EXCEPTION and s.specific_date == current_date_iter))]
            blocking_rules = [s for s in all_schedules if not s.is_available and s.type == ScheduleType.EXCEPTION and s.specific_date == current_date_iter]

            for rule in daily_rules:
                slot_start = datetime.combine(current_date_iter, rule.start_time).replace(tzinfo=timezone.utc)
                slot_end = datetime.combine(current_date_iter, rule.end_time).replace(tzinfo=timezone.utc)
                
                while slot_start < slot_end:
                    current_slot_end = slot_start + timedelta(minutes=slot_duration_minutes)
                    if current_slot_end > slot_end: break
                    
                    is_blocked = any(slot_start < datetime.combine(current_date_iter, block.end_time).replace(tzinfo=timezone.utc) and current_slot_end > datetime.combine(current_date_iter, block.start_time).replace(tzinfo=timezone.utc) for block in blocking_rules)
                    
                    if not is_blocked:
                        potential_slots[slot_start] = {"end_time": current_slot_end, "capacity_available": db_resource.capacity}
                    
                    slot_start = current_slot_end
            current_date_iter += timedelta(days=1)

        for booking in relevant_bookings:
            for slot_start, slot_data in potential_slots.items():
                if booking.start_time < slot_data["end_time"] and booking.end_time > slot_start:
                    slot_data["capacity_available"] -= 1

        final_slots = []
        for slot_start, slot_data in sorted(potential_slots.items()):
            if slot_data["capacity_available"] > 0:
                final_slots.append({"start_time": slot_start.isoformat(), "end_time": slot_data["end_time"].isoformat(), "capacity_available": slot_data["capacity_available"]})
        return final_slots

    else: # booking_type == BookingType.DURATION_BASED
        # --- 2. SÜRE TABANLI MANTIK (Halı Saha Senaryosu) ---
        available_blocks = []
        current_date_iter = start_date
        while current_date_iter <= end_date:
            day_of_week_enum = DayOfWeek(current_date_iter.strftime('%A').upper())
            daily_rules = [s for s in all_schedules if s.is_available and ((s.type == ScheduleType.REGULAR and s.day_of_week == day_of_week_enum) or (s.type == ScheduleType.EXCEPTION and s.specific_date == current_date_iter))]
            for rule in daily_rules:
                start_dt = datetime.combine(current_date_iter, rule.start_time).replace(tzinfo=timezone.utc)
                end_dt = datetime.combine(current_date_iter, rule.end_time).replace(tzinfo=timezone.utc)
                available_blocks.append({"start": start_dt, "end": end_dt})
            current_date_iter += timedelta(days=1)
        
        for booking in relevant_bookings:
            booking_start_utc = booking.start_time.astimezone(timezone.utc)
            booking_end_utc = booking.end_time.astimezone(timezone.utc)
            
            new_blocks = []
            for block in available_blocks:
                if booking_end_utc <= block["start"] or booking_start_utc >= block["end"]:
                    new_blocks.append(block)
                    continue
                if booking_start_utc > block["start"]:
                    new_blocks.append({"start": block["start"], "end": booking_start_utc})
                if booking_end_utc < block["end"]:
                    new_blocks.append({"start": booking_end_utc, "end": block["end"]})
            available_blocks = new_blocks
            
        return [{"start_time": b["start"].isoformat(), "end_time": b["end"].isoformat()} for b in available_blocks]