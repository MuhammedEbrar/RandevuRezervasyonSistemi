# backend/routers/payments.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import random # Mock işlem ID'si için
from decimal import Decimal # Decimal kullanmak için

from database import get_db
from models.user import User # User modelini import edin
from core.security import get_current_user # Kimlik doğrulama için
from crud import payments as crud_payments # Yeni payments CRUD'u import ettik
from crud import bookings as crud_bookings # Booking'i güncellemek için
from schemas.payment import PaymentInitiateRequest, PaymentInitiateResponse, WebhookEvent # Yeni şemaları import ettik
from models.booking import BookingStatus, PaymentStatus # Enum'ları import ettik
from schemas.payment import PaymentInitiateRequest, PaymentInitiateResponse, WebhookEvent
from schemas.booking import BookingStatusUpdate, BookingPaymentStatusUpdate # <-- Bu satırları ekleyin!
from models.booking import BookingStatus, PaymentStatus

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

# --- Ödeme Başlatma Endpoint'i ---
@router.post("/initiate", response_model=PaymentInitiateResponse, status_code=status.HTTP_200_OK)
async def initiate_payment(
    payment_request: PaymentInitiateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Rezervasyonun varlığını ve durumunu kontrol et
    # CONCURRENCY KORUMASI: with_for_update() ile rezervasyonu kilitle
    # Bu, aynı rezervasyon için eşzamanlı ödeme işlemlerini engeller
    from models.booking import Booking
    db_booking = db.query(Booking).filter(Booking.booking_id == payment_request.booking_id).with_for_update().first()

    if not db_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ödeme yapılmak istenen rezervasyon bulunamadı.")

    # Rezervasyonun ödeme için uygun olup olmadığını kontrol eden mantık
    if db_booking.payment_status == PaymentStatus.PAID:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu rezervasyon için ödeme zaten yapılmış.")
    if db_booking.status in [BookingStatus.CANCELLED, BookingStatus.REJECTED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="İptal edilmiş/reddedilmiş bir rezervasyon için ödeme yapılamaz.")

    # Ödenecek miktarın rezervasyonun toplam fiyatıyla eşleştiğini kontrol et
    if payment_request.amount != db_booking.total_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ödenecek miktar rezervasyonun toplam fiyatıyla eşleşmiyor. Beklenen: {db_booking.total_price}, Gönderilen: {payment_request.amount}.")

    # 2. Mock Ödeme İşlemi Simülasyonu
    transaction_id = f"mock_txn_{random.randint(100000, 999999)}"

    is_successful = True
    message = "Ödeme başarıyla tamamlandı."
    payment_status = PaymentStatus.PAID

    if payment_request.card_number.startswith("4") and payment_request.card_number.endswith("4444"):
        is_successful = False
        message = "Ödeme başarısız oldu: Reddedilen kart."
        payment_status = PaymentStatus.FAILED

    # ---------------------------------------------------------------------------------------------
    # 3. Ödeme Kaydını Oluştur veya Güncelle (ÇÖZÜM BURADA!)

    # Bu rezervasyon için zaten bir ödeme kaydı var mı diye kontrol et
    db_payment = crud_payments.get_payment_by_booking_id(db, payment_request.booking_id)

    if db_payment:
        # Eğer mevcut bir ödeme kaydı varsa, onu güncelle
        # NOT: Bu crud_payments.update_payment_status fonksiyonu transaction_id'yi de almalı
        updated_payment = crud_payments.update_payment_status(
            db,
            db_payment=db_payment,
            new_status=payment_status,
            transaction_id=transaction_id # Yeni işlem ID'sini de güncelle
        )
        created_payment = updated_payment # Yanıt için referansı ayarla
    else:
        # Eğer mevcut bir ödeme kaydı yoksa, yeni bir ödeme kaydı oluştur
        created_payment = crud_payments.create_payment(
            db,
            booking_id=payment_request.booking_id,
            customer_id=current_user.user_id,
            amount=payment_request.amount,
            currency=payment_request.currency,
            status=payment_status,
            transaction_id=transaction_id,
            payment_method_last_four=payment_request.card_number[-4:],
            is_successful=is_successful
        )
    # ---------------------------------------------------------------------------------------------

    # 4. Rezervasyonun Ödeme Durumunu ve Genel Durumunu Güncelle
    booking_payment_status_update_data = BookingPaymentStatusUpdate(payment_status=payment_status)
    crud_bookings.update_booking_payment_status(db, booking=db_booking, payment_status_update=booking_payment_status_update_data)

    if is_successful and db_booking.status == BookingStatus.PENDING:
        booking_status_update_data = BookingStatusUpdate(status=BookingStatus.CONFIRMED)
        crud_bookings.update_booking_status(db, booking=db_booking, status_update=booking_status_update_data)
    elif not is_successful and db_booking.status == BookingStatus.PENDING:
        # Ödeme başarısız olursa ve rezervasyon PENDING ise, durumu REJECTED yapabiliriz
        booking_status_update_data = BookingStatusUpdate(status=BookingStatus.REJECTED) 
        crud_bookings.update_booking_status(db, booking=db_booking, status_update=booking_status_update_data)


    return PaymentInitiateResponse(
        payment_id=created_payment.payment_id,
        booking_id=payment_request.booking_id,
        amount=payment_request.amount,
        currency=payment_request.currency,
        status=payment_status,
        transaction_id=transaction_id,
        message=message
    )

# --- Webhook Endpoint'i (Görev 5 için ön hazırlık) ---
# Gerçek ödeme sağlayıcılarından gelecek geri bildirimleri simüle eder.
@router.post("/webhook", status_code=status.HTTP_200_OK)
async def payment_webhook(
    event: WebhookEvent,
    db: Session = Depends(get_db)
):
    print(f"Webhook event alındı: {event.event_type} için işlem ID: {event.transaction_id}")

    db_booking = crud_bookings.get_booking_by_id(db, event.booking_id)
    if not db_booking:
        print(f"Uyarı: Webhook için rezervasyon bulunamadı: {event.booking_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezervasyon bulunamadı.")

    # Ödeme durumunu güncelle
    payment_status_update_data = BookingPaymentStatusUpdate(payment_status=event.status)
    # db_booking yerine booking argümanını kullanıyoruz
    crud_bookings.update_booking_payment_status(db, booking=db_booking, payment_status_update=payment_status_update_data)

    # Eğer ödeme başarılıysa, rezervasyon durumunu CONFIRMED yap
    if event.event_type == "payment_succeeded" and db_booking.status == BookingStatus.PENDING:
        status_update_data = BookingStatusUpdate(status=BookingStatus.CONFIRMED)
        # db_booking yerine booking argümanını kullanıyoruz
        crud_bookings.update_booking_status(db, booking=db_booking, status_update=status_update_data)
    elif event.event_type == "payment_failed" and db_booking.status == BookingStatus.PENDING:
        status_update_data = BookingStatusUpdate(status=BookingStatus.REJECTED)
        # db_booking yerine booking argümanını kullanıyoruz
        crud_bookings.update_booking_status(db, booking=db_booking, status_update=status_update_data)

    return {"message": "Webhook başarıyla işlendi."}