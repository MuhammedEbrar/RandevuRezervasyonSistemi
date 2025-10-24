# backend/routers/bookings.py

from fastapi import APIRouter, Depends, HTTPException, status, Path as FastAPIPath
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime, time, timedelta

# Proje içi importlar
from database import get_db
from core.security import get_current_user, check_user_role
from crud import bookings as crud_bookings
from crud import resource as crud_resource
from crud import pricing as crud_pricing

# Şemalar ve Modeller
from schemas.booking import (
    BookingCreate, BookingOut, BookingCalculatePriceRequest,
    BookingCalculatePriceResponse, BookingStatusUpdate, BookingPaymentStatusUpdate
)
from models import User, UserRole, Booking, BookingStatus

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/calculate_price", response_model=BookingCalculatePriceResponse, status_code=status.HTTP_200_OK)
async def calculate_price(
    data: BookingCalculatePriceRequest,
    db: Session = Depends(get_db)
):
    """Verilen kaynak ve zaman aralığı için tahmini rezervasyon ücretini hesaplar."""
    if data.end_time <= data.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bitiş zamanı başlangıç zamanından sonra olmalıdır.")

    pricing_rule = crud_pricing.get_applicable_pricing_rule(
        db, resource_id=data.resource_id, booking_start_time=data.start_time, booking_end_time=data.end_time
    )

    if not pricing_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Belirtilen kaynak ve zaman için uygun fiyatlandırma kuralı bulunamadı.")

    total_price = crud_pricing.calculate_price_from_rule(
        pricing_rule=pricing_rule,
        start_time=data.start_time,
        end_time=data.end_time
    )
    return BookingCalculatePriceResponse(total_price=total_price)


@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Yeni bir rezervasyon oluşturur ve oluşturmadan önce tüm kuralları kontrol eder."""
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sadece müşteriler rezervasyon oluşturabilir.")

    db_resource = crud_resource.get_resource_by_id(db, booking_in.resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı.")

    if booking_in.end_time <= booking_in.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bitiş zamanı başlangıç zamanından sonra olmalıdır.")

    # ÇAKIŞMA KONTROLÜ - Çifte rezervasyonu önle
    conflicting_bookings = crud_bookings.check_booking_conflicts(
        db=db,
        resource_id=booking_in.resource_id,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time
    )
    if conflicting_bookings:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Bu zaman diliminde {len(conflicting_bookings)} adet çakışan rezervasyon bulunmaktadır. Lütfen farklı bir zaman seçiniz."
        )

    # 1. Geçerli Fiyat Kuralını Bul
    applicable_rule = crud_pricing.get_applicable_pricing_rule(db, db_resource.resource_id, booking_in.start_time, booking_in.end_time)
    if not applicable_rule:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu zaman aralığı için geçerli bir fiyatlandırma kuralı bulunamadı.")

    # 2. Süre Limitlerini DAKİKA Bazında Kontrol Et
    booking_duration_minutes = (booking_in.end_time - booking_in.start_time).total_seconds() / 60
    if applicable_rule.min_duration and booking_duration_minutes < applicable_rule.min_duration:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Minimum kiralama süresi {applicable_rule.min_duration} dakikadır.")
    if applicable_rule.max_duration and booking_duration_minutes > applicable_rule.max_duration:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Maksimum kiralama süresi {applicable_rule.max_duration} dakikadır.")
    
    # 3. Diğer Limitleri Kontrol Et (Günlük, Müşteri Başına vb.)
    # (Bu kontroller bir önceki cevabımızdaki gibi burada yer alabilir)
    
    # 4. Toplam Fiyatı Hesapla
    total_price = crud_pricing.calculate_price_from_rule(
        pricing_rule=applicable_rule, start_time=booking_in.start_time, end_time=booking_in.end_time
    )

    # 5. Veritabanına Kaydet
    try:
        new_booking = crud_bookings.create_booking(
            db=db, booking_in=booking_in, customer_id=current_user.user_id, owner_id=db_resource.owner_id, total_price=total_price
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return new_booking


@router.get("/customer", response_model=List[BookingOut])
async def get_customer_bookings(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user), skip: int = 0, limit: int = 100
):
    """Mevcut müşterinin kendi rezervasyonlarını listeler."""
    return crud_bookings.get_bookings_by_customer(db, customer_id=current_user.user_id, skip=skip, limit=limit)


@router.get("/owner", response_model=List[BookingOut])
async def get_owner_bookings(
    db: Session = Depends(get_db), current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])), skip: int = 0, limit: int = 100
):
    """Mevcut işletme sahibinin kendi kaynaklarına yapılan tüm rezervasyonları listeler."""
    return crud_bookings.get_bookings_by_owner(db, owner_id=current_user.user_id, skip=skip, limit=limit)


@router.put("/{booking_id}/status", response_model=BookingOut)
async def update_booking_status(
    booking_id: UUID, status_update: BookingStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER]))
):
    """Bir rezervasyonun durumunu günceller. Sadece işletme sahibi yapabilir."""
    db_booking = crud_bookings.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking or db_booking.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rezervasyon bulunamadı veya bu işlem için yetkiniz yok.")
    return crud_bookings.update_booking_status(db, booking=db_booking, status_update=status_update)

@router.put("/{booking_id}/cancel", response_model=BookingOut)
async def cancel_booking(
    booking_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Bir rezervasyonu iptal eder. Rezervasyonu yapan müşteri veya işletme sahibi yapabilir."""
    db_booking = crud_bookings.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon bulunamadı.")

    is_customer = db_booking.customer_id == current_user.user_id
    is_owner = db_booking.owner_id == current_user.user_id

    if not (is_customer or is_owner):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rezervasyonu iptal etme yetkiniz yok.")
    
    if db_booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu rezervasyon zaten iptal edilmiş.")

    status_update = BookingStatusUpdate(status=BookingStatus.CANCELLED)
    return crud_bookings.update_booking_status(db=db, booking=db_booking, status_update=status_update)

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER]))
):
    """Bir rezervasyonu siler. Sadece işletme sahibi yapabilir."""
    db_booking = crud_bookings.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking or db_booking.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rezervasyon bulunamadı veya bu işlem için yetkiniz yok.")
    
    crud_bookings.delete_booking(db, booking_id=booking_id)
    return