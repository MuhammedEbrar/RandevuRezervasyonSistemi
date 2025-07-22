// lib/owner_bookings_page.dart

import 'package:flutter/material.dart';
import 'package:mobile/auth_service.dart';

class OwnerBookingsPage extends StatefulWidget {
  const OwnerBookingsPage({super.key});

  @override
  State<OwnerBookingsPage> createState() => _OwnerBookingsPageState();
}

class _OwnerBookingsPageState extends State<OwnerBookingsPage> {
  final ResourceService _resourceService = ResourceService();
  late Future<List<dynamic>> _ownerBookingsFuture;

  @override
  void initState() {
    super.initState();
    _ownerBookingsFuture = _resourceService.getOwnerBookings();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Gelen Rezervasyonlar'),
        backgroundColor: Colors.blueGrey,
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _ownerBookingsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Rezervasyonlar yüklenirken bir hata oluştu: ${snapshot.error}'));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('Hiç rezervasyon bulunmuyor.'));
          }

          final bookings = snapshot.data!;
          return ListView.builder(
            itemCount: bookings.length,
            itemBuilder: (context, index) {
              final booking = bookings[index];
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: ListTile(
                  leading: const Icon(Icons.receipt_long, color: Colors.orange),
                  title: Text(booking['resource_name'] ?? 'Bilinmeyen Hizmet', style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text('Müşteri ID: ${booking['customer_id']}\nTarih: ${booking['start_time']}'),
                  trailing: Text('${booking['total_price']} TL'),
                ),
              );
            },
          );
        },
      ),
    );
  }
}