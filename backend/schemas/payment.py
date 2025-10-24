# backend/schemas/payment.py

from pydantic import BaseModel, field_validator, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

from models.booking import PaymentStatus # PaymentStatus enum'ını import ediyoruz

def luhn_checksum(card_number: str) -> bool:
    """Luhn algoritması ile kart numarası doğrulaması"""
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

# Ödeme isteği için şema (Mock Kredi Kartı Detayları dahil)
class PaymentInitiateRequest(BaseModel):
    booking_id: UUID
    amount: Decimal = Field(gt=0, description="Ödenecek miktar 0'dan büyük olmalıdır")
    currency: str = "TRY" # Varsayılan para birimi
    # Mock için basit kart detayları. Gerçekte bu bilgiler güvenli bir şekilde işlenir.
    card_number: str # Mock: "4111222233334444" gibi
    expiry_month: str # Mock: "12"
    expiry_year: str # Mock: "25"
    cvv: str # Mock: "123"

    @field_validator('card_number')
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        """Kart numarası doğrulaması: 13-19 hane, sadece rakam, Luhn algoritması"""
        # Boşlukları ve tireleri temizle
        v = v.replace(' ', '').replace('-', '')

        if not v.isdigit():
            raise ValueError('Kart numarası sadece rakamlardan oluşmalıdır')

        if len(v) < 13 or len(v) > 19:
            raise ValueError('Kart numarası 13-19 haneli olmalıdır')

        if not luhn_checksum(v):
            raise ValueError('Geçersiz kart numarası (Luhn kontrolü başarısız)')

        return v

    @field_validator('expiry_month')
    @classmethod
    def validate_expiry_month(cls, v: str) -> str:
        """Son kullanma ayı doğrulaması: 01-12 arası"""
        if not v.isdigit():
            raise ValueError('Son kullanma ayı sadece rakamlardan oluşmalıdır')

        month = int(v)
        if month < 1 or month > 12:
            raise ValueError('Son kullanma ayı 01-12 arasında olmalıdır')

        return v.zfill(2)  # "5" -> "05" gibi

    @field_validator('expiry_year')
    @classmethod
    def validate_expiry_year(cls, v: str) -> str:
        """Son kullanma yılı doğrulaması: Gelecek bir yıl olmalı"""
        if not v.isdigit():
            raise ValueError('Son kullanma yılı sadece rakamlardan oluşmalıdır')

        # 2 haneli yıl formatını kabul et (25 -> 2025)
        if len(v) == 2:
            current_year = datetime.now().year
            century = (current_year // 100) * 100
            year = century + int(v)
        elif len(v) == 4:
            year = int(v)
        else:
            raise ValueError('Son kullanma yılı 2 veya 4 haneli olmalıdır')

        current_year = datetime.now().year
        if year < current_year:
            raise ValueError('Kartınızın son kullanma tarihi geçmiş')

        return v

    @field_validator('cvv')
    @classmethod
    def validate_cvv(cls, v: str) -> str:
        """CVV doğrulaması: 3-4 haneli, sadece rakam"""
        if not v.isdigit():
            raise ValueError('CVV sadece rakamlardan oluşmalıdır')

        if len(v) < 3 or len(v) > 4:
            raise ValueError('CVV 3 veya 4 haneli olmalıdır')

        return v

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