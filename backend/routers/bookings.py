# backend/routers/bookings.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date, time
from uuid import UUID
from typing import List, Optional

# Kök paketten mutlak importlar
from database import get_db
from schemas.booking import (
    BookingCreate,
    BookingOut, # Veya BookingResponse olarak adlandırdıysanız
    BookingCalculatePriceRequest,
    BookingCalculatePriceResponse,
    RecurringBookingCreate,
    RecurringBookingResponse,
    BookingUpdate,
    BookingStatusUpdate,
    BookingPaymentStatusUpdate
)
# >>>>>>>>>>>>>>>>>>>>>>>>>>> YENİ İMPORTLAR / DÜZELTMELER <<<<<<<<<<<<<<<<<<<<<<<<<
from crud import booking as crud_bookings
from crud import pricing as crud_pricing
from crud import resource as crud_resource # resource crud'u import ettik
from crud import availability as crud_availability # availability crud'u import ettik
from models.user import User, UserRole
from core.security import get_current_user, check_user_role
from models.booking import BookingStatus, PaymentStatus # BookingStatus ve PaymentStatus'ı import ediyoruz
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

# --- Fiyat Hesaplama Endpoint'i ---
@router.post("/calculate_price", response_model=BookingCalculatePriceResponse, status_code=status.HTTP_200_OK)
async def calculate_price(
    data: BookingCalculatePriceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.end_time <= data.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bitiş zamanı başlangıç zamanından sonra olmalıdır.")

    # 1. Kaynağın varlığını kontrol et ve sahibinin ID'sini al
    db_resource = crud_resource.get_resource_by_id(db, data.resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı. Fiyatlandırma yapılamıyor.")
    owner_id_of_resource = db_resource.owner_id # Kaynağın sahibinin ID'si

    # 2. Fiyatlandırma kuralını kaynağın sahibinin ID'si ile bul
    pricing_rule = crud_pricing.get_applicable_pricing_rule(
        db,
        resource_id=data.resource_id,
        booking_start_time=data.start_time,
        booking_end_time=data.end_time,
        owner_id=owner_id_of_resource # <-- BURAYI DEĞİŞTİRDİK! Kaynağın sahibini gönderiyoruz
    )

    if not pricing_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Belirtilen kaynak ve zaman için uygun fiyatlandırma kuralı bulunamadı.")

    duration_hours = (data.end_time - data.start_time).total_seconds() / 3600
    total_price = duration_hours * float(pricing_rule.base_price)

    return BookingCalculatePriceResponse(total_price=round(total_price, 2))

# ----------------------------------------------------------------------------------------------------

# --- YENİ EKLENEN ENDPOINT: Tekil Rezervasyon Oluşturma (POST /bookings/) ---
@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED) # Veya BookingResponse
async def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Rezervasyonu oluşturan müşteri
):
    # Customer ID'yi giriş yapan kullanıcıdan alıyoruz
    customer_id = current_user.user_id

    # 1. Kaynağın varlığını ve sahibini kontrol et (Görevin 2. maddesi)
    db_resource = crud_resource.get_resource_by_id(db, booking_in.resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon yapılmak istenen kaynak bulunamadı.")
    owner_id_of_resource = db_resource.owner_id # Kaynağın sahibini aldık

    # 2. Müsaitlik Kontrolü (Görevin 2.1. maddesi)
    is_available = crud_availability.check_availability(
        db, 
        booking_in.resource_id, 
        booking_in.start_time, 
        booking_in.end_time
    )
    if not is_available:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Seçilen zaman aralığı müsait değil veya çakışıyor. Lütfen başka bir zaman seçin.")

    # 3. Fiyat Hesaplaması (Görevin 2.2. maddesi - CRUD içinde de yapılıyor, bu yüzden burada çağırmıyoruz)
    # create_booking CRUD fonksiyonunuz zaten fiyatı hesaplayıp atayacak.

    # 4. Rezervasyonu PENDING statüsünde kaydetme (Görevin 2.3. maddesi)
    created_booking = crud_bookings.create_booking(
        db, 
        booking_in=booking_in, 
        customer_id=customer_id,
        owner_id=owner_id_of_resource # Kaynağın sahibini gönderiyoruz
    )
    return created_booking

# ----------------------------------------------------------------------------------------------------

# --- YENİ EKLENEN ENDPOINT: Tekrarlayan Rezervasyon Oluşturma ---
@router.post("/recurring", response_model=RecurringBookingResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_bookings(
    data: RecurringBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.end_date < data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bitiş tarihi başlangıç tarihinden önce olamaz."
        )
    
    if data.end_time_of_day <= data.start_time_of_day:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bitiş saati başlangıç saatinden sonra olmalıdır."
        )

    day_name_map = {
        "MONDAY": 0, "TUESDAY": 1, "WEDNESDAY": 2, "THURSDAY": 3,
        "FRIDAY": 4, "SATURDAY": 5, "SUNDAY": 6
    }
    
    requested_day_index = day_name_map.get(data.day_of_week.upper())
    if requested_day_index is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz 'day_of_week' değeri. 'MONDAY', 'TUESDAY' vb. kullanın."
        )

    # Kaynağın sahibini bul
    db_resource = crud_resource.get_resource_by_id(db, data.resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tekrarlayan rezervasyon yapılmak istenen kaynak bulunamadı.")
    owner_id_of_resource = db_resource.owner_id

    current_date = data.start_date
    created_bookings_count = 0
    total_price_for_all_bookings = 0.0
    booking_ids = []

    while current_date <= data.end_date:
        if current_date.weekday() == requested_day_index:
            booking_start_datetime = datetime.combine(current_date, data.start_time_of_day)
            booking_end_datetime = datetime.combine(current_date, data.end_time_of_day)

            # Müsaitlik kontrolü
            is_available = crud_availability.check_availability(
                db, 
                data.resource_id, 
                booking_start_datetime, 
                booking_end_datetime
            )
            if not is_available:
                print(f"Uyarı: {current_date} tarihinde müsaitlik bulunamadı veya çakışma var. Rezervasyon atlandı.")
                current_date += timedelta(days=1)
                continue # Bir sonraki güne geç

            # Fiyatlandırma kuralını bul
            pricing_rule = crud_pricing.get_applicable_pricing_rule(
                db, 
                resource_id=data.resource_id, 
                booking_start_time=booking_start_datetime, 
                booking_end_time=booking_end_datetime,
                owner_id=owner_id_of_resource # Kaynağın sahibini gönderiyoruz
            )

            if not pricing_rule:
                print(f"Uyarı: {current_date} tarihi için uygun fiyatlandırma kuralı bulunamadı. Rezervasyon atlandı.")
                current_date += timedelta(days=1)
                continue

            duration_hours = (booking_end_datetime - booking_start_datetime).total_seconds() / 3600
            calculated_price = duration_hours * float(pricing_rule.base_price)

            booking_create_data = BookingCreate(
                resource_id=data.resource_id,
                start_time=booking_start_datetime,
                end_time=booking_end_datetime,
                # total_price'ı BookingCreate içinde doğrudan beklememeliyiz, CRUD hesaplayacak.
                # notes: Optional[str] = None # Eğer recurring_booking_create şemasında notlar varsa
            )
            
            try:
                created_booking = crud_bookings.create_booking(
                    db, 
                    booking_in=booking_create_data, 
                    customer_id=current_user.user_id, # Müşteri ID'si
                    owner_id=owner_id_of_resource # Kaynağın sahibinin ID'si
                )
                created_bookings_count += 1
                total_price_for_all_bookings += calculated_price
                booking_ids.append(created_booking.booking_id)
            except Exception as e: # HTTPExceptions dışındaki hatalar için genel yakalama
                print(f"Uyarı: {current_date} tarihinde rezervasyon oluşturulurken beklenmedik hata oluştu: {e}. Atlandı.")

        current_date += timedelta(days=1)

    if created_bookings_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Belirtilen kriterlere göre hiçbir tekrarlayan rezervasyon oluşturulamadı. Lütfen kaynak, tarih aralığı veya fiyatlandırma kuralını kontrol edin."
        )

    return RecurringBookingResponse(
        message=f"{created_bookings_count} adet tekrarlayan rezervasyon başarıyla oluşturuldu.",
        created_bookings_count=created_bookings_count,
        total_price_for_all_bookings=round(total_price_for_all_bookings, 2),
        booking_ids=booking_ids
    )

# ----------------------------------------------------------------------------------------------------

# --- YENİ EKLENEN ENDPOINT: Müşterinin Kendi Rezervasyonlarını Listeleme ---
@router.get("/my", response_model=List[BookingOut]) # Veya BookingResponse
async def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    bookings = crud_bookings.get_bookings_by_customer(db, current_user.user_id, skip=skip, limit=limit)
    return bookings

# ----------------------------------------------------------------------------------------------------

# --- YENİ EKLENEN ENDPOINT: İşletme Sahibine Ait Kaynaklara Yapılan Rezervasyonları Listeleme ---
@router.get("/owned", response_model=List[BookingOut]) # Veya BookingResponse
async def get_owned_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])), # Sadece işletme sahipleri görebilir
    skip: int = 0,
    limit: int = 100
):
    bookings = crud_bookings.get_bookings_by_owner(db, current_user.user_id, skip=skip, limit=limit)
    return bookings

# ----------------------------------------------------------------------------------------------------

# --- YENİ EKLENEN ENDPOINT: Belirli Bir Rezervasyonu ID'ye Göre Getirme ---
@router.get("/{booking_id}", response_model=BookingOut) # Veya BookingResponse
async def read_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_booking = crud_bookings.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon bulunamadı.")
    
    is_customer = str(db_booking.customer_id) == str(current_user.user_id)
    is_owner_of_resource = str(db_booking.owner_id) == str(current_user.user_id)

    if not (is_customer or is_owner_of_resource): # ADMIN rolü varsa or is_admin de eklenebilir
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rezervasyonu görme yetkiniz yok.")

    return db_booking

# ----------------------------------------------------------------------------------------------------

# --- YENİ EKLENEN ENDPOINT: Rezervasyon Güncelleme (Zaman, Notlar vb.) ---
@router.put("/{booking_id}", response_model=BookingOut) # Veya BookingResponse
async def update_booking(
    booking_id: UUID,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_booking = crud_bookings.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon bulunamadı.")
    
    is_customer = str(db_booking.customer_id) == str(current_user.user_id)
    is_owner_of_resource = str(db_booking.owner_id) == str(current_user.user_id) 

    if not (is_customer or is_owner_of_resource): # ADMIN rolü varsa or is_admin de eklenebilir
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rezervasyonu güncelleme yetkiniz yok.")
    
    if booking_update.start_time or booking_update.end_time:
        new_start_time = booking_update.start_time if booking_update.start_time else db_booking.start_time
        new_end_time = booking_update.end_time if booking_update.end_time else db_booking.end_time

        if new_end_time <= new_start_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Güncellenmiş bitiş zamanı başlangıç zamanından sonra olmalıdır.")

        # Müsaitlik kontrolü
        is_available = crud_availability.check_availability(
            db, 
            db_booking.resource_id, 
            new_start_time, 
            new_end_time, 
            exclude_booking_id=booking_id # Kendini kontrol dışı bırak
        )
        if not is_available:
           raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Güncellenmiş zaman aralığı müsait değil veya çakışıyor.")

        # Fiyatı yeniden hesapla
        pricing_rule = crud_pricing.get_applicable_pricing_rule(
            db, 
            resource_id=db_booking.resource_id, 
            booking_start_time=new_start_time, 
            booking_end_time=new_end_time,
            owner_id=db_booking.owner_id # Rezervasyonun sahibi üzerinden kuralı bul
        )

        if not pricing_rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Güncellenmiş zaman aralığı için uygun fiyatlandırma kuralı bulunamadı.")
        
        duration_hours = (new_end_time - new_start_time).total_seconds() / 3600
        recalculated_price = duration_hours * float(pricing_rule.base_price)
        
        # BookingUpdate şemasında total_price alanı yoksa, CRUD fonksiyonu içinde manuel set etmek daha iyi olabilir.
        # db_booking.total_price = recalculated_price
        # crud_bookings.update_booking'i çağırın.
        # Şu anki BookingUpdate'ınızda total_price olmadığı için, bu satırı comment'te bırakın veya BookingUpdate'a ekleyin.
        # booking_update.total_price = recalculated_price 


    updated_booking = crud_bookings.update_booking(db, db_booking=db_booking, booking_update=booking_update)
    
    return updated_booking

# ----------------------------------------------------------------------------------------------------

# --- YENİ EKLENEN ENDPOINT: Rezervasyon Durumunu Güncelleme ---
@router.put("/{booking_id}/status", response_model=BookingOut) # Veya BookingResponse
async def update_booking_status(
    booking_id: UUID,
    status_update: BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])) # Sadece işletme sahibi değiştirebilir
):
    db_booking = crud_bookings.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon bulunamadı.")
    
    if str(db_booking.owner_id) != str(current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rezervasyonun durumunu güncelleme yetkiniz yok.")
    
    updated_booking = crud_bookings.update_booking_status(db, booking=db_booking, status_update=status_update)
    return updated_booking

# ----------------------------------------------------------------------------------------------------

# --- YENİ EKLENEN ENDPOINT: Rezervasyon Ödeme Durumunu Güncelleme ---
@router.put("/{booking_id}/payment_status", response_model=BookingOut) # Veya BookingResponse
async def update_booking_payment_status(
    booking_id: UUID,
    payment_status_update: BookingPaymentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])) # Örn: Sadece işletme sahibi değiştirebilir
):
    db_booking = crud_bookings.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon bulunamadı.")
    
    if str(db_booking.owner_id) != str(current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rezervasyonun ödeme durumunu güncelleme yetkiniz yok.")
    
    updated_booking = crud_bookings.update_booking_payment_status(db, booking=db_booking, payment_status_update=payment_status_update)
    return updated_booking

# ----------------------------------------------------------------------------------------------------

# --- YENİ EKLENEN ENDPOINT: Rezervasyon İptal Etme ---
@router.put("/{booking_id}/cancel", response_model=BookingOut) # Veya BookingResponse
async def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Rezervasyon sahibi veya ilgili işletme sahibi iptal edebilir
):
    db_booking = crud_bookings.get_booking_by_id(db, booking_id=booking_id)
    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon bulunamadı.")

    is_customer = str(db_booking.customer_id) == str(current_user.user_id)
    is_owner_of_resource = str(db_booking.owner_id) == str(current_user.user_id) 

    if not (is_customer or is_owner_of_resource):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rezervasyonu iptal etme yetkiniz yok.")
    
    if db_booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rezervasyon zaten iptal edilmiş durumda.")
    
    status_update_data = BookingStatusUpdate(status=BookingStatus.CANCELLED)
    cancelled_booking = crud_bookings.update_booking_status(db, booking=db_booking, status_update=status_update_data)
    
    return cancelled_booking