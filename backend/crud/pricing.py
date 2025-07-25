# backend/crud/pricing.py

from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date, time, datetime
from sqlalchemy import or_
import math
from decimal import Decimal, ROUND_UP

from models import PricingRule, DurationType, ApplicableDay
from schemas.pricing import PricingRuleCreate, PricingRuleUpdate

def get_pricing_rule_by_id(db: Session, price_rule_id: UUID) -> Optional[PricingRule]:
    """ID'ye göre tek bir fiyatlandırma kuralını getirir."""
    return db.query(PricingRule).filter(PricingRule.price_rule_id == price_rule_id).first()

def get_pricing_rules_for_resource(
    db: Session, resource_id: UUID, owner_id: UUID, skip: int = 0, limit: int = 100
) -> List[PricingRule]:
    """Bir kaynağa ait tüm fiyatlandırma kurallarını listeler."""
    return db.query(PricingRule).filter(
        PricingRule.resource_id == resource_id,
        PricingRule.owner_id == owner_id
    ).offset(skip).limit(limit).all()

def create_pricing_rule(
    db: Session, rule_in: PricingRuleCreate, owner_id: UUID, resource_id: UUID
) -> PricingRule:
    """Yeni bir fiyatlandırma kuralı oluşturur."""
    rule_data = rule_in.model_dump()
    db_rule = PricingRule(
        **rule_data,
        owner_id=owner_id,
        resource_id=resource_id
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def update_pricing_rule(
    db: Session, db_rule: PricingRule, rule_update: PricingRuleUpdate
) -> PricingRule:
    """Mevcut bir fiyatlandırma kuralını günceller."""
    update_data = rule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_rule, key, value)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def delete_pricing_rule(db: Session, price_rule_id: UUID) -> Optional[UUID]:
    """Bir fiyatlandırma kuralını siler."""
    db_rule = db.query(PricingRule).filter(PricingRule.price_rule_id == price_rule_id).first()
    if db_rule:
        db.delete(db_rule)
        db.commit()
        return price_rule_id
    return None

def get_applicable_pricing_rule(
    db: Session, resource_id: UUID, booking_start_time: datetime, booking_end_time: datetime
) -> Optional[PricingRule]:
    """
    Belirli bir zaman aralığı için geçerli olan fiyatlandırma kuralını bulur.
    Eğer bir kuralda gün belirtilmemişse, tüm günler için geçerli sayılır.
    """
    booking_day_of_week = booking_start_time.strftime('%A').upper()
    booking_start_time_only = booking_start_time.time()

    query = db.query(PricingRule).filter(
        PricingRule.resource_id == resource_id,
        PricingRule.is_active == True,
        # Kural ya tüm günler için geçerli olmalı, ya belirtilen günü içermeli,
        # ya da hiç gün belirtilmemiş olmalı (bu da tüm günler anlamına gelir).
        or_(
            PricingRule.applicable_days == None,
            PricingRule.applicable_days.any(ApplicableDay.ALL.value),
            PricingRule.applicable_days.any(booking_day_of_week)
        ),
        # Başlangıç saati ya belirtilmemiş olmalı ya da rezervasyondan önce olmalı.
        or_(
            PricingRule.start_time_of_day.is_(None),
            PricingRule.start_time_of_day <= booking_start_time_only
        )
    )
    # İlk uygun kuralı döndür. Daha karmaşık senaryolar için burası geliştirilebilir.
    return query.first()
def calculate_price_from_rule(
    pricing_rule: PricingRule, start_time: datetime, end_time: datetime
) -> Decimal:
    """Verilen bir fiyatlandırma kuralına ve süreye göre toplam fiyatı hesaplar."""
    total_price = Decimal(0)
    duration = end_time - start_time

    if pricing_rule.duration_type == DurationType.FIXED_PRICE:
        total_price = pricing_rule.base_price
    
    elif pricing_rule.duration_type == DurationType.PER_DAY:
        days = Decimal(math.ceil(duration.total_seconds() / (24 * 3600)))
        if days == 0 and duration.total_seconds() > 0:
            days = 1
        total_price = days * pricing_rule.base_price

    elif pricing_rule.duration_type == DurationType.PER_HOUR:
        hours = Decimal(duration.total_seconds() / 3600)
        total_price = hours * pricing_rule.base_price

    return total_price.quantize(Decimal('0.01'), rounding=ROUND_UP)