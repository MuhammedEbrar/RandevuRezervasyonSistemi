// lib/owner_bookings_page.dart

import 'package:flutter/material.dart';
import 'package:mobile/resource_service.dart';

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
            return Center(
                child: Text(
                    'Rezervasyonlar yüklenirken bir hata oluştu: ${snapshot.error}'));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('Hiç rezervasyon bulunmuyor.'));
          }

          final bookings = snapshot.data!;
          return ListView.builder(
            itemCount: bookings.length,
            itemBuilder: (context, index) {
              final booking = bookings[index];
              final resourceName = booking['resource'] != null
                  ? booking['resource']['name'] as String
                  : 'Hizmet bilgisi yok';
              final status = booking['status'];
              final isPending = status == 'PENDING';

              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    children: [
                      ListTile(
                        leading: Icon(
                          status == 'PENDING'
                              ? Icons.hourglass_empty_rounded
                              : (status == 'CANCELLED' || status == 'REJECTED'
                                  ? Icons.cancel
                                  : Icons.check_circle_rounded),
                          color: status == 'PENDING'
                              ? Colors.orange
                              : (status == 'CANCELLED' || status == 'REJECTED'
                                  ? Colors.red
                                  : Colors.green),
                        ),
                        title: Text(resourceName,
                            style:
                                const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text(
                            'Müşteri ID: ${booking['customer_id']}\nTarih: ${booking['start_time']}'),
                        trailing: Text('${booking['total_price']} TL',
                            style: const TextStyle(
                                fontWeight: FontWeight.bold, fontSize: 16)),
                      ),
                      if (isPending)
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16.0),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.end,
                            children: [
                              OutlinedButton.icon(
                                onPressed: () async {
                                  final success = await _resourceService
                                      .updateBookingStatus(
                                          booking['booking_id'], 'CANCELLED');
                                  if (success) {
                                    if (mounted) {
                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(const SnackBar(
                                              content: Text(
                                                  'Rezervasyon reddedildi.')));
                                      // Listeyi yenile
                                      setState(() {
                                        _ownerBookingsFuture =
                                            _resourceService.getOwnerBookings();
                                      });
                                    }
                                  } else {
                                    if (mounted) {
                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(const SnackBar(
                                              content: Text(
                                                  'İşlem başarısız oldu.')));
                                    }
                                  }
                                },
                                icon:
                                    const Icon(Icons.close, color: Colors.red),
                                label: const Text('Reddet',
                                    style: TextStyle(color: Colors.red)),
                              ),
                              const SizedBox(width: 12),
                              ElevatedButton.icon(
                                onPressed: () async {
                                  final success = await _resourceService
                                      .updateBookingStatus(
                                          booking['booking_id'], 'CONFIRMED');
                                  if (success) {
                                    if (mounted) {
                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(const SnackBar(
                                              content: Text(
                                                  'Rezervasyon onaylandı!')));
                                      // Listeyi yenile
                                      setState(() {
                                        _ownerBookingsFuture =
                                            _resourceService.getOwnerBookings();
                                      });
                                    }
                                  } else {
                                    if (mounted) {
                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(const SnackBar(
                                              content: Text(
                                                  'İşlem başarısız oldu.')));
                                    }
                                  }
                                },
                                icon: const Icon(Icons.check,
                                    color: Colors.white),
                                label: const Text('Onayla'),
                                style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.green),
                              ),
                            ],
                          ),
                        ),
                    ],
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
