# Modüler Randevu ve Kiralama Platformu: Yerel Kurulum Rehberi

Bu rehber, projenin backend ve veritabanı ortamını yerel makinenizde kurmak için adım adım talimatlar içerir.

## Önkoşullar

* **Python 3.13 veya üzeri:** https://www.python.org/downloads/ (Windows için indirin ve kurulumda PATH'e eklediğinizden emin olun.)
* **Poetry:** Python paket yönetim aracı. Kurulum talimatları: https://python-poetry.org/docs/#installation
    * Windows'ta PowerShell'den kurmak için: `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -`
    * Kurulumdan sonra Poetry'nin PATH'e eklendiğinden emin olun (genellikle otomatik yapılır veya komut çıktısında yönlendirme olur).
* **PostgreSQL:** Veritabanı sunucusu. Windows için resmi installer veya Postgres.app önerilir:
    * Resmi Installer: https://www.postgresql.org/download/windows/
    * Kurulum sırasında bir yönetici (superuser) şifresi belirlemeniz istenecektir (örneğin `postgres` kullanıcısı için).
* **Git:** Versiyon kontrol sistemi. https://git-scm.com/downloads

## Kurulum Adımları

### 1. Projeyi Klonlama

Projeyi GitHub'dan yerel makinenize kopyalayın:

```bash
git clone [https://github.com/MuhammedEbrar/RandevuRezervasyonSistemi.git](https://github.com/MuhammedEbrar/RandevuRezervasyonSistemi.git)


### 2. PostgreSQL Veritabanı ve Kullanıcısı Oluşturma

Bu adımda, uygulamanın kullanacağı veritabanını ve kullanıcıyı oluşturacaksınız.

    * PostgreSQL servisi çalıştığından emin olun. Windows'ta genellikle servisler listesinden veya PostgreSQL uygulamalarından başlatabilirsiniz.

    * Yönetici yetkileriyle (örneğin postgres kullanıcısı olarak) PostgreSQL komut istemcisine (psql) bağlanın. Windows'ta Başlat Menüsü'nden "SQL Shell (psql)" uygulamasını bulabilirsiniz. Server, Database, Port, Username için varsayılanları kabul edin, Password kısmına PostgreSQL kurulumunda belirlediğiniz yönetici şifresini girin.

    * Açılan psql komut istemcisinde aşağıdaki SQL komutlarını çalıştırın. Bu komutları tek tek kopyalayıp yapıştırın ve her satırın sonunda Enter tuşuna basın.

 ------------------------------------------------------------------------------------

    -- Kullanıcı oluştur (eğer yoksa) ve şifresini belirle
-- Şifreyi projenizdeki .env dosyasında kullanacağınız şifre ile aynı yapın!
-- RANDENİZİ KENDİNİZ GİRİN
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'randevuuser') THEN
      CREATE USER randevuuser WITH PASSWORD 'MEKPostgreSQL22003';
   END IF;
END
$do$;

-- Veritabanı oluştur (eğer yoksa) ve sahibini belirle
CREATE DATABASE randevuplatformu_db OWNER randevuuser;

-- Kullanıcıya veritabanı üzerinde tüm yetkileri ver
GRANT ALL PRIVILEGES ON DATABASE randevuplatformu_db TO randevuuser;

-- İsteğe bağlı: Yeni rol için varsayılan ayarlar
ALTER ROLE randevuuser SET client_encoding TO 'utf8';
ALTER ROLE randevuuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE randevuuser SET timezone TO 'UTC';

 ------------------------------------------------------------------------------------

 ### 3.Poetry Bağımlılıklarını Kurma

* Backend dizinine giderek Python bağımlılıklarını Poetry ile kurun:


    cd backend
    poetry install --no-root

### 4. Veritabanı Migrasyonlarını Uygulama

* Projenin veritabanı şemasını oluşturmak için Alembic migrasyonlarını uygulayın:


    poetry run alembic upgrade head

### 5. FastAPI Uygulamasını Başlatma

* Uygulamayı yerel sunucunuzda başlatın:


    poetry run uvicorn main:app --reload

Uygulama çalışmaya başladığında terminalde Uvicorn running on http://127.0.0.1:8000 mesajını görmelisiniz.