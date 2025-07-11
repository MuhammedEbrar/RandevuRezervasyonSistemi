// lib/resource_list_page.dart (GÜNCELLENDİ)

import 'package:flutter/material.dart';
import 'package:mobile/add_resource_page.dart';
import 'package:mobile/resource_detail_page.dart'; // Detay sayfasını dahil ediyoruz
import 'package:mobile/resource_service.dart';

class ResourceListPage extends StatefulWidget {
  const ResourceListPage({super.key});

  @override
  State<ResourceListPage> createState() => _ResourceListPageState();
}

class _ResourceListPageState extends State<ResourceListPage> {
  final ResourceService _resourceService = ResourceService();
  late Future<List<dynamic>> _resourcesFuture;

  @override
  void initState() {
    super.initState();
    _resourcesFuture = _resourceService.getMyResources();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Hizmetlerim / Varlıklarım'),
        backgroundColor: Colors.blueGrey,
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
            itemCount: resources.length,
            itemBuilder: (context, index) {
              final resource = resources[index];
              final resourceId = resource['resource_id']; // ID'yi değişkene alıyoruz

              return ListTile(
                leading: const Icon(Icons.business_center_outlined),
                title: Text(resource['name'] ?? 'İsimsiz Varlık'),
                subtitle: Text(resource['description'] ?? 'Açıklama yok.'),
                trailing: const Icon(Icons.arrow_forward_ios),
                // TIKLAMA OLAYINI GÜNCELLİYORUZ
                onTap: () {
                  if (resourceId != null) {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => ResourceDetailPage(
                          resourceId: resourceId, // ID'yi detay sayfasına gönder
                        ),
                      ),
                    );
                  }
                },
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const AddResourcePage()),
          );
        },
        backgroundColor: Colors.blueGrey,
        child: const Icon(Icons.add),
      ),
    );
  }
}