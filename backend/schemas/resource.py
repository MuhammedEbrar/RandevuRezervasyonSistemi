# backend/schemas/resource.py
from pydantic import BaseModel, Field # Field için
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from models import ResourceType
# Resource oluşturmak için girdi şeması
class ResourceCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100) # Kaynak adı
    description: Optional[str] = Field(None, max_length=500) # Açıklama
    type: ResourceType # Kaynak tipi (HIZMET veya MEKAN)
    capacity: Optional[int] = None # Eğer MEKAN ise kapasite
    location: Optional[dict] = None # JSON olarak konum bilgisi
    tags: Optional[List[str]] = None # Etiketler
    images: Optional[List[str]] = None # Resim URL'leri
    cancellation_policy: Optional[str] = None # İptal politikası

# Resource güncellemek için girdi şeması (tüm alanlar isteğe bağlı)
class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: Optional[ResourceType] = None
    capacity: Optional[int] = None
    location: Optional[dict] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    cancellation_policy: Optional[str] = None

# Resource çıktısı (API yanıtı) şeması
class ResourceOut(BaseModel):
    resource_id: UUID
    owner_id: UUID
    name: str
    description: Optional[str] = None
    type: ResourceType
    capacity: Optional[int] = None
    location: Optional[dict] = None
    is_active: bool
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    cancellation_policy: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # SQLAlchemy modellerinden Pydantic modeline dönüştürme için
