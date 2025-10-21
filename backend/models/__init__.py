# backend/models/__init__.py
# Bu dosya, tüm modellerimizi bir araya getirerek SQLAlchemy'nin
# ilişkileri doğru bir şekilde haritalamasını sağlar.

from .user import User, UserRole
from .resource import Resource, ResourceType, BookingType
from .availability import AvailabilitySchedule, ScheduleType, DayOfWeek
from .pricing import PricingRule, DurationType, ApplicableDay
from .booking import Booking, BookingStatus
from .payment import Payment, PaymentStatus


# __all__ tanımı, bu paketten * ile import yapıldığında nelerin dışa aktarılacağını belirler.
# Bu satırlar zorunlu değil, ancak iyi bir pratiktir.
__all__ = [
    "User", "UserRole",
    "Resource", "ResourceType",
    "AvailabilitySchedule", "ScheduleType", "DayOfWeek",
    "PricingRule", "DurationType", "ApplicableDay",
    "Booking", "BookingStatus", "PaymentStatus",
    "Payment"
]