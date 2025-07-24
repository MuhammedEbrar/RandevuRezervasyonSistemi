# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.settings import settings # config dosyasını import eder
# DÜZELTİLDİ: Gereksiz tekrar eden import satırı kaldırıldı
from routers import auth, users, resource, availability, pricing, bookings # Tüm router'lar tek satırda import edildi

app = FastAPI(
    title="Randevu ve Kiralama Platformu API",
    description="Modüler bir randevu ve kiralama sistemi için API dokümantasyonu.",
    version="0.1.0",
)

# Router'larıı eklendiği bölüm
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(resource.router)
app.include_router(availability.router)
app.include_router(pricing.router)
app.include_router(bookings.router)

# CORS ayarları
# Geliştirme aşamasında her yerden erişime izin veriyoruz.
# Canlıya alırken belirli domainlere kısıtlamalısın!
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173", # Vite'ın varsayılan portu
    "http://127.0.0.1:8000",
    "http://10.0.2.2:8000",
    "https://*.ngrok-free.app", # ngrok için bu yeterli
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Randevu ve Kiralama Platformu API'sine Hoş Geldiniz!"}

# Router'lar buraya eklenecek (ileriki adımlarda)
# from .routers import auth, users
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])