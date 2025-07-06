# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.settings import settings # settings objesini artık core_settings.py'den alıyoruz


SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() # Tüm modellerimiz bu Base'den türeyecek

# Dependency to get the database session (FastAPI için)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
