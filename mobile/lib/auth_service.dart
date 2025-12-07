// lib/auth_service.dart

import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class AuthService {
  // Lütfen buraya bilgisayarınızın IP adresini yazın (Örn: 192.168.1.35)
  // Terminalde 'ipconfig' yazarak IPv4 adresinizi öğrenebilirsiniz.
  final String _baseUrl = 'http://13.60.31.19/api/v1/auth';

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
      final response = await http
          .post(
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
          )
          .timeout(const Duration(seconds: 30));
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
      // Backend OAuth2PasswordRequestForm bekliyor (form-data formatı)
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': email, // OAuth2 standardı 'username' field'ı kullanır
          'password': password,
        },
      ).timeout(const Duration(seconds: 30));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final token = data['access_token'];
        final user = data['user'];

        // Token ve kullanıcı bilgilerini safe storage'a kaydet
        await _storage.write(key: 'auth_token', value: token);
        if (user != null) {
          await _storage.write(key: 'user_id', value: user['user_id']);
          await _storage.write(key: 'user_role', value: user['role']);
        }
        return true;
      } else {
        print('Login başarısız: ${response.statusCode} - ${response.body}');
        return false;
      }
    } catch (e) {
      print('Login hatası: $e');
      return false;
    }
  }
}
