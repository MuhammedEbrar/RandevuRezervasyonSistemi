// lib/resource_service.dart (GÜNCELLENDİ)

import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
// ignore: unused_import
import 'package:intl/intl.dart';

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

  // YENİ EKLENEN FONKSİYON
  Future<String?> calculatePrice(String resourceId, String startTime, String endTime) async {
    final token = await _getToken();
    if (token == null) throw Exception('Token bulunamadı.');

    // Proje planındaki API adresini kullanıyoruz: /bookings/calculate_price
    final url = Uri.parse('$_baseUrl/bookings/calculate_price');
    try {
      final response = await http.post( // Genellikle bu tür istekler POST olur
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
        return data['total_price'].toString(); // Backend'den gelen fiyatı string olarak döndür
      } else {
        throw Exception('Fiyat hesaplanırken hata: ${response.body}');
      }
    } catch (e) {
      throw Exception('API\'ye bağlanırken hata oluştu: $e');
    }
  }
}