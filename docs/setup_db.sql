-- docs/setup_db.sql

-- PostgreSQL'de veritabanı kullanıcısını oluştur (eğer yoksa)
-- Şifreyi kendi belirlediğiniz şifre ile değiştirin
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'randevuuser') THEN
      CREATE USER randevuuser WITH PASSWORD 'MEKPostgreSQL22003';
   END IF;
END
$do$;

-- PostgreSQL'de veritabanını oluştur (eğer yoksa) ve sahibini belirle
-- Veritabanı isminin küçük harfli olduğuna dikkat edin
CREATE DATABASE randevuplatformu_db OWNER randevuuser;

-- Oluşturulan kullanıcıya veritabanı üzerinde tüm yetkileri ver
GRANT ALL PRIVILEGES ON DATABASE randevuplatformu_db TO randevuuser;

-- İsteğe bağlı: Yeni rol için varsayılan ayarlar (genellikle iyidir)
ALTER ROLE randevuuser SET client_encoding TO 'utf8';
ALTER ROLE randevuuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE randevuuser SET timezone TO 'UTC';