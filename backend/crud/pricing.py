# backend/crud/pricing.py
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date, time, datetime
from sqlalchemy import or_ # or_ import edildi
from models.pricing import PricingRule, DurationType, ApplicableDay # Güncel modeller import edildi
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
    owner_id: UUID,
    resource_id: UUID # <-- Router'dan gelen resource_id'yi burada kabul ediyoruz
) -> PricingRule:
    # rule_in.model_dump() içindeki verilerle birlikte owner_id ve resource_id'yi atıyoruz
    rule_data = rule_in.model_dump()
    db_rule = PricingRule(
        **rule_data,
        owner_id=owner_id,
        resource_id=resource_id # <-- resource_id'yi burada kullanıyoruz
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

# Fiyatlandırma kuralını güncelle 
def update_pricing_rule(
    db: Session,
    db_rule: PricingRule, # Mevcut veritabanı objesi
    rule_update: PricingRuleUpdate # Güncelleme verileri (Pydantic şeması)
) -> PricingRule: # Return tipi olarak PricingRule modelini belirtin

    update_data = rule_update.model_dump(exclude_unset=True) # Sadece set edilmiş alanları al
    
    for key, value in update_data.items():
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

# Belirli bir kaynak ve zaman aralığı için uygun fiyatlandırma kuralını bul
def get_applicable_pricing_rule(
    db: Session,
    resource_id: UUID,
    booking_start_time: datetime, # Booking'in başlangıç zamanı (datetime)
    booking_end_time: datetime,   # Booking'in bitiş zamanı (datetime)
    owner_id: Optional[UUID] = None # Opsiyonel: Eğer owner_id'ye göre de filtreleyecekseniz
) -> Optional[PricingRule]:
    """
    Belirli bir kaynak ve rezervasyon zamanı için geçerli fiyatlandırma kuralını bulur.
    Bu kısım, fiyatlandırma mantığınıza göre karmaşıklaşabilir.
    """
    query = db.query(PricingRule).filter(
        PricingRule.resource_id == resource_id
    )

    if owner_id:
        query = query.filter(PricingRule.owner_id == owner_id)
    
    # Kuralın aktif olup olmadığını kontrol et
    query = query.filter(PricingRule.is_active == True)

    # 1. Gün filtresi (ApplicableDay)
    booking_day_of_week = booking_start_time.strftime('%A').upper() 

    # PricingRule.applicable_days array'i içinde ya rezervasyon gününü (booking_day_of_week) içeriyor olmalı
    # ya da 'ALL' değerini içeriyor olmalı.
    query = query.filter(
        or_(
            PricingRule.applicable_days.any(booking_day_of_week), 
            PricingRule.applicable_days.any(ApplicableDay.ALL.value) 
        )
    )

    # 2. Saat filtresi (start_time_of_day, end_time_of_day)
    booking_start_time_only = booking_start_time.time()
    booking_end_time_only = booking_end_time.time()

    query = query.filter(
        or_(
            PricingRule.start_time_of_day.is_(None), 
            PricingRule.start_time_of_day <= booking_start_time_only 
        ),
        or_(
            PricingRule.end_time_of_day.is_(None), 
            PricingRule.end_time_of_day >= booking_end_time_only 
        )
    )

    # 3. Süre filtresi (min_duration, max_duration ve duration_type)
    # Bu kısmı kendi iş mantığınıza göre dikkatlice uygulayın.
    # Burada sadece bir genel çerçeve veriyorum, çünkü detaylar PricingRule'unuzun DurationType'ına bağlı.
    
    # Örnek: Eğer kural "PER_HOUR" ise ve min_duration/max_duration saat cinsinden ise:
    # duration_hours = (booking_end_time - booking_start_time).total_seconds() / 3600
    # query = query.filter(
    #     or_(PricingRule.min_duration.is_(None), PricingRule.min_duration <= duration_hours),
    #     or_(PricingRule.max_duration.is_(None), PricingRule.max_duration >= duration_hours)
    # )


    # Önemli: Eğer birden fazla uygun kural varsa, hangisinin en doğru kural olduğunu belirlemek için
    # ek bir sıralama veya seçim mantığına ihtiyacınız olabilir (örn: en spesifik kuralı seç, vb.)

    return query.first() # İlk uygun kuralı döndür