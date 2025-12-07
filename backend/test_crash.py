
import sys
import os
import traceback
# Backend klasörünü path'e ekle
sys.path.append(os.getcwd())

from database import SessionLocal, engine, Base
from models import Resource, User, UserRole, ResourceType, AvailabilitySchedule, ScheduleType, DayOfWeek, Booking, BookingStatus, BookingType
from crud import availability as crud_availability
from crud import resource as crud_resource
from sqlalchemy.orm import Session
import datetime
from datetime import time, timedelta, timezone
import uuid

# Veritabanını sıfırla (temiz test için)
# Base.metadata.drop_all(bind=engine) 
# Base.metadata.create_all(bind=engine)
# MEVCUT VERİTABANINI KULLANALIM Ki ZATEN HATA VERİYOR DU

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_test():
    db = SessionLocal()
    try:
        print("Starting test...")
        
        # 1. Kaynak bul veya oluştur
        resource = db.query(Resource).first()
        if not resource:
            print("No resource found, creating one...")
            user_id = uuid.uuid4()
            user = User(user_id=user_id, email=f"test{uuid.uuid4()}@a.com", password_hash="x", role=UserRole.BUSINESS_OWNER)
            db.add(user)
            db.commit()
            
            # TEST CASE: RESOURCE WITH NONE CAPACITY
            resource_id = uuid.uuid4()
            resource = Resource(resource_id=resource_id, owner_id=user_id, name="TestRes_NullCap", type=ResourceType.MEKAN, capacity=None, is_active=True, booking_type=BookingType.SLOT_BASED)
            db.add(resource)
            
            schedule = AvailabilitySchedule(
                schedule_id=uuid.uuid4(), resource_id=resource_id, owner_id=user_id,
                day_of_week=DayOfWeek.MONDAY, start_time=time(9,0), end_time=time(17,0),
                type=ScheduleType.REGULAR, is_available=True
            )
            db.add(schedule)
            db.commit()
            print(f"Created resource {resource_id} with NULL CAPACITY")
        else:
            print(f"Using resource {resource.resource_id}")
            # Ensure it has null capacity for testing
            resource.capacity = None
            db.commit()
            print("Forced resource capacity to None for testing.")

        resource_id = resource.resource_id
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=30)
        
        print(f"Testing logic for range {start_date} to {end_date}")
        
        # --- LOGIC FROM ROUTER ---
        if start_date > end_date:
            print("Bad date range")
            return

        db_resource = crud_resource.get_resource_by_id(db, resource_id)
        print(f"Resource found: {db_resource.name}")

        all_schedules = crud_availability.get_availability_schedules_for_resource(db, resource_id=resource_id, start_date=start_date, end_date=end_date)
        print(f"Schedules found: {len(all_schedules)}")
        
        # SORGUNUN HATALI OLMA OLASILIĞI YÜKSEK
        relevant_bookings = db.query(Booking).filter(
            Booking.resource_id == resource_id,
            Booking.end_time > datetime.datetime.combine(start_date, time.min, tzinfo=timezone.utc),
            Booking.start_time < datetime.datetime.combine(end_date, time.max, tzinfo=timezone.utc),
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING])
        ).all()
        print(f"Bookings found: {len(relevant_bookings)}")

        if db_resource.booking_type == BookingType.SLOT_BASED:
            print("Calculating SLOT BASED...")
            potential_slots = {}
            slot_duration_minutes = 30
            
            days_mapping = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
            current_date_iter = start_date
            while current_date_iter <= end_date:
                # Fix locale issue: use weekday() index instead of strftime('%A')
                day_of_week_enum = DayOfWeek(days_mapping[current_date_iter.weekday()])
                
                # SIKIŞMA NOKTASI: DATE vs DATETIME
                # daily_rules = [s for s in all_schedules if s.is_available and ((s.type == ScheduleType.REGULAR and s.day_of_week == day_of_week_enum) or (s.type == ScheduleType.EXCEPTION and s.specific_date == current_date_iter))]
                # s.specific_date veritabanından DATE olarak dönüyor. current_date_iter DATE objesi. Karşılaştırma OK.
                
                daily_rules = []
                blocking_rules = []
                
                for s in all_schedules:
                     # Basit print ile debug
                     # print(f"Checking schedule {s.type} {s.day_of_week}")
                     
                     if s.is_available:
                         match_regular = (s.type == ScheduleType.REGULAR and s.day_of_week == day_of_week_enum)
                         match_exception = (s.type == ScheduleType.EXCEPTION and s.specific_date == current_date_iter)
                         if match_regular or match_exception:
                             daily_rules.append(s)
                     else:
                         if s.type == ScheduleType.EXCEPTION and s.specific_date == current_date_iter:
                             blocking_rules.append(s)

                for rule in daily_rules:
                    # TIMEZONE HANDLING
                    # rule.start_time time objesi. combine edince naive datetime olur. .replace(tzinfo=utc) ekliyoruz.
                    slot_start = datetime.datetime.combine(current_date_iter, rule.start_time).replace(tzinfo=timezone.utc)
                    slot_end = datetime.datetime.combine(current_date_iter, rule.end_time).replace(tzinfo=timezone.utc)
                    
                    while slot_start < slot_end:
                        current_slot_end = slot_start + datetime.timedelta(minutes=slot_duration_minutes)
                        if current_slot_end > slot_end: break
                        
                        is_blocked = False
                        # BLOCKING CHECK
                        # any(...)
                        
                        if not is_blocked:
                            potential_slots[slot_start] = {"end_time": current_slot_end, "capacity_available": db_resource.capacity}
                        slot_start = current_slot_end
                current_date_iter += datetime.timedelta(days=1)
            
            print("Slots calculated successfully.")
            
    except Exception as e:
        print("CRASHED IN LOGIC!")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
