# backend/routers/__init__.py
from . import auth
from . import resource
from . import availability # Yeni eklenen router modülü
from . import pricing # Fiyatlandırma router'ı da buraya eklenecek
from . import bookings # Bookings router'ı da buraya eklenecek (Hafta 4)
from . import payments
# ... diğer router'lar