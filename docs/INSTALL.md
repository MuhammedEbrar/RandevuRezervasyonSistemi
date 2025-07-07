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