# backend/models/availability.py
from sqlalchemy import Column, String, Boolean, DateTime, Date, Time, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from database import Base # SQLAlchemy Base objesini import ediyoruz
# Modelleri models/__init__.py üzerinden import ettiğimiz için burada tek tek gerek yok, ancak SQLAlchemy'nin model bulması için buraya eklenebilir
# from models.user import User
# from models.resource import Resource

# Müsaitlik takvimi tipi için Python Enum'u
class ScheduleType(str, enum.Enum):
    REGULAR = "REGULAR"
    EXCEPTION = "EXCEPTION"

# Haftanın günleri için Python Enum'u
class DayOfWeek(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

class AvailabilitySchedule(Base):
    __tablename__ = "availability_schedules"

    schedule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.resource_id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    day_of_week = Column(Enum(DayOfWeek), nullable=True)
    specific_date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    type = Column(Enum(ScheduleType), nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler: back_populates'ların doğru ve eşleşen isimlere sahip olduğundan emin olun
    resource = relationship("Resource", back_populates="availability_schedules") # BURASI KRİTİK!
    owner = relationship("User", back_populates="availability_schedules") # BURASI KRİTİK!

    def __repr__(self):
        return f"<AvailabilitySchedule(resource_id='{self.resource_id}', date='{self.specific_date or self.day_of_week}', type='{self.type}')>"