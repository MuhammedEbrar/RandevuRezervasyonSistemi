# backend/models/availability.py
from sqlalchemy import Column, String, Boolean, DateTime, Date, Time, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID # UUID için
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship # İlişkiler için
import uuid # uuid.uuid4 için
import enum # Python'ın kendi enum'u

from database import Base # SQLAlchemy Base objesini import ediyoruz
from models.user import User # User modeli için (owner_id ilişkisi için)
from models.resource import Resource # Resource modeli için (resource_id ilişkisi için)

# Müsaitlik takvimi tipi için Python Enum'u
class ScheduleType(str, enum.Enum):
    REGULAR = "REGULAR"   # Düzenli çalışma saatleri (örn: her Salı 09:00-17:00)
    EXCEPTION = "EXCEPTION" # İstisnai durumlar (örn: 15 Ağustos kapalı, 20 Ağustos ekstra mesai)

# Haftanın günleri için Python Enum'u (isteğe bağlı, string de kullanılabilir)
class DayOfWeek(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

class AvailabilitySchedule(Base):
    __tablename__ = "availability_schedules" # Veritabanındaki tablo adı

    schedule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.resource_id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False) # Redundant ama faydalı [cite: 546]
    day_of_week = Column(Enum(DayOfWeek), nullable=True) # Hangi gün (REGULAR için)
    specific_date = Column(Date, nullable=True) # Hangi tarih (EXCEPTION için)
    start_time = Column(Time, nullable=False) # Müsaitlik başlangıç saati
    end_time = Column(Time, nullable=False) # Müsaitlik bitiş saati
    type = Column(Enum(ScheduleType), nullable=False) # Müsaitlik tipi (REGULAR veya EXCEPTION)
    is_available = Column(Boolean, default=True) # Müsaitlik durumu (True: müsait, False: bloklu)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # İlişkiler
    resource = relationship("Resource", back_populates="availability_schedules") # Resource modeli ile ilişki
    owner = relationship("User", back_populates="availability_schedules") # User modeli ile ilişki

    def __repr__(self):
        return f"<AvailabilitySchedule(resource_id='{self.resource_id}', date='{self.specific_date or self.day_of_week}', type='{self.type}')>"

# Resource modeline ilişkinin eklenmesi (eğer daha önce User modelinde yapmadıysak)
# User modeline resource ilişkisi eklenmeli
# from models.user import User # Bu import zaten yapıldı, yeniden yapmaya gerek yok
# User.resources = relationship("Resource", back_populates="owner")
# User.availability_schedules = relationship("AvailabilitySchedule", back_populates="owner")

# Resource modeline availability_schedules ilişkisi eklenmeli
# from models.resource import Resource # Bu import zaten yapıldı, yeniden yapmaya gerek yok
# Resource.availability_schedules = relationship("AvailabilitySchedule", back_populates="resource")