# backend/crud/pricing.py
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date, time, datetime
from sqlalchemy import or_
from models.pricing import PricingRule # PricingRule modeli
from schemas.pricing import PricingRuleCreate, PricingRuleUpdate # Girdi şemaları
from models.pricing import PricingRule, DurationType, ApplicableDay # Güncel model import edildi

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

# Yeni bir fiyatlandırma kuralı oluştur (ESKİ HALİNDEKİ İLK CREATE FONKSİYONU)
# Bu fonksiyonun resource_id alması gerekiyordu, onu da ekledim.
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

# Fiyatlandırma kuralını güncelle (DAHA ÖNCE YANLIŞLIKLA create_pricing_rule olarak adlandırılan fonksiyon)
def update_pricing_rule( # <-- BURAYI DÜZELTTİK!
    db: Session,
    db_rule: PricingRule, # Mevcut veritabanı objesi
    rule_update: PricingRuleUpdate # Güncelleme verileri
) -> PricingRule: # Return tipi olarak PricingRule modelini belirtin

    # Pydantic model_dump() çağrısının verileri düzgün şekilde dictionaries'e dönüştürdüğünden emin olun
    update_data = rule_update.model_dump(exclude_unset=True) # Sadece set edilmiş alanları al

    # Her bir alanı döngü ile güncelle
    for key, value in update_data.items():
        setattr(db_rule, key, value)
    
    db.add(db_rule) # Mevcut objeyi session'a ekle (zaten ekliyse sorun olmaz)
    db.commit() # Değişiklikleri veritabanına kaydet
    db.refresh(db_rule) # Güncellenmiş verilerle objeyi yenile
    return db_rule

# Fiyatlandırma kuralını sil
def delete_pricing_rule(db: Session, price_rule_id: UUID) -> Optional[UUID]:
    db_rule = db.query(PricingRule).filter(PricingRule.price_rule_id == price_rule_id).first()
    if db_rule:
        db.delete(db_rule)
        db.commit()
        return price_rule_id
    return None

# Yeni eklenen fonksiyon (hatalı olabilir): Belirli bir kaynak ve zaman aralığı için uygun fiyatlandırma kuralını bul
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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # BURADAKİ FİLTRELEME MANTIĞI MODELİNİZE GÖRE DEĞİŞMELİ # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # 1. Gün filtresi (ApplicableDay)
    # Rezervasyonun başladığı günün haftanın hangi günü olduğunu bulalım
    booking_day_of_week = booking_start_time.strftime('%A').upper() # 'MONDAY', 'TUESDAY' gibi string verir

    # PricingRule.applicable_days array'i içinde ya rezervasyon gününü (booking_day_of_week) içeriyor olmalı
    # ya da 'ALL' değerini içeriyor olmalı.
    query = query.filter(
        or_(
            PricingRule.applicable_days.any(booking_day_of_week), # Belirtilen günlerden biri mi?
            PricingRule.applicable_days.any(ApplicableDay.ALL.value) # Ya da tüm günler için mi geçerli?
        )
    )

    # 2. Saat filtresi (start_time_of_day, end_time_of_day)
    # Rezervasyonun başlangıç ve bitiş saatlerini al
    booking_start_time_only = booking_start_time.time()
    booking_end_time_only = booking_end_time.time()

    # Kuralın zaman aralığı içindeyse veya kuralın zaman aralığı belirtilmemişse geçerli
    query = query.filter(
        or_(
            PricingRule.start_time_of_day.is_(None), # Kuralın başlangıç saati yoksa (tüm gün geçerli)
            PricingRule.start_time_of_day <= booking_start_time_only # Kuralın başlangıç saati, rezervasyon başlangıcından önce veya eşit
        ),
        or_(
            PricingRule.end_time_of_day.is_(None), # Kuralın bitiş saati yoksa (tüm gün geçerli)
            PricingRule.end_time_of_day >= booking_end_time_only # Kuralın bitiş saati, rezervasyon bitişinden sonra veya eşit
        )
    )

    # 3. Süre filtresi (min_duration, max_duration ve duration_type) - BU KISIM ÇOK KRİTİK VE İŞ MANTIĞINA BAĞLI
    # Bu kısmı, DurationType'a göre kendi iş mantığınıza göre dikkatlice uygulamalısınız.
    # Örneğin, "PER_HOUR" bir kural ise, rezervasyonun süresi min/max saatler arasında olmalı.
    # Bu örnekte sadece min/max duration'ı genel olarak kontrol ediyorum, ama siz bunu DurationType'a göre ayırmalısınız.

    # Rezervasyonun toplam süresini (dakika veya saat olarak) hesaplayın
    duration_minutes = (booking_end_time - booking_start_time).total_seconds() / 60
    duration_hours = duration_minutes / 60

    # Bu filtreleme çok genel, kendi iş mantığınıza göre uyarlayın.
    # Eğer kuralın min_duration'ı varsa ve rezervasyon süresi bundan azsa geçersiz sayılabilir.
    # Eğer kuralın max_duration'ı varsa ve rezervasyon süresi bundan fazlaysa geçersiz sayılabilir.
    # query = query.filter(
    #     or_(
    #         PricingRule.min_duration.is_(None),
    #         # min_duration'ın birimi DurationType'a göre değişir (saat, gün, adet)
    #         # Örn: PricingRule.min_duration <= duration_hours (eğer saat ise)
    #     ),
    #     or_(
    #         PricingRule.max_duration.is_(None),
    #         # Örn: PricingRule.max_duration >= duration_hours (eğer saat ise)
    #     )
    # )

    # Önemli: Eğer birden fazla uygun kural varsa, hangisinin en doğru kural olduğunu belirlemek için
    # ek bir sıralama veya seçim mantığına ihtiyacınız olabilir (örn: en spesifik kuralı seç, vb.)

    return query.first() # İlk uygun kuralı döndür