# backend/routers/resource.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Annotated # Annotated import edildi

from database import get_db
from models.resource import Resource # Resource modeli
from models.user import User, UserRole # User ve UserRole modelleri
from schemas.resource import ResourceCreate, ResourceUpdate, ResourceOut
from crud import resource as crud_resource

from core.security import get_current_user, check_user_role # <-- Bu importları ekleyin/kontrol edin

router = APIRouter(
    prefix="/resources",
    tags=["resources"]
)

#  Yeni kaynak oluştur
@router.post("/", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
def create_resource(
    resource_in: ResourceCreate,
    db: Session = Depends(get_db),
    # Kimliği doğrulanmış, BUSINESS_OWNER rolüne sahip kullanıcıyı alıyoruz
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])) # <-- Burayı DEĞİŞTİRİN
):
    # current_user objesinden user_id'yi alıyoruz
    owner_id = current_user.user_id
    
    # crud fonksiyonunu çağırırken artık owner_id'yi current_user'dan alıyoruz
    return crud_resource.create_resource(db, resource_in, owner_id)

# Belirli bir kaynağı getir
@router.get("/{resource_id}", response_model=ResourceOut)
def read_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    # Sadece kaynağı görmek için herhangi bir doğrulanmış kullanıcı yeterli olabilir,
    # veya sadece sahibi veya admin görebilir gibi bir rol kontrolü de eklenebilir.
    current_user: User = Depends(get_current_user) # <-- Burayı DEĞİŞTİRİN
):
    db_resource = crud_resource.get_resource_by_id(db, resource_id)
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Kaynağı sadece sahibi veya (eğer varsa) admin görebilir
    if db_resource.owner_id != current_user.user_id and current_user.role != UserRole.BUSINESS_OWNER: # Business Owner kendi kaynaklarını görür
        # Ek olarak admin rolü varsa: and current_user.role != UserRole.ADMIN gibi
        raise HTTPException(status_code=403, detail="Not authorized to view this resource")

    return db_resource

# ✅ Sahip olunan tüm kaynakları listele
@router.get("/", response_model=List[ResourceOut])
def list_resources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # Sadece doğrulanmış kullanıcının kaynaklarını listelemek için
    current_user: User = Depends(get_current_user) # <-- Burayı DEĞİŞTİRİN
):
    # Kullanıcının rolüne göre filtreleme yapabiliriz
    if current_user.role == UserRole.BUSINESS_OWNER:
        # Business Owner sadece kendi kaynaklarını listeler
        return crud_resource.get_resources_by_owner(db, current_user.user_id, skip, limit)
    elif current_user.role == UserRole.CUSTOMER:
        # Müşteriler tüm kaynakları görebilir veya sadece kendileri için rezervasyon yapabilecekleri kaynakları görebilir.
        # Varsayılan olarak tüm aktif kaynakları döndürelim (örnek)
        return crud_resource.get_all_active_resources(db, skip, limit) # Yeni crud fonksiyonu gerekebilir
    else:
        # Diğer roller için yetkilendirme hatası veya özel liste
        raise HTTPException(status_code=403, detail="Not authorized to list resources for this role")


# ✅ Kaynak güncelle
@router.put("/{resource_id}", response_model=ResourceOut)
def update_resource(
    resource_id: UUID,
    resource_in: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])) # <-- Burayı DEĞİŞTİRİN
):
    db_resource = crud_resource.get_resource_by_id(db, resource_id)
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Sadece kaynak sahibi güncelleyebilir
    if db_resource.owner_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this resource")

    return crud_resource.update_resource(db, db_resource, resource_in)

# ✅ Kaynak sil
@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])) # <-- Burayı DEĞİŞTİRİN
):
    db_resource = crud_resource.get_resource_by_id(db, resource_id)
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Sadece kaynak sahibi silebilir
    if db_resource.owner_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this resource")

    crud_resource.delete_resource(db, resource_id)
    return