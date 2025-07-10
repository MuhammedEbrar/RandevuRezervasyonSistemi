// lib/resource_service.dart (GÜNCELLENDİ)


import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;


class ResourceService {
  final String _baseUrl = 'http://10.0.2.2:8000';
  final _storage = const FlutterSecureStorage();


  Future<String?> _getToken() async {
    return await _storage.read(key: 'auth_token');
  }


  Future<List<dynamic>> getMyResources() async {
    // Bu fonksiyon aynı kalıyor...
    final token = await _getToken();
    if (token == null) throw Exception('Token bulunamadı. Lütfen giriş yapın.');


    final url = Uri.parse('$_baseUrl/owner/resources');
    try {
      final response = await http.get(
        url,
        headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $token'},
      );
      if (response.statusCode == 200) return json.decode(response.body);
      throw Exception('Varlıkları getirirken hata: ${response.body}');
    } catch (e) {
      throw Exception('API\'ye bağlanırken hata oluştu: $e');
    }
  }


  // YENİ EKLENEN FONKSİYON
  Future<bool> createResource(String name, String description) async {
    final token = await _getToken();
    if (token == null) {
      print('Token bulunamadı.');
      return false;
    }


    final url = Uri.parse('$_baseUrl/resources'); // Proje planındaki POST adresi
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
          'type': 'SERVICE', // Örnek olarak varsayılan bir tip gönderiyoruz
        }),
      );


      if (response.statusCode == 200 || response.statusCode == 201) {
        print('Varlık başarıyla oluşturuldu.');
        return true;
      } else {
        print('Varlık oluştururken hata: ${response.body}');
        return false;
      }
    } catch (e) {
      print('API\'ye bağlanırken hata oluştu: $e');
      return false;
    }
  }
}

