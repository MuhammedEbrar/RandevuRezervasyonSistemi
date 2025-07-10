// lib/auth_service.dart (GÜNCELLENDİ)


import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;


class AuthService {
  final String _baseUrl = 'http://10.0.2.2:8000/auth';
  // Güvenli depolama için bir nesne oluşturuyoruz
  final _storage = const FlutterSecureStorage();


  Future<void> register(String email, String password) async {
    // Register fonksiyonu aynı kalıyor...
    final url = Uri.parse('$_baseUrl/register');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'email': email, 'password': password}),
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


  // Fonksiyonu artık bool (true/false) döndürecek şekilde güncelliyoruz
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


        // Gelen token'ı güvenli depoya kaydediyoruz
        await _storage.write(key: 'auth_token', value: token);
        print('Giriş başarılı ve token kaydedildi.');
        return true; // İşlem başarılı olduğu için true döndürüyoruz
      } else {
        print('Giriş başarısız: ${response.body}');
        return false; // Başarısız olduğu için false döndürüyoruz
      }
    } catch (e) {
      print('API\'ye bağlanırken hata oluştu: $e');
      return false;
    }
  }
}
