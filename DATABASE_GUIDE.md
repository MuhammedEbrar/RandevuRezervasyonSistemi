# PostgreSQL Veritabanı Yönetim Kılavuzu

Bu dokümantasyon, Randevu Rezervasyon Sistemi'nin PostgreSQL veritabanını incelemek ve yönetmek için gerekli tüm komutları içerir.

---

## 📋 İçindekiler

1. [Veritabanına Bağlanma](#veritabanına-bağlanma)
2. [Temel PostgreSQL Komutları](#temel-postgresql-komutları)
3. [Tabloları İnceleme](#tabloları-inceleme)
4. [Veri Sorgulama](#veri-sorgulama)
5. [Veri Ekleme/Güncelleme/Silme](#veri-eklemegüncellemesime)
6. [Yaygın Sorun Giderme](#yaygın-sorun-giderme)

---

## 1. Veritabanına Bağlanma

### Docker Container'a Bağlan ve PostgreSQL'e Gir

```bash
# Sunucuda şu komutu çalıştırın:
docker exec -it randevu_db psql -U randevuuser -d randevuplatformu_db
```

**Açıklama:**
- `docker exec -it` - Docker container'da interaktif komut çalıştır
- `randevu_db` - Container adı
- `psql` - PostgreSQL client
- `-U randevuuser` - Kullanıcı adı
- `-d randevuplatformu_db` - Veritabanı adı

**Başarılı bağlantı sonrası görünüm:**
```
psql (15.x)
Type "help" for help.

randevuplatformu_db=#
```

### Veritabanından Çıkış

```sql
\q
```
veya `Ctrl + D`

---

## 2. Temel PostgreSQL Komutları

### Meta Komutlar (\ ile başlayanlar)

| Komut | Açıklama |
|-------|----------|
| `\dt` | Tüm tabloları listele |
| `\d tablo_adı` | Tablo yapısını (sütunlar, tipler) göster |
| `\d+ tablo_adı` | Detaylı tablo bilgisi (indexler, constraintler) |
| `\du` | Kullanıcıları listele |
| `\l` | Tüm veritabanlarını listele |
| `\c veritabanı_adı` | Başka veritabanına geç |
| `\?` | Tüm meta komutları göster |
| `\h` | SQL komutları yardımı |
| `\q` | Çıkış |

---

## 3. Tabloları İnceleme

### Tüm Tabloları Listele

```sql
\dt
```

**Çıktı:**
```
             List of relations
 Schema |          Name          | Type  |    Owner
--------+------------------------+-------+--------------
 public | alembic_version        | table | randevuuser
 public | availability_schedules | table | randevuuser
 public | bookings               | table | randevuuser
 public | payments               | table | randevuuser
 public | pricing_rules          | table | randevuuser
 public | resources              | table | randevuuser
 public | users                  | table | randevuuser
```

### Tablo Yapısını Görüntüle

#### Users Tablosu

```sql
\d users
```

**Çıktı:**
```
Column       | Type                  | Nullable | Default
-------------+-----------------------+----------+------------------
user_id      | uuid                  | not null | uuid_generate_v4()
email        | character varying     | not null |
password_hash| character varying     | not null |
full_name    | character varying     |          |
phone_number | character varying     |          |
role         | user_role             | not null | 'CUSTOMER'
is_active    | boolean               |          | true
created_at   | timestamp with time zone |       | now()
```

#### Resources Tablosu

```sql
\d resources
```

#### Bookings Tablosu

```sql
\d bookings
```

#### Payments Tablosu

```sql
\d payments
```

#### Pricing Rules Tablosu

```sql
\d pricing_rules
```

#### Availability Schedules Tablosu

```sql
\d availability_schedules
```

---

## 4. Veri Sorgulama

### Kullanıcıları Görüntüleme

#### Tüm kullanıcıları listele

```sql
SELECT * FROM users;
```

#### Kullanıcıları role göre listele

```sql
-- Müşterileri listele
SELECT user_id, email, full_name, phone_number, role, created_at
FROM users
WHERE role = 'CUSTOMER';

-- İşletme sahiplerini listele
SELECT user_id, email, full_name, phone_number, role, created_at
FROM users
WHERE role = 'BUSINESS_OWNER';
```

#### Belirli kullanıcıyı ara

```sql
-- Email ile ara
SELECT * FROM users WHERE email = 'test@example.com';

-- ID ile ara
SELECT * FROM users WHERE user_id = 'kullanıcı-uuid-buraya';
```

#### Kullanıcı sayısını öğren

```sql
SELECT role, COUNT(*) as kullanici_sayisi
FROM users
GROUP BY role;
```

### Kaynakları (Resources) Görüntüleme

```sql
-- Tüm kaynakları listele
SELECT * FROM resources;

-- Aktif kaynakları listele
SELECT resource_id, name, type, is_active, created_at
FROM resources
WHERE is_active = true;

-- Belirli sahibin kaynaklarını listele
SELECT r.name, r.type, r.capacity, u.full_name as owner_name
FROM resources r
JOIN users u ON r.owner_id = u.user_id
WHERE u.email = 'owner@example.com';
```

### Rezervasyonları (Bookings) Görüntüleme

```sql
-- Tüm rezervasyonları listele
SELECT * FROM bookings;

-- Son 10 rezervasyon
SELECT b.booking_id, r.name as resource_name, u.full_name as customer_name,
       b.start_time, b.end_time, b.status, b.total_price
FROM bookings b
JOIN resources r ON b.resource_id = r.resource_id
JOIN users u ON b.customer_id = u.user_id
ORDER BY b.created_at DESC
LIMIT 10;

-- Belirli müşterinin rezervasyonları
SELECT b.booking_id, r.name, b.start_time, b.end_time, b.status, b.total_price
FROM bookings b
JOIN resources r ON b.resource_id = r.resource_id
WHERE b.customer_id = 'müşteri-uuid-buraya';

-- Durum bazında rezervasyon sayısı
SELECT status, COUNT(*) as adet
FROM bookings
GROUP BY status;
```

### Ödemeleri (Payments) Görüntüleme

```sql
-- Tüm ödemeleri listele
SELECT * FROM payments;

-- Başarılı ödemeleri listele
SELECT p.payment_id, p.amount, p.currency, p.status,
       u.full_name as customer_name, b.booking_id
FROM payments p
JOIN bookings b ON p.booking_id = b.booking_id
JOIN users u ON p.customer_id = u.user_id
WHERE p.is_successful = true;
```

### Fiyatlandırma Kurallarını (Pricing Rules) Görüntüleme

```sql
-- Tüm fiyatlandırma kurallarını listele
SELECT * FROM pricing_rules;

-- Belirli kaynağın fiyatlandırma kuralları
SELECT pr.*, r.name as resource_name
FROM pricing_rules pr
JOIN resources r ON pr.resource_id = r.resource_id
WHERE r.name = 'Halı Saha A';

-- Aktif fiyatlandırma kuralları
SELECT * FROM pricing_rules WHERE is_active = true;
```

### Müsaitlik Takvimini (Availability Schedules) Görüntüleme

```sql
-- Tüm müsaitlik takvimini listele
SELECT * FROM availability_schedules;

-- Belirli kaynağın müsaitlik takvimi
SELECT a.*, r.name as resource_name
FROM availability_schedules a
JOIN resources r ON a.resource_id = r.resource_id
WHERE r.name = 'Halı Saha A';
```

---

## 5. Veri Ekleme/Güncelleme/Silme

### Kullanıcı Ekleme (Manuel - Genelde API üzerinden yapılır)

```sql
-- NOT: Şifreyi manuel hash'lemek yerine API kullanın!
-- Bu sadece test amaçlıdır

INSERT INTO users (email, password_hash, full_name, phone_number, role)
VALUES (
    'test@example.com',
    '$2b$12$hashedpasswordburaya', -- API üzerinden kayıt yapın!
    'Test Kullanıcı',
    '+905551234567',
    'CUSTOMER'
);
```

### Kullanıcı Güncelleme

```sql
-- Email güncelleme
UPDATE users
SET email = 'yeni@email.com'
WHERE user_id = 'kullanıcı-uuid-buraya';

-- Telefon numarası güncelleme
UPDATE users
SET phone_number = '+905559876543'
WHERE email = 'test@example.com';

-- Kullanıcıyı aktif/pasif yapma
UPDATE users
SET is_active = false
WHERE email = 'test@example.com';
```

### Kaynak Güncelleme

```sql
-- Kaynağı aktif/pasif yapma
UPDATE resources
SET is_active = false
WHERE name = 'Halı Saha A';

-- Kapasite güncelleme
UPDATE resources
SET capacity = 20
WHERE resource_id = 'kaynak-uuid-buraya';
```

### Rezervasyon Durumu Güncelleme

```sql
-- Rezervasyonu iptal et
UPDATE bookings
SET status = 'CANCELLED'
WHERE booking_id = 'rezervasyon-uuid-buraya';

-- Ödeme durumunu güncelle
UPDATE bookings
SET payment_status = 'PAID'
WHERE booking_id = 'rezervasyon-uuid-buraya';
```

### Veri Silme (DİKKAT!)

```sql
-- Test kullanıcısını sil (CASCADE dikkat!)
DELETE FROM users WHERE email = 'test@example.com';

-- Test rezervasyonunu sil
DELETE FROM bookings WHERE booking_id = 'rezervasyon-uuid-buraya';
```

---

## 6. Yaygın Sorun Giderme

### Kullanıcı Giriş Yapamıyor

```sql
-- Kullanıcının var olup olmadığını kontrol et
SELECT email, role, is_active, created_at
FROM users
WHERE email = 'kullanıcı@email.com';

-- Kullanıcı pasif mi kontrol et
SELECT email, is_active
FROM users
WHERE email = 'kullanıcı@email.com' AND is_active = false;
```

### Rezervasyon Fiyatı Hesaplanmıyor

```sql
-- İlgili kaynağın fiyatlandırma kuralı var mı?
SELECT pr.*, r.name as resource_name
FROM pricing_rules pr
JOIN resources r ON pr.resource_id = r.resource_id
WHERE r.name = 'Kaynak Adı'
  AND pr.is_active = true;

-- Hiç fiyatlandırma kuralı var mı?
SELECT COUNT(*) FROM pricing_rules WHERE is_active = true;
```

### Müsait Slot Görünmüyor

```sql
-- Kaynağın müsaitlik takvimi var mı?
SELECT a.*, r.name
FROM availability_schedules a
JOIN resources r ON a.resource_id = r.resource_id
WHERE r.name = 'Kaynak Adı';

-- Hiç müsaitlik takvimi var mı?
SELECT COUNT(*) FROM availability_schedules;
```

### Veritabanını Sıfırlama (TÜMÜNÜ SİLER - DİKKATLİ!)

```sql
-- Tüm rezervasyonları sil
TRUNCATE TABLE bookings CASCADE;

-- Tüm kaynakları sil
TRUNCATE TABLE resources CASCADE;

-- Tüm kullanıcıları sil
TRUNCATE TABLE users CASCADE;

-- VEYA tüm tabloları temizle
TRUNCATE TABLE users, resources, bookings, payments,
               pricing_rules, availability_schedules CASCADE;
```

---

## 7. Kullanışlı Sorgular

### Toplam İstatistikler

```sql
-- Özet istatistikler
SELECT
    (SELECT COUNT(*) FROM users WHERE role = 'CUSTOMER') as musteri_sayisi,
    (SELECT COUNT(*) FROM users WHERE role = 'BUSINESS_OWNER') as isletme_sayisi,
    (SELECT COUNT(*) FROM resources WHERE is_active = true) as aktif_kaynak_sayisi,
    (SELECT COUNT(*) FROM bookings WHERE status = 'CONFIRMED') as onaylanmis_rezervasyon,
    (SELECT SUM(total_price) FROM bookings WHERE payment_status = 'PAID') as toplam_kazanc;
```

### Bugünkü Rezervasyonlar

```sql
SELECT b.booking_id, r.name, u.full_name as customer,
       b.start_time, b.status
FROM bookings b
JOIN resources r ON b.resource_id = r.resource_id
JOIN users u ON b.customer_id = u.user_id
WHERE DATE(b.start_time) = CURRENT_DATE
ORDER BY b.start_time;
```

### En Çok Rezervasyon Yapılan Kaynaklar

```sql
SELECT r.name, COUNT(b.booking_id) as rezervasyon_sayisi
FROM resources r
LEFT JOIN bookings b ON r.resource_id = b.resource_id
GROUP BY r.resource_id, r.name
ORDER BY rezervasyon_sayisi DESC
LIMIT 10;
```

### Gelir Raporu (Aylık)

```sql
SELECT
    TO_CHAR(b.created_at, 'YYYY-MM') as ay,
    COUNT(*) as rezervasyon_sayisi,
    SUM(b.total_price) as toplam_gelir,
    SUM(CASE WHEN b.payment_status = 'PAID' THEN b.total_price ELSE 0 END) as odenen_gelir
FROM bookings b
GROUP BY TO_CHAR(b.created_at, 'YYYY-MM')
ORDER BY ay DESC;
```

---

## 8. Güvenlik İpuçları

1. **Asla production veritabanında test yapmayın**
2. **DELETE/UPDATE/TRUNCATE komutlarından önce WHERE şartını iki kez kontrol edin**
3. **Şifreleri manuel eklemeyin - API kullanın**
4. **Yedek almadan toplu silme yapmayın**
5. **Docker container dışından direkt veritabanına bağlanmayın**

---

## 9. Yedekleme ve Geri Yükleme

### Veritabanını Yedekleme

```bash
# Sunucuda çalıştırın:
docker exec randevu_db pg_dump -U randevuuser randevuplatformu_db > backup_$(date +%Y%m%d).sql
```

### Yedekten Geri Yükleme

```bash
# Sunucuda çalıştırın:
docker exec -i randevu_db psql -U randevuuser -d randevuplatformu_db < backup_20250101.sql
```

---

## 10. Hızlı Referans

### Veritabanına Bağlan
```bash
docker exec -it randevu_db psql -U randevuuser -d randevuplatformu_db
```

### En Çok Kullanılan Komutlar
```sql
\dt                          -- Tabloları listele
\d users                     -- users tablosu yapısı
SELECT * FROM users;         -- Tüm kullanıcılar
SELECT * FROM bookings;      -- Tüm rezervasyonlar
SELECT * FROM resources;     -- Tüm kaynaklar
\q                          -- Çıkış
```

---

## 📞 Yardım

Sorun yaşarsanız:
1. `\?` - PostgreSQL yardım
2. `\h SELECT` - SQL komut yardımı
3. Docker logları: `docker logs randevu_db`

---

**Son Güncelleme:** 2025-01-24
**Versiyon:** 1.0
