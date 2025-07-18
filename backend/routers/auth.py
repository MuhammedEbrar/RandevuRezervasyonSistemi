# backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Login için özel form data bağımlılığı
from sqlalchemy.orm import Session

# Kendi modüllerinizden importlar
from schemas.user import UserCreate, UserOut, UserLogin # Kullanıcı şemalarınız
from crud import user as crud_user # Stajyer 1'in yazdığı CRUD fonksiyonları
from core.security import get_password_hash, verify_password, create_access_token # Güvenlik fonksiyonları
from models import User, UserRole
from database import get_db # Veritabanı oturumu için bağımlılık

router = APIRouter(prefix="/auth", tags=["Auth"]) # /auth ile başlayan endpointler, Swagger'da "Auth" altında görünür

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate, # Gelen kullanıcı verileri
    db: Session = Depends(get_db) # Veritabanı oturumu
):
    # Email'in zaten kullanılıp kullanılmadığını kontrol eder
    db_user = crud_user.get_user_by_email(db, email=user_create.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email zaten kayıtlı."
        )

    # Şifreyi hash'ler
    hashed_password = get_password_hash(user_create.password)
    
    # Yeni UserCreate objesini oluştur, şifreyi hash'lenmiş haliyle güncelle
    # Pydantic modelini dict'e çevirip şifreyi değiştirebiliriz.
    user_data = user_create.model_dump() # Pydantic v2 için .model_dump(), v1 için .dict()
    user_data["hashed_password"] = hashed_password

    del user_data["password"] # Hassas şifreyi dict'ten kaldırın

    # Eğer UserCreate'de 'role' alanı yoksa ve varsayılan bir rol atamak istiyorsanız:
    if "role" not in user_data or user_data["role"] is None:
        user_data["role"] = UserRole.CUSTOMER # Varsayılan olarak CUSTOMER atayın

    # Kullanıcıyı veritabanına kaydeder (CRUD fonksiyonu kullanarak)
    ###created_user = crud_user.create_user(db, user=user_data) # user_data bir dict
    created_user = crud_user.create_user(db, user_in=user_create)

    return created_user

@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), # FastAPI'nin özel bağımlılığı
    db: Session = Depends(get_db)
):
    
    # Kullanıcıyı email ile veritabanından bulur
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yanlış email veya şifre."
        )

    # Şifreyi doğrulaması yapar
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yanlış email veya şifre."
        )

    # # Eğer kullanıcı pasifse giriş yapmasına izin verme (isteğe bağlı)
    # if not user.is_active: # User modelinizde is_active alanı olduğunu varsayar
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Kullanıcı hesabı pasif."
    #     )

    # 4. JWT Access Token oluştur
    access_token_data = {
        "sub": str(user.user_id), # user.id bir UUID ise str'ye çevirin
        "email": user.email,
        "role": user.role.value # UserRole Enum'unun string değerini alın
    }
    access_token = create_access_token(access_token_data)

    return {"access_token": access_token, "token_type": "bearer"}