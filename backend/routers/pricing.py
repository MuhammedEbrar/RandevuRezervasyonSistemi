# backend/routers/pricing.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional # Optional'ı ekledim
from uuid import UUID

from database import get_db # Veritabanı oturumu için
from schemas.pricing import PricingRuleCreate, PricingRuleUpdate, PricingRuleOut # Pydantic şemalarınız
from crud import pricing as crud_pricing # CRUD fonksiyonlarını kullanmak için

# Kullanıcı ve rol modellerini ve güvenlik fonksiyonlarını import edin
from models import User, UserRole, Resource
from core.security import get_current_user, check_user_role 
# from crud import resource as crud_resource # Kaynak kontrolü için eğer gerekecekse

# Yeni bir API router oluştur
router = APIRouter(
    # Fiyatlandırma kuralları genellikle belirli bir kaynağa (resource) aittir.
    # Bu yüzden prefix'i buna göre düzenledik.
    prefix="/resources/{resource_id}/pricing", 
    tags=["Pricing Rules"] # Swagger UI'da görünmesi için etiket
)

# --- Yeni Fiyatlandırma Kuralı Oluşturma ---
@router.post("/", response_model=PricingRuleOut, status_code=status.HTTP_201_CREATED)
def create_pricing_rule(
    resource_id: UUID, # URL'den gelen resource_id (Path Parametre)
    rule_in: PricingRuleCreate,
    db: Session = Depends(get_db),
    # Sadece BUSINESS_OWNER rolündeki kullanıcılar fiyatlandırma kuralı oluşturabilir
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])) 
):
    # Owner ID'yi giriş yapan kullanıcıdan alıyoruz.
    owner_id = current_user.user_id 
    
    # Opsiyonel: Oluşturulacak fiyatlandırma kuralının, sahibin kendi kaynağına ait olduğunu doğrula
    # Bu kontrol, Business Owner'ın başka bir Business Owner'ın kaynağına fiyat eklemesini engeller.
    # Eğer crud_resource'ı import ederseniz bu kısmı uncomment edebilirsiniz.
    # db_resource = crud_resource.get_resource_by_id(db, resource_id) 
    # if not db_resource or str(db_resource.owner_id) != str(owner_id):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu kaynağa fiyatlandırma kuralı ekleme yetkiniz yok.")

    # CRUD fonksiyonuna resource_id ve owner_id'yi gönderiyoruz
    new_rule = crud_pricing.create_pricing_rule(
        db, 
        rule_in=rule_in, 
        owner_id=owner_id, 
        resource_id=resource_id # CRUD fonksiyonunuzun bunu kabul ettiğinden emin olun
    )
    return new_rule

# --- Belirli Bir Fiyatlandırma Kuralını ID'ye Göre Getirme ---
# resource_id'yi de URL'den alıyoruz, çünkü bu kural belirli bir kaynağa aittir.
@router.get("/{price_rule_id}", response_model=PricingRuleOut)
def read_pricing_rule(
    resource_id: UUID, # URL'den gelen resource_id
    price_rule_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Herhangi bir doğrulanmış kullanıcı
):
    db_rule = crud_pricing.get_pricing_rule_by_id(db, price_rule_id=price_rule_id)
    if not db_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fiyatlandırma kuralı bulunamadı.")
    
    # Kuralın ilgili kaynağa ait olduğunu kontrol et
    if str(db_rule.resource_id) != str(resource_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sağlanan resource_id ile fiyat kuralı eşleşmiyor.")

    # Sadece sahibi, veya belirli rollere sahip kullanıcılar görebilir
    # Müşteriler fiyatlandırmaları görebilir:
    if str(db_rule.owner_id) != str(current_user.user_id) and current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu fiyatlandırma kuralını görme yetkiniz yok.")
        
    return db_rule

# --- Bir Kaynağın Tüm Fiyatlandırma Kurallarını Listeleme ---
@router.get("/", response_model=List[PricingRuleOut])
def list_pricing_rules_for_resource(
    resource_id: UUID, # URL'den gelen resource_id
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), # Kimliği doğrulanmış kullanıcıyı al
    skip: int = 0,
    limit: int = 100
):
    # Opsiyonel: current_user'ın bu kaynağın sahibi olduğunu kontrol edebilirsiniz
    # veya müşterilerin tüm fiyatlandırmaları görmesine izin veriyorsanız bu kontrolü atlayın.
    # Bu kısım, iş mantığınıza göre değişir. Eğer herkesin tüm fiyatlandırmaları görmesini istiyorsanız,
    # CRUD fonksiyonunuzdaki owner_id filtresini opsiyonel yapmanız veya kaldırmanız gerekir.
    # Ancak, Business Owner'ların sadece kendi kaynaklarının fiyatlandırmasını görmesi yaygın bir senaryodur.

    rules = crud_pricing.get_pricing_rules_for_resource(
        db,
        resource_id=resource_id,
        owner_id=current_user.user_id, # <-- owner_id'yi BURADAN gönderiyoruz!
        skip=skip,
        limit=limit
    )
    return rules

# --- Fiyatlandırma Kuralı Güncelleme ---
@router.put("/{price_rule_id}", response_model=PricingRuleOut)
def update_pricing_rule(
    resource_id: UUID, # URL'den gelen resource_id
    price_rule_id: UUID,
    rule_update: PricingRuleUpdate,
    db: Session = Depends(get_db),
    # Sadece BUSINESS_OWNER rolündeki kullanıcılar kural güncelleyebilir
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])) 
):
    db_rule = crud_pricing.get_pricing_rule_by_id(db, price_rule_id=price_rule_id)
    if not db_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fiyatlandırma kuralı bulunamadı.")

    # Kuralın ilgili kaynağa ait olduğunu kontrol et
    if str(db_rule.resource_id) != str(resource_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sağlanan resource_id ile fiyat kuralı eşleşmiyor.")

    # Sadece kuralın sahibi güncelleyebilir
    if str(db_rule.owner_id) != str(current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu fiyatlandırma kuralını güncelleme yetkiniz yok.")

    updated_rule = crud_pricing.update_pricing_rule(db, db_rule=db_rule, rule_update=rule_update)
    return updated_rule

# --- Fiyatlandırma Kuralı Silme ---
@router.delete("/{price_rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pricing_rule(
    resource_id: UUID, # URL'den gelen resource_id
    price_rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])) 
):
    db_rule = crud_pricing.get_pricing_rule_by_id(db, price_rule_id=price_rule_id)
    if not db_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fiyatlandırma kuralı bulunamadı.")

    if db_rule.resource_id != resource_id: # UUID karşılaştırmasını doğrudan yapın
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sağlanan resource_id ile fiyat kuralı eşleşmiyor.")

    if db_rule.owner_id != current_user.user_id: # UUID karşılaştırmasını doğrudan yapın
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu fiyatlandırma kuralını silme yetkiniz yok.")

    crud_pricing.delete_pricing_rule(db, price_rule_id=price_rule_id)
    return