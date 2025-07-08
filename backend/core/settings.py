# backend/core/settings.py
# Bu dosya, uygulamanın ayarlarını (veritabanı URL'si, JWT anahtarı vb.) yönetir.

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv

# KRİTİK ADIM: load_dotenv() çağrısını, Settings sınıfı tanımlanmadan ve kullanılmadan önce yapın.
# Bu şekilde, Pydantic Settings sınıfı örneklendiğinde ortam değişkenleri zaten bellekte olacaktır.
# __file__ değişkeni bu dosyanın (settings.py) yolunu verir.
# Path(__file__).resolve() -> /home/mekzcgl/Staj2/RandevuRezervasyonSistemi/backend/core/settings.py
# .parents[0] -> /home/mekzcgl/Staj2/RandevuRezervasyonSistemi/backend/core/
# .parents[1] -> /home/mekzcgl/Staj2/RandevuRezervasyonSistemi/backend/ (yani 'backend' klasörü)
# .env dosyamız 'RandevuRezervasyonSistemi' ana dizininde olduğu için, 'backend' klasöründen bir seviye yukarı çıkmalıyız.
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / '.env') # Bu satır doğru kalmalı


# --- Hata ayıklama için eklenen print ifadeleri ---
print(f"DEBUG: core/settings.py konumu: {Path(__file__).resolve()}")
# .env dosyasının doğru konumunu gösteren debug yolu
dot_env_debug_path = Path(__file__).resolve().parents[2] / '.env'
print(f"DEBUG: .env aranacak konum (debug): {dot_env_debug_path}")
print(f"DEBUG: .env dosyası mevcut mu (debug)? {dot_env_debug_path.exists()}")
print(f"DEBUG: DATABASE_URL (os.getenv): {os.getenv('DATABASE_URL')}")
print(f"DEBUG: JWT_SECRET_KEY (os.getenv): {os.getenv('JWT_SECRET_KEY')}")
# --- Hata ayıklama için eklenen print ifadeleri sonu ---



class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=(
            '../.env', # settings.py'den bir seviye yukarı (backend), oradan .env'ye erişmek için
        ),
        extra='ignore',
        case_sensitive=True
    )

settings = Settings()