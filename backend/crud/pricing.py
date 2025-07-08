# backend/crud/pricing.py
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date, time

from models.pricing import PricingRule # PricingRule modeli
from schemas.pricing import PricingRuleCreate, PricingRuleUpdate # Girdi şemaları

# Fiyatlandırma kuralını ID'ye göre getir
def get_pricing_rule_by_id(db: Session, price_rule_id: UUID) -> Optional[PricingRule]:
    return db.query(PricingRule).filter(PricingRule.price_rule_id == price_rule_id).first()

# Belirli bir işletme sahibine ait belirli bir kaynak için fiyatlandırma kurallarını listele
def get_pricing_rules_for_resource(
    db: Session,
    resource_id: UUID,
    owner_id: UUID, # Multi-tenancy ve güvenlik için
    skip: int = 0,
    limit: int = 100
) -> List[PricingRule]:
    return db.query(PricingRule).filter(
        PricingRule.resource_id == resource_id,
        PricingRule.owner_id == owner_id
    ).offset(skip).limit(limit).all()

# Yeni bir fiyatlandırma kuralı oluştur
def create_pricing_rule(
    db: Session,
    rule_in: PricingRuleCreate,
    owner_id: UUID
) -> PricingRule:
    # rule_in.model_dump() içindeki resource_id'yi de alarak doğrudan atama yapıyoruz
    db_rule = PricingRule(
        **rule_in.model_dump(),
        owner_id=owner_id
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

# Fiyatlandırma kuralını güncelle
def update_pricing_rule(
    db: Session,
    db_rule: PricingRule,
    rule_update: PricingRuleUpdate
) -> PricingRule:
    for key, value in rule_update.model_dump(exclude_unset=True).items():
        setattr(db_rule, key, value)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

# Fiyatlandırma kuralını sil
def delete_pricing_rule(db: Session, price_rule_id: UUID) -> Optional[UUID]:
    db_rule = db.query(PricingRule).filter(PricingRule.price_rule_id == price_rule_id).first()
    if db_rule:
        db.delete(db_rule)
        db.commit()
        return price_rule_id
    return None