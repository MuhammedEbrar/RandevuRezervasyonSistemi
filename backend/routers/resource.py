# backend/routers/resource.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional # Optional, List import edildi

from database import get_db
from models import Resource, User, UserRole
from schemas.resource import ResourceCreate, ResourceUpdate, ResourceOut
from crud import resource as crud_resource

from core.security import get_current_user, check_user_role # Kimlik doğrulama ve rol kontrolü fonksiyonları

router = APIRouter(
    prefix="/resources",
    tags=["Resources"] # Swagger UI için etiket
)

# --- Kaynak Oluşturma ---
@router.post("/", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
def create_resource(
    resource_in: ResourceCreate,
    db: Session = Depends(get_db),
    # Sadece BUSINESS_OWNER rolündeki kullanıcılar kaynak oluşturabilir.
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER]))
):
    # Kaynağın sahibi, isteği yapan kullanıcının ID'si olacak.
    owner_id = current_user.user_id 
    
    new_resource = crud_resource.create_resource(db, resource_in=resource_in, owner_id=owner_id)
    return new_resource

# --- Kaynakları Listeleme ---
@router.get("/", response_model=List[ResourceOut])
def list_resources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Herhangi bir doğrulanmış kullanıcı
):
    # Kullanıcının rolüne göre kaynakları filtrele.
    if current_user.role == UserRole.BUSINESS_OWNER:
        # İşletme sahibi sadece kendi kaynaklarını listeler.
        resources = crud_resource.get_resources_by_owner(db, current_user.user_id, skip, limit)
    elif current_user.role == UserRole.CUSTOMER:
        # Müşteriler, aktif olan tüm kaynakları görebilir (veya rezervasyon yapabilecekleri kaynakları).
        # crud_resource.get_all_active_resources fonksiyonunun var olduğunu varsayalım.
        # Eğer yoksa, get_resources fonksiyonunu owner_id filtresi olmadan çağırın.
        resources = crud_resource.get_resources(db, skip=skip, limit=limit) 
    # ADMIN rolü gibi diğer roller için de buraya özel mantık eklenebilir.
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu rol için kaynakları listeleme yetkiniz yok.")
    
    return resources

# --- Belirli Bir Kaynağı Getirme ---
@router.get("/{resource_id}", response_model=ResourceOut)
def read_resource(
    resource_id: UUID,
    db: Session = Depends(get_db)
    # DÜZELTİLDİ: current_user bağımlılığı kaldırıldı, böylece halka açık oldu
):
    db_resource = crud_resource.get_resource_by_id(db, resource_id=resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı.")

    # DÜZELTİLDİ: Bu endpoint artık halka açık olduğu için,
    # sadece belirli rollerin erişimini kısıtlayan bir kontrol burada mantıksızdır.
    # Eğer kaynağın sadece sahibi görebilsin isterseniz, current_user bağımlılığını geri getirin.
    # Bu senaryoda amacımız halka açık olması.

    return db_resource

# --- Kaynak Güncelleme ---
@router.put("/{resource_id}", response_model=ResourceOut)
def update_resource(
    resource_id: UUID,
    resource_update: ResourceUpdate,
    db: Session = Depends(get_db),
    # Sadece BUSINESS_OWNER rolündeki kullanıcılar kaynak güncelleyebilir.
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])) 
):
    db_resource = crud_resource.get_resource_by_id(db, resource_id=resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı.")

    # Kaynağı sadece sahibi güncelleyebilir.
    if db_resource.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu kaynağı güncelleme yetkiniz yok.")

    updated_resource = crud_resource.update_resource(db, db_resource=db_resource, resource_update=resource_update)
    return updated_resource

# --- Kaynak Silme ---
@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    # Sadece BUSINESS_OWNER rolündeki kullanıcılar kaynak silebilir.
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER]))
):
    db_resource = crud_resource.get_resource_by_id(db, resource_id=resource_id)
    if not db_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kaynak bulunamadı.")

    # Kaynağı sadece sahibi silebilir.
    if db_resource.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu kaynağı silme yetkiniz yok.")

    crud_resource.delete_resource(db, resource_id=resource_id)
    # 204 No Content yanıtında genellikle gövde olmaz.
    return

