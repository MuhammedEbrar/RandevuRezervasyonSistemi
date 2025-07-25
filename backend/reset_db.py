# backend/reset_db.py

import sys
from pathlib import Path

# Proje yolunu sys.path'e ekleyerek importların çalışmasını sağla
sys.path.append(str(Path(__file__).resolve().parent))

from database import Base, engine
# Tüm modellerin import edilmesini ve Base.metadata tarafından tanınmasını sağla
import models

def reset_database():
    print("Mevcut tablolar siliniyor...")
    # Önce tüm tabloları siler (eğer varsa)
    Base.metadata.drop_all(bind=engine)
    print("Tüm tablolar silindi.")

    print("Yeni şema oluşturuluyor...")
    # Modellerde tanımlı tüm tabloları oluşturur
    Base.metadata.create_all(bind=engine)
    print("Yeni şema başarıyla oluşturuldu!")

if __name__ == "__main__":
    reset_database()