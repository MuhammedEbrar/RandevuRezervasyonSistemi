# backend/crud/resource.py
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID # UUID tipi için
from sqlalchemy.exc import SQLAlchemyError

from models import Resource, ResourceType # Resource modeli ve Enum'ı
from schemas.resource import ResourceCreate, ResourceUpdate # Girdi şemaları

# Kaynakları ID'ye göre getir
def get_resource_by_id(db: Session, resource_id: UUID) -> Optional[Resource]:
    return db.query(Resource).filter(Resource.resource_id == resource_id).first()

# Tüm kaynakları listele (müşteriler için - aktif olanlar)
def get_resources(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Resource]:
    query = db.query(Resource)
    if active_only:
        query = query.filter(Resource.is_active == True)
    return query.offset(skip).limit(limit).all()

# Bir işletme sahibinin tüm kaynaklarını listele
def get_resources_by_owner(db: Session, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[Resource]:
    # Multi-tenancy için owner_id ile filtreleme çok kritik!
    return db.query(Resource).filter(Resource.owner_id == owner_id).offset(skip).limit(limit).all()

# Yeni bir kaynak oluştur
def create_resource(db: Session, resource_in: ResourceCreate, owner_id: UUID) -> Resource:
    try:
        db_resource = Resource(
            **resource_in.model_dump(),
            owner_id=owner_id
        )
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
        return db_resource
    except SQLAlchemyError as e:
        db.rollback()
        raise e  # burada FastAPI'de `HTTPException`'a çevrilebilir

# Kaynağı güncelle
def update_resource(db: Session, db_resource: Resource, resource_update: ResourceUpdate) -> Resource:
    # exclude_unset=True: Sadece gönderilen alanları günceller, gönderilmeyenleri olduğu gibi bırakır
    for key, value in resource_update.model_dump(exclude_unset=True).items():
        setattr(db_resource, key, value)
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

# Kaynağı sil (veya is_active durumunu değiştir)
def delete_resource(db: Session, resource_id: UUID) -> Optional[UUID]:
    db_resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if db_resource:
        db.delete(db_resource)
        db.commit()
        return resource_id
    return None