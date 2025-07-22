// lib/resource_service.dart (İçinde hem Auth hem Resource servisi var)

import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

// ... (AuthService sınıfı aynı kalıyor) ...
class AuthService { /* ... */ }


class ResourceService {
  final String _baseUrl = 'http://10.0.2.2:8000';
  // ignore: unused_field
  final _storage = const FlutterSecureStorage();

  // ... (Diğer fonksiyonlar aynı kalıyor) ...
  Future<String?> _getToken() async { /* ... */ return null; }
  Future<List<dynamic>> getMyResources() async { /* ... */ return []; }
  Future<bool> createResource(String name, String description) async { /* ... */ return false; }
  Future<Map<String, dynamic>> getResourceById(String resourceId) async { /* ... */ return {}; }
  Future<List<dynamic>> getAvailableSlots(String resourceId, DateTime date) async { /* ... */ return []; }
  Future<String?> calculatePrice(String resourceId, String startTime, String endTime) async { /* ... */ return null; }

  // YENİ EKLENEN REZERVASYON FONKSİYONU
  Future<bool> createBooking({
    required String resourceId,
    required String startTime,
    required String endTime,
    required String totalPrice,
  }) async {
    final token = await _getToken();
    if (token == null) {
      print('Token bulunamadı.');
      return false;
    }
    
    // Proje planındaki POST /bookings adresini kullanıyoruz
    final url = Uri.parse('$_baseUrl/bookings');
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
          'total_price': double.tryParse(totalPrice) ?? 0.0, // Fiyatı sayıya çevir
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        print('Rezervasyon başarıyla oluşturuldu.');
        return true;
      } else {
        print('Rezervasyon oluşturulurken hata: ${response.body}');
        return false;
      }
    } catch (e) {
      print('API\'ye bağlanırken hata oluştu: $e');
      return false;
    }
  }
}