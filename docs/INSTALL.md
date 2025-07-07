Elbette! Aşağıda verdiğiniz metni düzenlenmiş ve okunabilirliği yüksek şekilde **Markdown formatında** hazırladım:

---

````markdown
# Modüler Randevu ve Kiralama Platformu: Yerel Kurulum Rehberi

Bu rehber, projenin backend ve veritabanı ortamını yerel makinenizde kurmak için adım adım talimatlar içerir.

## 🧰 Önkoşullar

- **Python 3.13 veya üzeri:** [https://www.python.org/downloads/](https://www.python.org/downloads/)  
  _(Windows için indirin ve kurulumda PATH'e eklediğinizden emin olun.)_

- **Poetry:** Python paket yönetim aracı  
  Kurulum talimatları: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)

  - Windows'ta PowerShell ile kurmak için:
    ```powershell
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    ```
  - Kurulumdan sonra Poetry'nin PATH'e eklendiğinden emin olun. (Genellikle otomatik yapılır.)

- **PostgreSQL:** Veritabanı sunucusu  
  Windows için resmi installer veya Postgres.app önerilir:
  - [Resmi Installer](https://www.postgresql.org/download/windows/)
  - Kurulum sırasında bir superuser şifresi belirlemeniz istenir (örneğin `postgres` kullanıcısı için).

- **Git:** Versiyon kontrol sistemi  
  [https://git-scm.com/downloads](https://git-scm.com/downloads)

---

## ⚙️ Kurulum Adımları

### 1. 📁 Projeyi Klonlama

Projeyi GitHub’dan yerel makinenize kopyalayın:

```bash
git clone https://github.com/MuhammedEbrar/RandevuRezervasyonSistemi.git
````

---

### 2. 🗄️ PostgreSQL Veritabanı ve Kullanıcısı Oluşturma

1. **PostgreSQL servisinin çalıştığından emin olun.**
   Windows’ta servisler listesinden veya PostgreSQL uygulamasından başlatabilirsiniz.

2. **Yönetici yetkileriyle `psql` kabuğuna bağlanın.**

   * Windows’ta "SQL Shell (psql)" uygulamasını açın.
   * Server, Database, Port, Username için varsayılanları kabul edin.
   * Password kısmına PostgreSQL kurulumunda belirlediğiniz şifreyi girin.

3. **Aşağıdaki SQL komutlarını sırasıyla girin:**
   *(Şifreyi `.env` dosyasındakiyle aynı yapın)*

```sql
-- Kullanıcı oluştur (eğer yoksa) ve şifresini belirle
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
```

---

### 3. 📦 Poetry Bağımlılıklarını Kurma

Backend dizinine gidin ve bağımlılıkları kurun:

```bash
cd backend
poetry install --no-root
```

---

### 4. 🔧 Veritabanı Migrasyonlarını Uygulama

Alembic migrasyonlarıyla veritabanı şemasını oluşturun:

```bash
poetry run alembic upgrade head
```

---

### 5. 🚀 FastAPI Uygulamasını Başlatma

Uygulamayı yerel sunucuda çalıştırmak için:

```bash
poetry run uvicorn main:app --reload
```

Terminalde şu mesajı görmelisiniz:

```
Uvicorn running on http://127.0.0.1:8000
```

---

📝 Artık uygulamanız yerel ortamda çalışıyor! Gerekli tüm yapılandırmaları başarıyla tamamladınız.

```

---

İstersen bu Markdown içeriğini `.md` uzantılı bir dosyaya da dönüştürüp sana verebilirim. Yardımcı olayım mı?
```
