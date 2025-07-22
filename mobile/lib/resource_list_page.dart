// lib/resource_list_page.dart

import 'package:flutter/material.dart';
import 'package:mobile/add_resource_page.dart';
import 'package:mobile/owner_bookings_page.dart';
import 'package:mobile/resource_detail_page.dart';
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
      body: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          children: [
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.list_alt),
                label: const Text('Gelen Rezervasyonları Görüntüle'),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const OwnerBookingsPage()),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepOrangeAccent,
                  foregroundColor: Colors.white
                ),
              ),
            ),
            const Divider(),
            Expanded(
              child: FutureBuilder<List<dynamic>>(
                future: _resourcesFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
                  if (snapshot.hasError) return Center(child: Text('Bir hata oluştu: ${snapshot.error}'));
                  if (!snapshot.hasData || snapshot.data!.isEmpty) return const Center(child: Text('Gösterilecek hizmet bulunamadı.'));
                  
                  final resources = snapshot.data!;
                  return ListView.builder(
                    itemCount: resources.length,
                    itemBuilder: (context, index) {
                      final resource = resources[index];
                      final resourceId = resource['resource_id'];
                      return Card(
                        child: ListTile(
                          leading: const Icon(Icons.business_center_outlined),
                          title: Text(resource['name'] ?? 'İsimsiz Varlık'),
                          subtitle: Text(resource['description'] ?? 'Açıklama yok.'),
                          trailing: const Icon(Icons.arrow_forward_ios),
                          onTap: () {
                            if (resourceId != null) {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => ResourceDetailPage(resourceId: resourceId),
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
            ),
          ],
        ),
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