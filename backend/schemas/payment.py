# backend/schemas/payment.py

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

from models.booking import PaymentStatus # PaymentStatus enum'ını import ediyoruz

# Ödeme isteği için şema (Mock Kredi Kartı Detayları dahil)
class PaymentInitiateRequest(BaseModel):
    booking_id: UUID
    amount: Decimal # Ödenecek miktar
    currency: str = "TRY" # Varsayılan para birimi
    # Mock için basit kart detayları. Gerçekte bu bilgiler güvenli bir şekilde işlenir.
    card_number: str # Mock: "4111222233334444" gibi
    expiry_month: str # Mock: "12"
    expiry_year: str # Mock: "25"
    cvv: str # Mock: "123"

# Ödeme yanıtı için şema
class PaymentInitiateResponse(BaseModel):
    payment_id: UUID
    booking_id: UUID
    amount: Decimal
    currency: str
    status: PaymentStatus # "PAID" veya "FAILED" gibi
    transaction_id: str # Ödeme sağlayıcısından gelen işlem ID'si
    message: str # Ödeme sonucu mesajı

# Webhook'lar için genel bir şema (mock için basit)
# Gerçek webhook'lar çok daha karmaşık olabilir ve imza doğrulaması gerektirir.
class WebhookEvent(BaseModel):
    event_type: str # "payment_succeeded", "payment_failed" vb.
    transaction_id: str
    booking_id: UUID
    status: PaymentStatus # İşlemin sonucu
    # Diğer webhook verileri...