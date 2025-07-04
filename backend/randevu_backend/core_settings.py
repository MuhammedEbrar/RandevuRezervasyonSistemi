# RandevuRezervasyonSistemi/backend/randevu_backend/core_settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv
import os # os modülünü de import ediyoruz

# --- Hata ayıklama için eklenen print ifadeleri ---
print(f"DEBUG: core_settings.py konumu: {Path(__file__).resolve()}")
dot_env_path = Path(__file__).resolve().parents[2] / '.env'
print(f"DEBUG: .env aranacak konum: {dot_env_path}")
print(f"DEBUG: .env dosyası mevcut mu? {dot_env_path.exists()}")
# --- Hata ayıklama için eklenen print ifadeleri sonu ---

load_dotenv(dotenv_path=dot_env_path)

# --- Hata ayıklama için eklenen print ifadeleri ---
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
            '../../.env', # RandevuRezervasyonSistemi/.env
        ),
        extra='ignore',
        case_sensitive=True
    )

settings = Settings()