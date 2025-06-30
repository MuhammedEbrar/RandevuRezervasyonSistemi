# RandevuRezervasyonSistemi
Bu 4 kişilik bir stajyer ekibin staj süresince geliştirmeye başladığı bir projedir.
<<<<<<< HEAD

# Randevu ve Kiralama Platformu

Bu proje, işletme sahipleri ve müşteriler için modüler bir randevu ve kiralama platformu oluşturmayı amaçlamaktadır.
İşletme sahipleri, hizmetlerini veya kaynaklarını (örn: diş hekimi, halı saha, etkinlik alanı) sisteme tanımlayabilirken,
  müşteriler bu hizmetler için kolayca rezervasyon yapabilirler.

## Çekirdek Kavramlar

* **Varlık (Resource):** Sisteme eklenebilen her türlü hizmet veya fiziksel alan. Esnek bir yapıyla tanımlanabilir (örn: Bireysel Hizmet, Toplu Kiralama Alanı).
* **Müsaitlik Takvimi (Availability):** Her varlığın kendi çalışma saatlerini ve özel müsaitlik durumlarını tanımlayabilmesi.
* **Fiyatlandırma Motoru (Pricing Engine):** Saatlik, günlük veya birim bazında dinamik olarak fiyat hesaplama yeteneği.
* **Rezervasyon Motoru (Booking Engine):** Tek seferlik ve tekrarlayan rezervasyonları yönetme, çakışmaları önleme ve kapora/ödeme süreçlerini entegre etme.

## Proje Amaçları

* İşletme sahiplerine kolayca hizmet ve kaynaklarını yönetme imkanı sunmak.
* Müşterilere sezgisel bir arayüz ile randevu ve kiralama yapma deneyimi sağlamak.
* Modüler ve ölçeklenebilir bir mimari ile gelecekteki geliştirmelere uygun bir temel oluşturmak.

## Kullanılan Teknolojiler (Tech Stack)

### Backend (Sunucu Tarafı)
* **Dil:** Python
* **Web Çatısı (Framework):** FastAPI
* **Veritabanı ORM:** SQLAlchemy

### Frontend (Kullanıcı Arayüzü)
* **Çerçeve (Framework):** React
* **Paket Yöneticisi:** npm / Yarn
* **Stil (CSS Framework):** Tailwind CSS / Chakra UI (Tercihe göre seçilecektir)

### Veritabanı
* **İlişkisel Veritabanı:** PostgreSQL
* **Önbellekleme (Opsiyonel):** Redis (Gelecekteki performans iyileştirmeleri için)

### Versiyon Kontrol
* **Sistem:** Git
* **Platform:** GitHub

## Kurulum ve Geliştirme Ortamı

Bu projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin.

### Ön Gereksinimler

* Python 3.8+
* Node.js ve npm/Yarn
* PostgreSQL
* Git

### Projeyi Klonlama

```bash
# Projeyi kaydetmek istediğiniz dizine gidin
cd ~/Documents/Projects # veya istediğiniz başka bir dizin

# GitHub'dan projeyi klonlayın (SSH kullanılıyorsa)
git clone git@github.com:MuhammedEbrar/RandevuRezervasyonSistemi.git

# Klonlanan projenin dizinine geçin
cd RandevuRezervasyonSistemi

#Bu satır iskender tarafından düzenlenmiştir.
=======
>>>>>>> parent of be1fce3 (README.md güncellendi)
