# Randevu ve Kiralama Platformu

Bu proje, modüler ve ölçeklenebilir bir randevu ve kiralama sistemi platformudur. Kullanıcıların kaynakları (araçlar, odalar, ekipmanlar vb.) rezerve etmelerini, uygunluk durumlarını kontrol etmelerini ve ödeme işlemlerini gerçekleştirmelerini sağlar.

## 🚀 Özellikler

Proje aşağıdaki temel modüllerden oluşmaktadır:

- **Kimlik Doğrulama (Auth)**: Kullanıcı kayıt, giriş ve JWT tabanlı yetkilendirme.
- **Kullanıcı Yönetimi (Users)**: Profil yönetimi ve rol tabanlı erişim kontrolü.
- **Kaynak Yönetimi (Resources)**: Kiralanabilir varlıkların (araç, oda vb.) tanımlanması ve yönetimi.
- **Uygunluk (Availability)**: Kaynakların müsaitlik durumlarının takibi.
- **Fiyatlandırma (Pricing)**: Dinamik fiyatlandırma kuralları.
- **Rezervasyon (Bookings)**: Randevu oluşturma, iptal ve güncelleme işlemleri.
- **Ödeme (Payments)**: Ödeme entegrasyonu ve işlem takibi.

## 🛠️ Teknoloji Yığını

Proje modern ve güçlü teknolojiler kullanılarak geliştirilmiştir:

### Backend
- **Dil**: Python 3.11+
- **Framework**: FastAPI
- **Veritabanı**: PostgreSQL
- **ORM**: SQLAlchemy (Async)
- **Paket Yöneticisi**: Poetry
- **Migrasyon**: Alembic

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Dil**: JavaScript/JSX

### Mobile
- **Framework**: Flutter
- **Dil**: Dart

### Altyapı
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx

## 📂 Proje Yapısı

```
RandevuRezervasyonSistemi/
├── backend/                # FastAPI backend uygulaması
├── frontend/               # React frontend uygulaması
├── mobile/                 # Flutter mobil uygulaması
├── nginx/                  # Nginx konfigürasyonları
├── docker-compose.yml      # Docker servis tanımları
├── MOBILE_API_DOCUMENTATION.md # Mobil API dokümantasyonu
└── GITHUB_PR_REHBER.md     # GitHub Pull Request rehberi
```

## 🏁 Kurulum ve Çalıştırma

Projeyi yerel ortamınızda çalıştırmak için Docker ve Docker Compose'un yüklü olması gerekmektedir.

1. **Repoyu Klonlayın:**
   ```bash
   git clone <repo-url>
   cd RandevuRezervasyonSistemi
   ```

2. **Frontend'i Derleyin:**
   Docker çalıştırmadan önce frontend uygulamasının derlenmesi gereklidir.
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

3. **Çevresel Değişkenleri Ayarlayın:**
   `backend` ve `frontend` klasörleri içindeki `.env.example` dosyalarını `.env` olarak kopyalayın ve gerekli ayarları yapın.
   *(Not: `docker-compose.yml` varsayılan değerlerle çalışacak şekilde yapılandırılmıştır, ancak prodüksiyon için şifreleri değiştirmeniz önerilir.)*

3. **Docker ile Başlatın:**
   Ana dizinde aşağıdaki komutu çalıştırarak tüm servisleri (db, api, nginx) başlatın:
   ```bash
   docker-compose up --build
   ```

4. **Erişim:**
   - **Frontend**: [http://localhost](http://localhost)
   - **Backend API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs) (Nginx üzerinden yönlendirme ayarına göre değişebilir, direkt erişim için port 8000)

## 📚 Dokümantasyon

Daha detaylı bilgi için proje içindeki diğer dokümanlara göz atabilirsiniz:

- [Mobil API Dokümantasyonu](MOBILE_API_DOCUMENTATION.md)
- [GitHub PR ve Katkı Rehberi](GITHUB_PR_REHBER.md)

## 🤝 Katkıda Bulunma

Lütfen değişiklik yapmadan önce [GITHUB_PR_REHBER.md](GITHUB_PR_REHBER.md) dosyasını okuyunuz.
