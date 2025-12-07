// lib/resource_service.dart
// Bu servis sadece Resource ve Booking işlemleriyle ilgilenir.

import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';

class ResourceService {
  // Backend base URL (Android emulator için 10.0.2.2)
  final String _baseUrl = 'http://13.60.31.19/api/v1';
  final _storage = const FlutterSecureStorage();

  // Token'ı güvenli depolamadan alır
  Future<String?> _getToken() async {
    return await _storage.read(key: 'auth_token');
  }

  // --- RESOURCE (VARLIK) İŞLEMLERİ ---

  /// Kullanıcının rolüne göre kaynakları listeler.
  /// İşletme sahibi: Kendi kaynaklarını görür.
  /// Müşteri: Tüm aktif kaynakları görür.
  Future<List<dynamic>> getMyResources() async {
    final token = await _getToken();
    if (token == null) return []; // Token yoksa boş liste döndür

    final url = Uri.parse('$_baseUrl/resources/'); // GET /resources/
    try {
      final response = await http.get(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token', // Token'ı header'a ekle
        },
      );

      if (response.statusCode == 200) {
        return List<dynamic>.from(json.decode(response.body));
      } else {
        print(
            'Kaynaklar alınırken hata (getMyResources): ${response.statusCode} - ${response.body}');
        return [];
      }
    } catch (e) {
      print('API Hatası (getMyResources): $e');
      return [];
    }
  }

  /// Yeni bir kaynak (hizmet) oluşturur. (Sadece İşletme Sahibi)
  Future<bool> createResource(String name, String description,
      {int capacity = 1, int price = 0, int duration = 60}) async {
    final token = await _getToken();
    if (token == null) return false;

    final url = Uri.parse('$_baseUrl/resources/');
    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'name': name,
          'description': description,
          'capacity': capacity,
          'price': price, // Backend modeline uygun alanlar eklenebilir
          'duration_minutes': duration,
          // Diğer varsayılan alanlar backend'de ele alınıyor
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return true;
      } else {
        print(
            'Kaynak oluşturma hatası: ${response.statusCode} - ${response.body}');
        return false;
      }
    } catch (e) {
      print('API Hatası (createResource): $e');
      return false;
    }
  }

  /// Belirli bir kaynağın detaylarını getirir.
  Future<Map<String, dynamic>> getResourceById(String resourceId) async {
    final token =
        await _getToken(); // Public endpoint olsa da token varsa gönderelim
    // Auth gerektirmeyen bir endpoint ise token kontrolü zorunlu olmayabilir ama
    // user bağlamı için göndermek iyidir.

    final url = Uri.parse('$_baseUrl/resources/$resourceId');
    try {
      final headers = {'Content-Type': 'application/json'};
      if (token != null) {
        headers['Authorization'] = 'Bearer $token'; // 'Bearer ' formatı önemli
      }

      final response = await http.get(url, headers: headers);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print(
            'Kaynak detayı hatası: ${response.statusCode} - ${response.body}');
        return {};
      }
    } catch (e) {
      print('API Hatası (getResourceById): $e');
      return {};
    }
  }

  // --- MÜSAİTLİK VE REZERVASYON İŞLEMLERİ ---

  /// Belirli bir tarih aralığı için müsait saat dilimlerini getirir.
  /// Backend endpoint: GET /resources/{id}/availability/available_slots
  Future<List<dynamic>> getAvailableSlots(
      String resourceId, DateTime date) async {
    final token = await _getToken();
    if (token == null) return [];

    // Backend start_date ve end_date istiyor. Tek bir gün için her ikisi de aynı gün olabilir.
    final formattedDate = DateFormat('yyyy-MM-dd').format(date);

    // Query parametreleri ekleniyor
    final url = Uri.parse(
        '$_baseUrl/resources/$resourceId/availability/available_slots?start_date=$formattedDate&end_date=$formattedDate');

    try {
      final response = await http.get(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data; // Backend [{"start_time": "...", "end_time": "..."}] formatında dönüyor
      } else {
        print(
            'Müsaitlik alma hatası: ${response.statusCode} - ${response.body}');
        return [];
      }
    } catch (e) {
      print('API Hatası (getAvailableSlots): $e');
      return [];
    }
  }

  /// Rezervasyon fiyatını hesaplar.
  /// POST /bookings/calculate_price
  Future<String?> calculatePrice(
      String resourceId, String startTime, String endTime) async {
    final token = await _getToken();
    if (token == null) return null;

    final url = Uri.parse('$_baseUrl/bookings/calculate_price');
    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'resource_id': resourceId,
          'start_time': startTime, // ISO formatında olmalı
          'end_time': endTime, // ISO formatında olmalı
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['total_price'].toString();
      } else {
        print('Fiyat hesaplama hatası: ${response.body}');
        return null;
      }
    } catch (e) {
      print('API Hatası (calculatePrice): $e');
      return null;
    }
  }

  /// Yeni bir rezervasyon oluşturur.
  /// POST /bookings/
  Future<bool> createBooking({
    required String resourceId,
    required String startTime,
    required String endTime,
    // totalPrice genellikle backend'de tekrar hesaplanır ama frontend gönderiyorsa burada parametre olabilir
    String? totalPrice,
  }) async {
    final token = await _getToken();
    if (token == null) return false;

    final url = Uri.parse('$_baseUrl/bookings/');
    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'resource_id': resourceId,
          'start_time': startTime,
          'end_time': endTime,
          // 'total_price': ... // Backend CreateBooking şemasında varsa eklenebilir
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return true;
      } else {
        print(
            'Rezervasyon oluşturma hatası: ${response.statusCode} - ${response.body}');
        return false;
      }
    } catch (e) {
      print('API Hatası (createBooking): $e');
      return false;
    }
  }

  /// Müşterinin kendi rezervasyonlarını getirir.
  /// GET /bookings/customer
  Future<List<dynamic>> getMyBookings() async {
    final token = await _getToken();
    if (token == null) return [];

    final url = Uri.parse('$_baseUrl/bookings/customer');
    try {
      final response = await http.get(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return List<dynamic>.from(json.decode(response.body));
      } else {
        print(
            'Müşteri rezervasyonları hatası: ${response.statusCode} - ${response.body}');
        return [];
      }
    } catch (e) {
      print('API Hatası (getMyBookings): $e');
      return [];
    }
  }

  /// İşletme sahibine gelen rezervasyonları getirir.
  /// GET /bookings/owner
  Future<List<dynamic>> getOwnerBookings() async {
    final token = await _getToken();
    if (token == null) return [];

    final url = Uri.parse('$_baseUrl/bookings/owner');
    try {
      final response = await http.get(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return List<dynamic>.from(json.decode(response.body));
      } else {
        print(
            'İşletme rezervasyonları hatası: ${response.statusCode} - ${response.body}');
        return [];
      }
    } catch (e) {
      print('API Hatası (getOwnerBookings): $e');
      return [];
    }
  }
}
