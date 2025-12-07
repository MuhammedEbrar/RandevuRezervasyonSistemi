// lib/auth_service.dart

import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class AuthService {
  final String _baseUrl = 'http://10.0.2.2:8000/api/v1/auth';
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
          'email': email,
          'password': password,
          'first_name': firstName,
          'last_name': lastName,
          'phone_number': phone,
          'role': role,
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

        // Token'ı safe storage'a kaydet
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
