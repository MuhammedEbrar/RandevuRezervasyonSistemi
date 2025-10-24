# Randevu ve Kiralama Platformu - Mobil API Dokümantasyonu

## 📋 Genel Bilgiler

### API Base URL
- **Production:** `http://13.60.31.19/api/v1`
- **API Docs:** `http://13.60.31.19/docs`

### Authentication
- **Tip:** JWT (JSON Web Token)
- **Header:** `Authorization: Bearer {token}`
- **Token Expire:** 30 dakika

---

## 🔐 Authentication Endpoints

### 1. Kullanıcı Kaydı (Register)

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "minimum8karakter",
  "role": "CUSTOMER",  // veya "BUSINESS_OWNER"
  "first_name": "Ahmet",
  "last_name": "Yılmaz",
  "phone_number": "5551234567"  // Opsiyonel
}
```

**Validasyon Kuralları:**
- `email`: Geçerli email formatı
- `password`: Minimum 8 karakter
- `role`: Sadece "CUSTOMER" veya "BUSINESS_OWNER"
- `first_name`, `last_name`: Opsiyonel
- `phone_number`: Opsiyonel

**Success Response (201 Created):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "role": "CUSTOMER",
  "first_name": "Ahmet",
  "last_name": "Yılmaz",
  "phone_number": "5551234567",
  "profile_picture_url": null,
  "is_active": true,
  "created_at": "2025-10-23T10:30:00",
  "updated_at": null
}
```

**Error Response (422 Validation Error):**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "123",
      "ctx": {"min_length": 8}
    }
  ]
}
```

---

### 2. Kullanıcı Girişi (Login)

**Endpoint:** `POST /auth/login`

**Request Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Request Body (Form Data):**
```
username=user@example.com
password=sifre123456
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Email veya şifre hatalı."
}
```

---

## 👤 User Endpoints

### 3. Kullanıcı Profilini Getir

**Endpoint:** `GET /users/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200 OK):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "role": "CUSTOMER",
  "first_name": "Ahmet",
  "last_name": "Yılmaz",
  "phone_number": "5551234567",
  "profile_picture_url": null,
  "is_active": true,
  "created_at": "2025-10-23T10:30:00",
  "updated_at": "2025-10-23T11:00:00"
}
```

---

### 4. Kullanıcı Profilini Güncelle

**Endpoint:** `PUT /users/me`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "first_name": "Mehmet",
  "last_name": "Demir",
  "phone_number": "5559876543",
  "profile_picture_url": "https://example.com/photo.jpg"
}
```

**Success Response (200 OK):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "role": "CUSTOMER",
  "first_name": "Mehmet",
  "last_name": "Demir",
  "phone_number": "5559876543",
  "profile_picture_url": "https://example.com/photo.jpg",
  "is_active": true,
  "created_at": "2025-10-23T10:30:00",
  "updated_at": "2025-10-23T12:00:00"
}
```

---

## 🏢 Resource Endpoints (İş Yerleri / Kaynaklar)

### 5. Tüm Kaynakları Listele

**Endpoint:** `GET /resources/`

**Query Parameters:**
- `skip` (int, optional): Atlanacak kayıt sayısı (default: 0)
- `limit` (int, optional): Getirilecek kayıt sayısı (default: 100)
- `active_only` (bool, optional): Sadece aktif kaynaklar (default: true)

**Example:** `GET /resources/?skip=0&limit=10&active_only=true`

**Success Response (200 OK):**
```json
[
  {
    "resource_id": "123e4567-e89b-12d3-a456-426614174001",
    "owner_id": "123e4567-e89b-12d3-a456-426614174000",
    "resource_name": "Kuaför Salonu",
    "resource_type": "SINGLE_SLOT",
    "booking_type": "APPOINTMENT",
    "description": "Modern kuaför salonu",
    "location": "İstanbul, Kadıköy",
    "capacity": 1,
    "is_active": true,
    "created_at": "2025-10-23T09:00:00"
  }
]
```

---

### 6. Kaynak Detayı

**Endpoint:** `GET /resources/{resource_id}`

**Success Response (200 OK):**
```json
{
  "resource_id": "123e4567-e89b-12d3-a456-426614174001",
  "owner_id": "123e4567-e89b-12d3-a456-426614174000",
  "resource_name": "Kuaför Salonu",
  "resource_type": "SINGLE_SLOT",
  "booking_type": "APPOINTMENT",
  "description": "Modern kuaför salonu",
  "location": "İstanbul, Kadıköy",
  "capacity": 1,
  "is_active": true,
  "created_at": "2025-10-23T09:00:00"
}
```

---

### 7. Yeni Kaynak Oluştur (Sadece BUSINESS_OWNER)

**Endpoint:** `POST /resources/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "resource_name": "Spor Salonu",
  "resource_type": "MULTI_SLOT",
  "booking_type": "RENTAL",
  "description": "Modern fitness merkezi",
  "location": "Ankara, Çankaya",
  "capacity": 50
}
```

**Enum Values:**
- `resource_type`: "SINGLE_SLOT" | "MULTI_SLOT" | "UNLIMITED"
- `booking_type`: "APPOINTMENT" | "RENTAL"

**Success Response (201 Created):**
```json
{
  "resource_id": "123e4567-e89b-12d3-a456-426614174002",
  "owner_id": "123e4567-e89b-12d3-a456-426614174000",
  "resource_name": "Spor Salonu",
  "resource_type": "MULTI_SLOT",
  "booking_type": "RENTAL",
  "description": "Modern fitness merkezi",
  "location": "Ankara, Çankaya",
  "capacity": 50,
  "is_active": true,
  "created_at": "2025-10-23T14:00:00"
}
```

---

## 📅 Availability Endpoints (Müsaitlik Takvimi)

### 8. Kaynak Müsaitlik Takvimini Getir

**Endpoint:** `GET /resources/{resource_id}/availability/`

**Success Response (200 OK):**
```json
[
  {
    "schedule_id": "123e4567-e89b-12d3-a456-426614174003",
    "resource_id": "123e4567-e89b-12d3-a456-426614174001",
    "schedule_type": "WEEKLY",
    "day_of_week": "MONDAY",
    "start_time": "09:00:00",
    "end_time": "18:00:00",
    "is_active": true
  }
]
```

**Enum Values:**
- `schedule_type`: "WEEKLY" | "ONE_TIME"
- `day_of_week`: "MONDAY" | "TUESDAY" | "WEDNESDAY" | "THURSDAY" | "FRIDAY" | "SATURDAY" | "SUNDAY"

---

### 9. Müsait Slot'ları Getir

**Endpoint:** `GET /resources/{resource_id}/availability/available_slots`

**Query Parameters:**
- `start_date` (string, required): Başlangıç tarihi (YYYY-MM-DD)
- `end_date` (string, required): Bitiş tarihi (YYYY-MM-DD)

**Example:** `GET /resources/{resource_id}/availability/available_slots?start_date=2025-10-25&end_date=2025-10-25`

**Success Response (200 OK):**
```json
[
  {
    "start_time": "2025-10-25T09:00:00",
    "end_time": "2025-10-25T10:00:00",
    "is_available": true
  },
  {
    "start_time": "2025-10-25T10:00:00",
    "end_time": "2025-10-25T11:00:00",
    "is_available": true
  },
  {
    "start_time": "2025-10-25T11:00:00",
    "end_time": "2025-10-25T12:00:00",
    "is_available": false
  }
]
```

---

## 📝 Booking Endpoints (Rezervasyonlar)

### 10. Fiyat Hesaplama

**Endpoint:** `POST /bookings/calculate_price`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "resource_id": "123e4567-e89b-12d3-a456-426614174001",
  "start_time": "2025-10-25T10:00:00",
  "end_time": "2025-10-25T11:00:00"
}
```

**Success Response (200 OK):**
```json
{
  "total_price": 150.00
}
```

---

### 11. Rezervasyon Oluştur

**Endpoint:** `POST /bookings/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "resource_id": "123e4567-e89b-12d3-a456-426614174001",
  "start_time": "2025-10-25T10:00:00",
  "end_time": "2025-10-25T11:00:00",
  "notes": "Saç kesimi istiyorum"
}
```

**Success Response (201 Created):**
```json
{
  "booking_id": "123e4567-e89b-12d3-a456-426614174004",
  "resource_id": "123e4567-e89b-12d3-a456-426614174001",
  "customer_id": "123e4567-e89b-12d3-a456-426614174000",
  "start_time": "2025-10-25T10:00:00",
  "end_time": "2025-10-25T11:00:00",
  "total_price": 150.00,
  "status": "PENDING",
  "notes": "Saç kesimi istiyorum",
  "created_at": "2025-10-23T15:00:00"
}
```

**Booking Status Enum:**
- "PENDING": Bekliyor
- "CONFIRMED": Onaylandı
- "CANCELLED": İptal edildi
- "COMPLETED": Tamamlandı
- "NO_SHOW": Gelmedi

---

### 12. Müşterinin Rezervasyonlarını Getir

**Endpoint:** `GET /bookings/customer`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200 OK):**
```json
[
  {
    "booking_id": "123e4567-e89b-12d3-a456-426614174004",
    "resource_id": "123e4567-e89b-12d3-a456-426614174001",
    "customer_id": "123e4567-e89b-12d3-a456-426614174000",
    "start_time": "2025-10-25T10:00:00",
    "end_time": "2025-10-25T11:00:00",
    "total_price": 150.00,
    "status": "CONFIRMED",
    "notes": "Saç kesimi istiyorum",
    "created_at": "2025-10-23T15:00:00"
  }
]
```

---

## 💳 Payment Endpoints (Ödemeler)

### 13. Ödeme Oluştur

**Endpoint:** `POST /payments/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "booking_id": "123e4567-e89b-12d3-a456-426614174004",
  "payment_method": "CREDIT_CARD",
  "amount": 150.00
}
```

**Payment Method Enum:**
- "CREDIT_CARD"
- "DEBIT_CARD"
- "CASH"
- "BANK_TRANSFER"

**Success Response (201 Created):**
```json
{
  "payment_id": "123e4567-e89b-12d3-a456-426614174005",
  "booking_id": "123e4567-e89b-12d3-a456-426614174004",
  "amount": 150.00,
  "payment_method": "CREDIT_CARD",
  "payment_status": "COMPLETED",
  "payment_date": "2025-10-23T15:30:00"
}
```

**Payment Status Enum:**
- "PENDING": Bekliyor
- "COMPLETED": Tamamlandı
- "FAILED": Başarısız
- "REFUNDED": İade edildi

---

## 🔧 Genel Bilgiler

### Tarih-Saat Formatları
- **ISO 8601:** `2025-10-25T10:00:00`
- **Tarih:** `2025-10-25`
- **Saat:** `09:00:00`

### UUID Formatı
- **Format:** `123e4567-e89b-12d3-a456-426614174000`
- Tüm ID'ler UUID v4 formatında

### Pagination
- `skip`: Kaç kayıt atlanacak (default: 0)
- `limit`: Kaç kayıt getirilecek (default: 100)

### Error Codes
- `200`: OK - Başarılı
- `201`: Created - Kayıt oluşturuldu
- `400`: Bad Request - Hatalı istek
- `401`: Unauthorized - Yetkisiz erişim
- `403`: Forbidden - Erişim yasak
- `404`: Not Found - Bulunamadı
- `422`: Validation Error - Doğrulama hatası
- `500`: Internal Server Error - Sunucu hatası

---

## 🧪 Test Kullanıcıları

### Test için Database Credentials (Geliştirme Amaçlı)
```
Database Host: 13.60.31.19:5432
Database Name: randevuplatformu_db
Username: randevuuser
Password: RandevuDB2025SecurePass
```

**NOT:** Production için bu bilgileri kullanmayın!

---

## 📱 Mobil Uygulama İçin Öneriler

### 1. Token Yönetimi
- Token'ı güvenli şekilde saklayın (Keychain/Keystore)
- Her istekte `Authorization: Bearer {token}` header'ı ekleyin
- Token expire olduğunda kullanıcıyı yeniden login'e yönlendirin

### 2. Error Handling
- 401 hatası → Kullanıcıyı login sayfasına yönlendirin
- 422 hatası → Validation error mesajlarını kullanıcıya gösterin
- 500 hatası → "Sunucu hatası, lütfen daha sonra tekrar deneyin" mesajı gösterin

### 3. Offline Desteği
- Kritik verileri local cache'leyin
- Network olmadığında cached data gösterin
- Online olunca sync yapın

### 4. Performans
- Image'leri cache'leyin
- List view'lerde pagination kullanın
- Gereksiz API call'lardan kaçının

### 5. UI/UX
- Loading indicator'ları gösterin
- Hata mesajlarını kullanıcı dostu gösterin
- Success/error feedback'leri verin

---

## 🔗 Faydalı Linkler

- **API Interactive Docs:** http://13.60.31.19/docs
- **Frontend Demo:** http://13.60.31.19/

---

## 📞 İletişim

Sorularınız için:
- Backend Developer: [İletişim Bilgisi]
- API Issues: GitHub Issues

---

**Son Güncelleme:** 2025-10-23
**API Version:** 1.0.0
