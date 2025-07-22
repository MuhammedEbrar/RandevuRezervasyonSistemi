// lib/my_bookings_page.dart (DÜZELTİLMİŞ VE İYİLEŞTİRİLMİŞ HALİ)

import 'package:flutter/material.dart';
import 'package:intl/intl.dart'; // Tarih formatlamak için
import 'package:mobile/auth_service.dart';

class MyBookingsPage extends StatefulWidget {
  const MyBookingsPage({super.key});

  @override
  State<MyBookingsPage> createState() => _MyBookingsPageState();
}

class _MyBookingsPageState extends State<MyBookingsPage> {
  final ResourceService _resourceService = ResourceService();
  late Future<List<dynamic>> _myBookingsFuture;

  @override
  void initState() {
    super.initState();
    _myBookingsFuture = _resourceService.getMyBookings();
  }

  // Duruma göre renk döndüren yardımcı bir fonksiyon
  Color _getStatusColor(String? status) {
    switch (status) {
      case 'CONFIRMED':
        return Colors.green;
      case 'PENDING':
        return Colors.orange;
      case 'CANCELLED':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  // Tarih formatlayan yardımcı bir fonksiyon
  String _formatDate(String? dateString) {
    if (dateString == null) return 'Tarih belirtilmemiş';
    try {
      final dateTime = DateTime.parse(dateString);
      // Örneğin: 17 Temmuz 2025, 14:00
      return DateFormat('d MMMM y, HH:mm', 'tr_TR').format(dateTime);
    } catch (e) {
      return dateString; // Formatlanamazsa orijinalini göster
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Rezervasyonlarım'),
        backgroundColor: Colors.blueGrey,
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _myBookingsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Rezervasyonlar yüklenirken bir hata oluştu: ${snapshot.error}'));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('Hiç rezervasyonunuz bulunmuyor.'));
          }

          final bookings = snapshot.data!;
          return ListView.builder(
            padding: const EdgeInsets.all(8.0),
            itemCount: bookings.length,
            itemBuilder: (context, index) {
              final booking = bookings[index];
              final status = booking['status'] as String?;
              
              // Backend'den 'resource' objesi içinde 'name' gelebilir, bu daha güvenli bir yoldur.
              final resourceName = booking['resource']?['name'] ?? 'Bilinmeyen Hizmet';

              return Card(
                elevation: 3,
                margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  leading: Icon(Icons.event_available, color: _getStatusColor(status), size: 40),
                  title: Text(
                    resourceName,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(
                    'Tarih: ${_formatDate(booking['start_time'])}\nDurum: ${status ?? 'Belirsiz'}',
                  ),
                  trailing: Text(
                    '${booking['total_price']} TL',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.teal),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}