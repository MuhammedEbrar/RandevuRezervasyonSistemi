# schemas/resource.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# CREATE
class ResourceCreate(BaseModel):
    name: str = Field(..., example="Mavi Toplantı Odası")
    capacity: int = Field(..., ge=1, example=10)
    location: Optional[str] = Field(None, example="3. Kat, Oda 305")
    available: Optional[bool] = Field(default=True)

# UPDATE
class ResourceUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Güncellenmiş Oda Adı")
    capacity: Optional[int] = Field(None, ge=1, example=12)
    location: Optional[str] = Field(None, example="Yenilenen konum")
    available: Optional[bool] = Field(None)

# READ / OUTPUT
class ResourceOut(BaseModel):
    id: int
    name: str
    capacity: int
    location: Optional[str]
    available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # SQLAlchemy modelleri ile uyumlu hale getirir


#example olan kısımlar testten sonra silinecek