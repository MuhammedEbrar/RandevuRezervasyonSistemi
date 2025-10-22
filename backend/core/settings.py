# backend/core/settings.py
# Bu dosya, uygulamanın ayarlarını (veritabanı URL'si, JWT anahtarı vb.) yönetir.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file='../.env',
        extra='ignore',
        case_sensitive=True
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert comma-separated CORS origins to list"""
        if self.ENVIRONMENT == "development":
            return ["*"]  # Allow all in development
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

settings = Settings()