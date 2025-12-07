// lib/explore_page.dart

import 'package:flutter/material.dart';
import 'package:mobile/resource_detail_page.dart';
import 'package:mobile/resource_service.dart';

class ExplorePage extends StatefulWidget {
  const ExplorePage({super.key});

  @override
  State<ExplorePage> createState() => _ExplorePageState();
}

class _ExplorePageState extends State<ExplorePage> {
  final ResourceService _resourceService = ResourceService();
  late Future<List<dynamic>> _resourcesFuture;

  @override
  void initState() {
    super.initState();
    // Sayfa açıldığında bütün kaynakları getiren fonksiyonumuzu çağırıyoruz
    // getMyResources fonksiyonu kullanıcı rolüne göre (CUSTOMER ise hepsi, BUSINESS ise kendisininki) kaynakları getirir.
    _resourcesFuture = _resourceService.getMyResources();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Hizmetleri Keşfet'),
        backgroundColor: Colors.teal,
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _resourcesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Bir hata oluştu: ${snapshot.error}'));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('Gösterilecek hizmet bulunamadı.'));
          }

          final resources = snapshot.data!;
          return ListView.builder(
            padding: const EdgeInsets.all(8.0),
            itemCount: resources.length,
            itemBuilder: (context, index) {
              final resource = resources[index];
              final resourceId = resource['resource_id'];

              return Card(
                elevation: 4,
                margin: const EdgeInsets.symmetric(vertical: 8.0),
                child: ListTile(
                  contentPadding: const EdgeInsets.all(12.0),
                  leading:
                      const Icon(Icons.store, color: Colors.teal, size: 40),
                  title: Text(
                    resource['name'] ?? 'İsimsiz Hizmet',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(resource['description'] ?? 'Açıklama yok.'),
                  trailing: const Icon(Icons.arrow_forward_ios),
                  onTap: () {
                    if (resourceId != null) {
                      // Kullanıcı bir hizmete tıkladığında, mevcut detay sayfasına yönlendiriyoruz
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => ResourceDetailPage(
                              resourceId: resourceId.toString()),
                        ),
                      );
                    }
                  },
                ),
              );
            },
          );
        },
      ),
    );
  }
}
