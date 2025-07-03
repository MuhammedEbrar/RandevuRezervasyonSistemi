# backend/core/settings.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    JWT_SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./sql_app.db" 

# Settings sınıfının bir örneği burada oluşturulur ve 'settings' adıyla dışarıya aktarılır.
settings = Settings() 
