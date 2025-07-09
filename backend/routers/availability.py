# backend/routers/availability.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date, time

from database import get_db # Veritabanı oturumu için
from schemas.availability import AvailabilityScheduleCreate, AvailabilityScheduleOut # Pydantic şemalarınız
from crud import availability as crud_availability # CRUD fonksiyonlarını kullanmak için
from models.user import User, UserRole # User ve UserRole modellerini import edin
from core.security import get_current_user, check_user_role # Kimlik doğrulama ve rol kontrolü fonksiyonları

# Yeni bir API router oluştur
router = APIRouter(
    # resource_id'yi URL'den alacağımız için prefix'i buna göre düzenledik.
    # Bu, belirli bir kaynağın müsaitliğini yönettiğimiz anlamına gelir.
    prefix="/resources/{resource_id}/availability",
    tags=["Availability Schedules"] # Swagger UI'da görünmesi için etiket
)

# --- Yeni Müsaitlik Takvimi Oluşturma ---
@router.post("/", response_model=AvailabilityScheduleOut, status_code=status.HTTP_201_CREATED)
def create_availability_schedule(
    resource_id: UUID, # URL'den gelen resource_id
    schedule_in: AvailabilityScheduleCreate,
    db: Session = Depends(get_db),
    # Sadece BUSINESS_OWNER rolündeki kullanıcılar kaynak için müsaitlik oluşturabilir
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER])) 
):
    # Owner ID'yi giriş yapan kullanıcıdan alıyoruz
    owner_id = current_user.user_id 
    
    # Oluşturulacak müsaitlik programının, sahibin kendi kaynağına ait olduğunu doğrula
    # Bu kontrolü CRUD katmanında veya burada yapabilirsiniz.
    # Örnek: Kaynağın sahibini kontrol eden bir CRUD fonksiyonu çağırma
    # db_resource = crud_resource.get_resource_by_id(db, resource_id) # crud_resource'a ihtiyacınız olabilir
    # if not db_resource or str(db_resource.owner_id) != str(owner_id):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu kaynağa müsaitlik ekleme yetkiniz yok.")

    # CRUD fonksiyonuna hem owner_id'yi hem de resource_id'yi gönderiyoruz
    new_schedule = crud_availability.create_availability_schedule(
        db, 
        schedule_in=schedule_in, 
        owner_id=owner_id, 
        resource_id=resource_id
    )
    return new_schedule

# --- Belirli Bir Müsaitlik Takvimini ID'ye Göre Getirme ---
# Bu endpoint, genel bir schedule_id ile erişim sağlar, ancak yetkilendirme gerektirebilir.
@router.get("/{schedule_id}", response_model=AvailabilityScheduleOut)
def read_availability_schedule(
    resource_id: UUID, # Prefixten gelen resource_id
    schedule_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Herhangi bir doğrulanmış kullanıcı
):
    db_schedule = crud_availability.get_availability_schedule_by_id(db, schedule_id=schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Müsaitlik takvimi bulunamadı.")
    
    # Kaynağın ilgili olduğunu ve kullanıcının yetkili olduğunu kontrol et
    if str(db_schedule.resource_id) != str(resource_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sağlanan resource_id ile takvim eşleşmiyor.")

    # Yalnızca sahibi veya admin/müşteri (müşteri görebilir) rolündeki kullanıcılar görebilir
    if str(db_schedule.owner_id) != str(current_user.user_id) and current_user.role != UserRole.CUSTOMER:
        # Business Owner kendi kaynaklarını görür, Customer tüm kaynakları görür
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu müsaitlik takvimini görme yetkiniz yok.")
        
    return db_schedule

# --- Kaynağa Göre Müsaitlikleri Listeleme ---
# Bu endpoint artık router prefix'inde resource_id olduğu için "/resource/{resource_id}/" ihtiyacı duymuyor.
@router.get("/", response_model=List[AvailabilityScheduleOut])
def get_resource_availability_list(
    resource_id: UUID, # URL'den gelen resource_id
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), # Kimliği doğrulanmış kullanıcıyı al
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    schedules = crud_availability.get_availability_schedules_for_resource(
        db,
        resource_id=resource_id,
        owner_id=current_user.user_id, # <-- owner_id'yi BURADAN gönderiyoruz!
        start_date=start_date,
        end_date=end_date
    )
    return schedules

# --- Müsaitlik Takvimi Güncelleme ---
@router.put("/{schedule_id}", response_model=AvailabilityScheduleOut)
def update_availability_schedule(
    resource_id: UUID, # URL'den gelen resource_id
    schedule_id: UUID,
    schedule_update: AvailabilityScheduleCreate, # AvailabilityScheduleUpdate yerine Create kullanılması tutarsızlık
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER]))
):
    db_schedule = crud_availability.get_availability_schedule_by_id(db, schedule_id=schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Müsaitlik takvimi bulunamadı.")
    
    # Kaynağın ilgili olduğunu kontrol et
    if str(db_schedule.resource_id) != str(resource_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sağlanan resource_id ile takvim eşleşmiyor.")

    # Sadece müsaitlik takviminin sahibi güncelleyebilir
    if str(db_schedule.owner_id) != str(current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu müsaitlik takvimini güncelleme yetkiniz yok.")

    # schedule_update'in AvailabilityScheduleUpdate tipinde olması daha doğru olurdu
    updated_schedule = crud_availability.update_availability_schedule(
        db, db_schedule=db_schedule, schedule_update=schedule_update
    )
    return updated_schedule

# --- Müsaitlik Takvimi Silme ---
@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability_schedule(
    resource_id: UUID, # URL'den gelen resource_id
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_role([UserRole.BUSINESS_OWNER]))
):
    db_schedule = crud_availability.get_availability_schedule_by_id(db, schedule_id=schedule_id)
    if not db_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Müsaitlik takvimi bulunamadı.")
    
    # Kaynağın ilgili olduğunu kontrol et
    if str(db_schedule.resource_id) != str(resource_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_BACKEND, detail="Sağlanan resource_id ile takvim eşleşmiyor.")


    # Sadece müsaitlik takviminin sahibi silebilir
    if str(db_schedule.owner_id) != str(current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu müsaitlik takvimini silme yetkiniz yok.")

    crud_availability.delete_availability_schedule(db, schedule_id=schedule_id)
    return # 204 No Content yanıtı için gövdeye gerek yoktur