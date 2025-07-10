// lib/add_resource_page.dart (GÜNCELLENDİ)


import 'package:flutter/material.dart';
import 'package:mobile/resource_service.dart'; // Servisi dahil ediyoruz


class AddResourcePage extends StatefulWidget {
  const AddResourcePage({super.key});


  @override
  State<AddResourcePage> createState() => _AddResourcePageState();
}


class _AddResourcePageState extends State<AddResourcePage> {
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _resourceService = ResourceService(); // Servisi oluşturuyoruz
  bool _isLoading = false; // Yükleme durumunu takip etmek için


  void _saveResource() async {
    if (_nameController.text.isEmpty) {
      // Basit bir kontrol
      print("Varlık adı boş olamaz.");
      return;
    }


    setState(() {
      _isLoading = true; // Yükleme animasyonunu başlat
    });


    bool success = await _resourceService.createResource(
      _nameController.text,
      _descriptionController.text,
    );


    setState(() {
      _isLoading = false; // Yükleme animasyonunu bitir
    });


    if (success && mounted) {
      // Başarılı olursa bir önceki sayfaya geri dön
      Navigator.pop(context);
    } else {
      // Başarısız olursa kullanıcıya bir uyarı gösterilebilir
      print("Varlık oluşturulamadı.");
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Yeni Varlık Ekle'),
        backgroundColor: Colors.blueGrey,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: 'Varlık Adı', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(labelText: 'Açıklama', border: OutlineInputBorder()),
              maxLines: 4,
            ),
            const SizedBox(height: 24),
            // Yükleme durumuna göre ya buton ya da animasyon göster
            _isLoading
                ? const CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _saveResource, // Kaydetme fonksiyonunu bağlıyoruz
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 50),
                      backgroundColor: Colors.blueGrey,
                    ),
                    child: const Text('Kaydet'),
                  ),
          ],
        ),
      ),
    );
  }
}
