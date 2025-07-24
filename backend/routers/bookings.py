# backend/routers/bookings.py
from fastapi import APIRouter, Depends, HTTPException, status, Path as FastAPIPath, Query # Query eklendi
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

from database import get_db
from core.security import get_current_user, check_user_role
from crud import bookings as crud_booking
from crud import resource as crud_resource
from crud import pricing as crud_pricing

from schemas.booking import BookingCreate, BookingOut, BookingCalculatePriceRequest, BookingCalculatePriceResponse, BookingStatusUpdate, BookingPaymentStatusUpdate
from models import User, UserRole
from models import BookingStatus

router = APIRouter(prefix="/bookings", tags=["Bookings"])

# --- Fiyat Hesaplama Endpoint'i ---
@router.post("/calculate_price", response_model=BookingCalculatePriceResponse, status_code=status.HTTP_200_OK)
async def calculate_price(
    data: BookingCalculatePriceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.end_time <= data.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bitiş zamanı başlangıç zamanından sonra olmalıdır.")

    db_resource = crud_resource.get_resource_by_id(db, data.resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı.")

    pricing_rule = crud_pricing.get_applicable_pricing_rule(
        db,
        resource_id=data.resource_id,
        booking_start_time=data.start_time,
        booking_end_time=data.end_time,
        owner_id=db_resource.owner_id
    )

    if not pricing_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Belirtilen kaynak ve zaman için uygun fiyatlandırma kuralı bulunamadı.")

    duration_hours = (data.end_time - data.start_time).total_seconds() / 3600
    
    if pricing_rule.duration_type == "PER_HOUR":
        total_price = duration_hours * float(pricing_rule.base_price)
    elif pricing_rule.duration_type == "FIXED_PRICE":
        total_price = duration_hours * float(pricing_rule.base_price)
    else:
        total_price = duration_hours * float(pricing_rule.base_price)

    return BookingCalculatePriceResponse(total_price=round(total_price, 2))

# --- Rezervasyon Oluşturma Endpoint'i ---
@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sadece müşteriler rezervasyon oluşturabilir."
        )

    db_resource = crud_resource.get_resource_by_id(db, booking_in.resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı.")
    
    if booking_in.end_time <= booking_in.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bitiş zamanı başlangıç zamanından sonra olmalıdır.")
    
    try:
        new_booking = crud_booking.create_booking(
            db,
            booking_in=booking_in,
            customer_id=current_user.user_id,
            owner_id=db_resource.owner_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    return new_booking

# --- Müşterinin Kendi Rezervasyonlarını Listeleme ---
@router.get("/customer", response_model=List[BookingOut])
async def get_customer_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sadece müşteriler kendi rezervasyonlarını listeleme yetkisine sahiptir.")
    
    bookings = crud_booking.get_bookings_by_customer(db, current_user.user_id, skip, limit)
    return bookings

# --- İşletme Sahibinin Kendi Varlıklarına Yapılan Rezervasyonları Listeleme ---
@router.get("/owner", response_model=List[BookingOut])
async def get_owner_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])),
    skip: int = 0,
    limit: int = 100
):
    bookings = crud_booking.get_bookings_by_owner(db, current_user.user_id, skip, limit)
    return bookings

# --- Rezervasyon Durumu Güncelleme (İşletme Sahibi/Admin) ---
@router.put("/{booking_id}/status", response_model=BookingOut)
async def update_booking_status(
    status_update: BookingStatusUpdate, # DÜZELTİLDİ: Body parametresi öne alındı
    booking_id: UUID = FastAPIPath(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER]))
):
    db_booking = crud_booking.get_booking_by_id(db, booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon bulunamadı.")
    
    if db_booking.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rezervasyonu güncelleme yetkiniz yok.")
    
    updated_booking = crud_booking.update_booking_status(db, db_booking, status_update)
    return updated_booking

# --- Rezervasyon Ödeme Durumu Güncelleme (Webhook/Ödeme sağlayıcısı için) ---
@router.put("/{booking_id}/payment_status", response_model=BookingOut) # Yeni endpoint eklendi
async def update_booking_payment_status(
    payment_status_update: BookingPaymentStatusUpdate, # DÜZELTİLDİ: Body parametresi öne alındı
    booking_id: UUID = FastAPIPath(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])) # Sadece işletme sahibi güncelleyebilir
):
    db_booking = crud_booking.get_booking_by_id(db, booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon bulunamadı.")
    
    if db_booking.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rezervasyonu güncelleme yetkiniz yok.")
    
    updated_booking = crud_booking.update_booking_payment_status(db, db_booking, payment_status_update)
    return updated_booking

@router.put("/{booking_id}/cancel", response_model=BookingOut) # Veya BookingResponse
async def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Rezervasyon sahibi veya ilgili işletme sahibi iptal edebilir
):
    # 1. Rezervasyonu bul
    db_booking = crud_booking.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon bulunamadı.")

    # 2. Yetkilendirme Kontrolü
    # Sadece rezervasyonun sahibi (customer) veya ilgili kaynağın sahibi (business owner) iptal edebilir.
    # ADMIN rolü varsa, o da iptal edebilir.
    
    is_customer = str(db_booking.customer_id) == str(current_user.user_id)
    is_owner_of_resource = str(db_booking.owner_id) == str(current_user.user_id) # Booking modelinde owner_id varsa

    if not (is_customer or is_owner_of_resource): # if not (is_customer or is_owner_of_resource or current_user.role == UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rezervasyonu iptal etme yetkiniz yok.")
    
    # 3. Rezervasyonun zaten iptal edilmiş olup olmadığını kontrol et
    if db_booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rezervasyon zaten iptal edilmiş durumda.")
    
    # 4. Rezervasyon durumunu CANCELLED olarak güncelle
    # crud_bookings.update_booking_status fonksiyonunu kullanıyoruz
    status_update_data = BookingStatusUpdate(status=BookingStatus.CANCELLED)
    cancelled_booking = crud_booking.update_booking_status(db, booking=db_booking, status_update=status_update_data)
    
    # Kapora iadesi mantığı burada daha sonra eklenebilir.
    # Örneğin: if db_booking.payment_status == PaymentStatus.PAID:
    #             # Ödeme iade mekanizmasını çağır (mock veya gerçek)
    #             # db_booking.payment_status = PaymentStatus.REFUNDED
    #             # crud_bookings.update_booking_payment_status(...)

    return cancelled_booking

# --- Rezervasyon Silme (İşletme Sahibi/Admin) ---
@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: UUID = FastAPIPath(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER]))
):
    db_booking = crud_booking.get_booking_by_id(db, booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon bulunamadı.")
    
    if db_booking.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rezervasyonu silme yetkiniz yok.")
    
    crud_booking.delete_booking(db, booking_id)
    return # 204 No Content yanıtı için gövdeye gerek yoktur