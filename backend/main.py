# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.settings import settings
from routers import auth, users, resource, availability, pricing, bookings, payments

app = FastAPI(
    title="Randevu ve Kiralama Platformu API",
    description="Modüler bir randevu ve kiralama sistemi için API dokümantasyonu.",
    version="1.0.0",
)

# --- CORS Ayarları ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Geliştirme için her yerden gelen isteğe izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER'LARI UYGULAMAYA EKLEME ---
# DÜZELTME: Her bir router'ı eklerken başına /api/v1 ön ekini ekliyoruz.
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(resource.router, prefix=API_PREFIX)
app.include_router(availability.router, prefix=API_PREFIX)
app.include_router(pricing.router, prefix=API_PREFIX)
app.include_router(bookings.router, prefix=API_PREFIX)
app.include_router(payments.router, prefix=API_PREFIX)


@app.get("/")
async def read_root():
    return {"message": "Randevu ve Kiralama Platformu API'sine Hoş Geldiniz!"}