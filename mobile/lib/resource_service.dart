// lib/resource_service.dart
// Bu servis sadece Resource ve Booking işlemleriyle ilgilenir.

import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';

class ResourceService {
  // Backend base URL (Android emulator için 10.0.2.2, Web için localhost, Gerçek Cihaz için IP)
  final String _baseUrl = 'http://13.60.31.19/api/v1';
  final _storage = const FlutterSecureStorage();

  // Token'ı güvenli depolamadan alır
  Future<String?> _getToken() async {
    return await _storage.read(key: 'auth_token');
  }

  // --- RESOURCE (VARLIK) İŞLEMLERİ ---

  Future<List<dynamic>> getMyResources() async {
    final token = await _getToken();
    if (token == null) throw Exception("Oturum açılmamış.");

    final url = Uri.parse('$_baseUrl/resources/');
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
        // Hata detayını fırlat ki UI'da gözüksün
        final errorBody = utf8.decode(response.bodyBytes);
        throw Exception('${response.statusCode}: $errorBody');
      }
    } catch (e) {
      throw Exception('Bir hata oluştu: $e');
    }
  }

  /// Yeni bir kaynak (hizmet/mekan) oluşturur.
  Future<bool> createResource({
    required String name,
    required String description,
    required String type, // HIZMET veya MEKAN
    int? capacity,
    required Map<String, String> location, // address, city, country, zip_code
    List<String>? tags,
    List<String>? images,
    String? cancellationPolicy,
  }) async {
    final token = await _getToken();
    if (token == null) return false;

    final url = Uri.parse('$_baseUrl/resources/');
    try {
      final body = {
        'name': name,
        'description': description,
        'type': type,
        'capacity': capacity ?? 1,
        'location': location,
        'tags': tags ?? [],
        'images': images ?? [],
        'cancellation_policy': cancellationPolicy,
        // Varsayılan değerler
        'booking_type': type == 'MEKAN' ? 'DURATION_BASED' : 'SLOT_BASED',
      };

      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode(body),
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

  Future<Map<String, dynamic>> getResourceById(String resourceId) async {
    final token = await _getToken();
    final url = Uri.parse('$_baseUrl/resources/$resourceId');
    try {
      final headers = {'Content-Type': 'application/json'};
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
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

  // --- MÜSAİTLİK VE KURAL İŞLEMLERİ ---

  /// Yeni bir müsaitlik kuralı oluşturur via POST /resources/{id}/availability
  Future<bool> createAvailabilitySchedule({
    required String resourceId,
    required String dayOfWeek, // MONDAY, TUESDAY...
    required String startTime, // HH:MM
    required String endTime, // HH:MM
    String type = "REGULAR", // REGULAR veya EXCEPTION
    bool isAvailable = true,
  }) async {
    final token = await _getToken();
    if (token == null) return false;

    final url = Uri.parse('$_baseUrl/resources/$resourceId/availability/');
    try {
      final body = {
        'day_of_week': dayOfWeek,
        'start_time':
            startTime, // "09:00:00" formatında olabilir, backend parsing önemli
        'end_time': endTime,
        'type': type,
        'is_available': isAvailable,
      };

      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode(body),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return true;
      } else {
        print('Takvim kuralı oluşturma hatası: ${response.body}');
        return false;
      }
    } catch (e) {
      print('API Hatası (createAvailabilitySchedule): $e');
      return false;
    }
  }

  /// Yeni bir fiyatlandırma kuralı oluşturur via POST /resources/{id}/pricing
  Future<bool> createPricingRule({
    required String resourceId,
    required double basePrice,
    required String durationType, // FIXED, PER_HOUR, PER_DAY...
    int? minDuration,
    int? maxDuration,
    List<String>? applicableDays, // ["MONDAY", "FRIDAY"]
  }) async {
    final token = await _getToken();
    if (token == null) return false;

    final url = Uri.parse('$_baseUrl/resources/$resourceId/pricing/');
    try {
      final body = {
        'base_price': basePrice,
        'duration_type': durationType,
        'min_duration': minDuration,
        'max_duration': maxDuration,
        'applicable_days': applicableDays,
        'is_active': true
      };

      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode(body),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return true;
      } else {
        print('Fiyat kuralı oluşturma hatası: ${response.body}');
        return false;
      }
    } catch (e) {
      print('API Hatası (createPricingRule): $e');
      return false;
    }
  }

  Future<List<dynamic>> getAvailableSlots(
      String resourceId, DateTime date) async {
    final token = await _getToken();
    if (token == null) return [];

    final formattedDate = DateFormat('yyyy-MM-dd').format(date);
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
        return List<dynamic>.from(json.decode(response.body));
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }

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
          'start_time': startTime,
          'end_time': endTime,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['total_price'].toString();
      } else {
        return null;
      }
    } catch (e) {
      return null;
    }
  }

  Future<String?> createBooking({
    required String resourceId,
    required String startTime,
    required String endTime,
    String? totalPrice,
  }) async {
    final token = await _getToken();
    if (token == null) return "Oturum hatası. Lütfen tekrar giriş yapın.";

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
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return null; // Başarılı
      } else {
        // Backend'den gelen hata mesajını decode et
        try {
          final errorData = json.decode(utf8.decode(response.bodyBytes));
          return errorData['detail'] ??
              "Bir hata oluştu: ${response.statusCode}";
        } catch (_) {
          return "JSON Hatası: ${response.statusCode} - ${response.body}";
        }
      }
    } catch (e) {
      return "Bağlantı hatası: $e";
    }
  }

  Future<List<dynamic>> getMyBookings() async {
    final token = await _getToken();
    if (token == null) return [];

    final url = Uri.parse('$_baseUrl/bookings/customer');
    try {
      final response =
          await http.get(url, headers: {'Authorization': 'Bearer $token'});
      if (response.statusCode == 200)
        return List<dynamic>.from(json.decode(response.body));
      return [];
    } catch (e) {
      return [];
    }
  }

  Future<List<dynamic>> getOwnerBookings() async {
    final token = await _getToken();
    if (token == null) return [];

    final url = Uri.parse('$_baseUrl/bookings/owner');
    try {
      final response =
          await http.get(url, headers: {'Authorization': 'Bearer $token'});
      if (response.statusCode == 200)
        return List<dynamic>.from(json.decode(response.body));
      return [];
    } catch (e) {
      return [];
    }
  }
}
