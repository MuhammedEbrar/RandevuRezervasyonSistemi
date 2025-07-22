// lib/auth_service.dart

import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';

class AuthService {
  final String _baseUrl = 'http://10.0.2.2:8000/auth';
  final _storage = const FlutterSecureStorage();

  Future<void> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required String phone,
    required String role,
  }) async {
    final url = Uri.parse('$_baseUrl/register');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email, 'password': password, 'first_name': firstName, 'last_name': lastName, 'phone_number': phone, 'role': role,
        }),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        print('Kayıt başarılı!');
      } else {
        print('Kayıt başarısız: ${response.body}');
      }
    } catch (e) {
      print('API\'ye bağlanırken hata oluştu: $e');
    }
  }

  Future<bool> login(String email, String password) async {
    final url = Uri.parse('$_baseUrl/login');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'email': email, 'password': password}),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final token = data['access_token'];
        await _storage.write(key: 'auth_token', value: token);
        return true;
      } else {
        return false;
      }
    } catch (e) {
      return false;
    }
  }
}

class ResourceService {
  final String _baseUrl = 'https://api.gerceksunucu.com'; 
  final _storage = const FlutterSecureStorage();

  Future<String?> _getToken() async {
    return await _storage.read(key: 'auth_token');
  }

  Future<List<dynamic>> getMyResources() async {
    final token = await _getToken();
    if (token == null) throw Exception('Token bulunamadı.');
    final url = Uri.parse('$_baseUrl/owner/resources');
    final response = await http.get(url, headers: {'Authorization': 'Bearer $token'});
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Varlıkları getirirken hata: ${response.body}');
  }

  Future<Map<String, dynamic>> getResourceById(String resourceId) async {
    final token = await _getToken();
    if (token == null) throw Exception('Token bulunamadı.');
    final url = Uri.parse('$_baseUrl/resources/$resourceId');
    final response = await http.get(url, headers: {'Authorization': 'Bearer $token'});
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Varlık detayı getirilirken hata: ${response.body}');
  }

  Future<List<dynamic>> getAvailableSlots(String resourceId, DateTime date) async {
    final token = await _getToken();
    if (token == null) throw Exception('Token bulunamadı.');
    final formattedDate = DateFormat('yyyy-MM-dd').format(date);
    final url = Uri.parse('$_baseUrl/resources/$resourceId/available_slots?date=$formattedDate');
    final response = await http.get(url, headers: {'Authorization': 'Bearer $token'});
    if (response.statusCode == 200) return json.decode(response.body);
    throw Exception('Müsait saatler getirilirken hata: ${response.body}');
  }

  Future<String?> calculatePrice(String resourceId, String startTime, String endTime) async {
    final token = await _getToken();
    if (token == null) throw Exception('Token bulunamadı.');
    final url = Uri.parse('$_baseUrl/bookings/calculate_price');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $token'},
      body: json.encode({'resource_id': resourceId, 'start_time': startTime, 'end_time': endTime}),
    );
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['total_price'].toString();
    }
    throw Exception('Fiyat hesaplanırken hata: ${response.body}');
  }

  Future<bool> createBooking({ required String resourceId, required String startTime, required String endTime, required String totalPrice }) async {
    final token = await _getToken();
    if (token == null) return false;
    final url = Uri.parse('$_baseUrl/bookings');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $token'},
        body: json.encode({'resource_id': resourceId, 'start_time': startTime, 'end_time': endTime, 'total_price': double.tryParse(totalPrice) ?? 0.0}),
      );
      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }

  Future<List<dynamic>> getMyBookings() async {
    final token = await _getToken();
    if (token == null) throw Exception('Token bulunamadı.');
    final url = Uri.parse('$_baseUrl/customer/bookings');
    try {
      final response = await http.get(url, headers: {'Authorization': 'Bearer $token'});
      if (response.statusCode == 200) return json.decode(response.body);
      throw Exception('Rezervasyonlar getirilirken hata: ${response.body}');
    } catch (e) {
      throw Exception('API\'ye bağlanırken hata oluştu: $e');
    }
  }

  // YENİ EKLENEN FONKSİYON
  Future<List<dynamic>> getOwnerBookings() async {
    final token = await _getToken();
    if (token == null) throw Exception('Token bulunamadı.');
    final url = Uri.parse('$_baseUrl/owner/bookings');
    try {
      final response = await http.get(url, headers: {'Authorization': 'Bearer $token'});
      if (response.statusCode == 200) return json.decode(response.body);
      throw Exception('İşletme rezervasyonları getirilirken hata: ${response.body}');
    } catch (e) {
      throw Exception('API\'ye bağlanırken hata oluştu: $e');
    }
  }
}