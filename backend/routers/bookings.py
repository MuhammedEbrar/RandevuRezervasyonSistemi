# backend/routers/bookings.py
from fastapi import APIRouter, Depends, HTTPException, status # status import edildi
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, date # date de eklendi, pricing rule'da date kullanabiliriz
from uuid import UUID

from database import get_db
from crud import pricing as crud_pricing
from crud.pricing import get_applicable_pricing_rule # <-- Bu satırı değiştirdik
# Kimlik doğrulama için gerekli importlar
from models.user import User # User modelini import edin
from core.security import get_current_user # get_current_user fonksiyonunu import edin

router = APIRouter(
    prefix="/bookings", # Bu router'daki tüm yollar /bookings ile başlayacak
    tags=["Bookings"] # Swagger UI'da görünmesi için etiket
)

# Fiyat hesaplama isteği için Pydantic şeması (mevcut PriceRequest'i kullanıyoruz)
class PriceRequest(BaseModel):
    resource_id: UUID
    start_time: datetime
    end_time: datetime

# Fiyat yanıtı için Pydantic şeması (mevcut PriceResponse'u kullanıyoruz)
class PriceResponse(BaseModel):
    total_price: float

@router.post("/calculate_price", response_model=PriceResponse, status_code=status.HTTP_200_OK)
async def calculate_price(
    data: PriceRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.end_time <= data.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bitiş zamanı başlangıç zamanından sonra olmalıdır.")

    pricing_rule = crud_pricing.get_applicable_pricing_rule(
        db, 
        resource_id=data.resource_id, 
        booking_start_time=data.start_time, 
        booking_end_time=data.end_time,
        owner_id=current_user.user_id 
    )

    if not pricing_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Belirtilen kaynak ve zaman için uygun fiyatlandırma kuralı bulunamadı.")

    duration_hours = (data.end_time - data.start_time).total_seconds() / 3600

    # Hata veren satırı düzelttik: pricing_rule.base_price'ı float'a dönüştürüyoruz
    total_price = duration_hours * float(pricing_rule.base_price) 

    return PriceResponse(total_price=round(total_price, 2))

# --- Diğer booking endpoint'leriniz buraya devam eder ---