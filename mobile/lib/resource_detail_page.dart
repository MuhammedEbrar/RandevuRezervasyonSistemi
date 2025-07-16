// lib/resource_detail_page.dart (GÜNCELLENDİ)

import 'package:flutter/material.dart';
import 'package:mobile/resource_service.dart';
import 'package:table_calendar/table_calendar.dart';

class ResourceDetailPage extends StatefulWidget {
  final String resourceId;

  const ResourceDetailPage({
    super.key,
    required this.resourceId,
  });

  @override
  State<ResourceDetailPage> createState() => _ResourceDetailPageState();
}

class _ResourceDetailPageState extends State<ResourceDetailPage> {
  final ResourceService _resourceService = ResourceService();
  late Future<Map<String, dynamic>> _resourceFuture;
  Future<List<dynamic>>? _slotsFuture;
  
  // Yeni durum değişkenleri
  String? _selectedSlot; // Seçili saati tutar
  String? _calculatedPrice; // Hesaplanan fiyatı tutar
  bool _isPriceLoading = false; // Fiyat hesaplanırken animasyon göstermek için

  DateTime _focusedDay = DateTime.now();
  DateTime? _selectedDay;

  @override
  void initState() {
    super.initState();
    _resourceFuture = _resourceService.getResourceById(widget.resourceId);
    _selectedDay = _focusedDay;
    _fetchSlots(_selectedDay!);
  }

  void _fetchSlots(DateTime date) {
    setState(() {
      _slotsFuture = _resourceService.getAvailableSlots(widget.resourceId, date);
      // Yeni tarih seçildiğinde eski seçimleri ve fiyatı sıfırla
      _selectedSlot = null;
      _calculatedPrice = null;
    });
  }

  void _onSlotSelected(String slot) async {
    setState(() {
      _selectedSlot = slot;
      _isPriceLoading = true; // Fiyat yükleniyor...
      _calculatedPrice = null; // Eski fiyatı temizle
    });

    try {
      // Not: Bu kısım backend'den gelen slot formatına göre uyarlanmalıdır.
      // Örnek olarak slot "14:00" formatında ve randevu 1 saat sürüyor varsayalım.
      final startTime = "${_selectedDay!.toIso8601String().substring(0, 10)}T$slot:00";
      final endTime = "${_selectedDay!.toIso8601String().substring(0, 10)}T${int.parse(slot.substring(0, 2)) + 1}:00:00";
      
      final price = await _resourceService.calculatePrice(widget.resourceId, startTime, endTime);
      setState(() {
        _calculatedPrice = price;
      });
    } catch (e) {
      print(e);
      setState(() {
        _calculatedPrice = 'Hesaplanamadı';
      });
    } finally {
      setState(() {
        _isPriceLoading = false; // Yükleme bitti.
      });
    }
  }


  @override
  Widget build(BuildContext context) {
    // ... Scaffold ve ilk FutureBuilder aynı kalıyor ...
    return Scaffold(
        appBar: AppBar(title: const Text('Varlık Detayı')),
        body: FutureBuilder<Map<String, dynamic>>(
            future: _resourceFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) return Center(child: Text('Hata: ${snapshot.error}'));
              if (!snapshot.hasData) return const Center(child: Text('Varlık bulunamadı.'));

              final resource = snapshot.data!;
              return SingleChildScrollView(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(resource['name'] ?? 'İsimsiz Varlık', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        Text(resource['description'] ?? 'Açıklama mevcut değil.', style: TextStyle(fontSize: 16, color: Colors.grey[700])),
                        const Divider(height: 40, thickness: 1),
                        TableCalendar(
                          firstDay: DateTime.now().subtract(const Duration(days: 365)),
                          lastDay: DateTime.now().add(const Duration(days: 365)),
                          focusedDay: _focusedDay,
                          selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
                          onDaySelected: (selectedDay, focusedDay) {
                            setState(() {
                              _selectedDay = selectedDay;
                              _focusedDay = focusedDay;
                              _fetchSlots(selectedDay);
                            });
                          },
                        ),
                        const Divider(height: 40, thickness: 1),
                        FutureBuilder<List<dynamic>>(
                          future: _slotsFuture,
                          builder: (context, slotSnapshot) {
                            if (slotSnapshot.connectionState == ConnectionState.waiting) {
                              return const Center(child: CircularProgressIndicator());
                            }
                            if (slotSnapshot.hasError) return const Center(child: Text('Saatler getirilemedi.'));
                            if (!slotSnapshot.hasData || slotSnapshot.data!.isEmpty) {
                              return const Center(child: Text('Bu tarih için müsait saat bulunamadı.'));
                            }
                            final slots = slotSnapshot.data!;
                            return Wrap(
                              spacing: 8.0,
                              runSpacing: 8.0,
                              children: slots.map<Widget>((slot) {
                                final String currentSlot = slot.toString();
                                return ChoiceChip(
                                  label: Text(currentSlot),
                                  selected: _selectedSlot == currentSlot,
                                  onSelected: (isSelected) {
                                    if (isSelected) {
                                      _onSlotSelected(currentSlot);
                                    }
                                  },
                                );
                              }).toList(),
                            );
                          },
                        ),
                        const SizedBox(height: 20),
                        // FİYATI GÖSTERME BÖLÜMÜ
                        if (_isPriceLoading)
                          const Center(child: CircularProgressIndicator())
                        else if (_calculatedPrice != null)
                          Center(
                            child: Text(
                              'Tahmini Fiyat: $_calculatedPrice TL',
                              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.teal),
                            ),
                          )
                      ],
                  ),
              );
            },
        ),
    );
  }
}