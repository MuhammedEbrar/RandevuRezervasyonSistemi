// lib/resource_detail_page.dart

import 'package:flutter/material.dart';
import 'package:mobile/booking_success_page.dart';
import 'package:mobile/resource_service.dart';
import 'package:table_calendar/table_calendar.dart';

class ResourceDetailPage extends StatefulWidget {
  final String resourceId;
  const ResourceDetailPage({super.key, required this.resourceId});

  @override
  State<ResourceDetailPage> createState() => _ResourceDetailPageState();
}

class _ResourceDetailPageState extends State<ResourceDetailPage> {
  final ResourceService _resourceService = ResourceService();
  late Future<Map<String, dynamic>> _resourceFuture;
  Future<List<dynamic>>? _slotsFuture;
  String? _selectedSlot;
  String? _calculatedPrice;
  bool _isPriceLoading = false;
  bool _isBookingLoading = false;
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
      _selectedSlot = null;
      _calculatedPrice = null;
    });
  }

  void _onSlotSelected(String slot) async {
    setState(() {
      _selectedSlot = slot;
      _isPriceLoading = true;
      _calculatedPrice = null;
    });

    try {
      final startTime = "${_selectedDay!.toIso8601String().substring(0, 10)}T$slot:00";
      final endTime = "${_selectedDay!.toIso8601String().substring(0, 10)}T${int.parse(slot.substring(0, 2)) + 1}:00:00";
      final price = await _resourceService.calculatePrice(widget.resourceId, startTime, endTime);
      setState(() { _calculatedPrice = price; });
    } catch (e) {
      print(e);
      setState(() { _calculatedPrice = 'Hesaplanamadı'; });
    } finally {
      if(mounted) { setState(() { _isPriceLoading = false; }); }
    }
  }

  void _makeBooking() async {
    if (_selectedSlot == null || _calculatedPrice == null) return;
    setState(() { _isBookingLoading = true; });

    final startTime = "${_selectedDay!.toIso8601String().substring(0, 10)}T$_selectedSlot:00";
    final endTime = "${_selectedDay!.toIso8601String().substring(0, 10)}T${int.parse(_selectedSlot!.substring(0, 2)) + 1}:00:00";

    bool success = await _resourceService.createBooking(
      resourceId: widget.resourceId,
      startTime: startTime,
      endTime: endTime,
      totalPrice: _calculatedPrice!,
    );

    if(mounted) {
      setState(() { _isBookingLoading = false; });
      if (success) {
        Navigator.push(context, MaterialPageRoute(builder: (context) => const BookingSuccessPage()));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Rezervasyon oluşturulamadı.')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Varlık Detayı')),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _resourceFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
          if (snapshot.hasError) return Center(child: Text('Hata: ${snapshot.error}'));
          if (!snapshot.hasData || snapshot.data!.isEmpty) return const Center(child: Text('Varlık bulunamadı.'));

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
                  locale: 'tr_TR',
                  firstDay: DateTime.utc(2020, 1, 1),
                  lastDay: DateTime.utc(2030, 12, 31),
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
                    if (slotSnapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
                    if (slotSnapshot.hasError) return const Center(child: Text('Saatler getirilemedi.'));
                    if (!slotSnapshot.hasData || slotSnapshot.data!.isEmpty) return const Center(child: Text('Bu tarih için müsait saat bulunamadı.'));
                    final slots = slotSnapshot.data!;
                    return Wrap(
                      spacing: 8.0,
                      runSpacing: 4.0,
                      children: slots.map<Widget>((slot) {
                        final String currentSlot = slot.toString();
                        return ChoiceChip(
                          label: Text(currentSlot),
                          selectedColor: Colors.teal,
                          labelStyle: TextStyle(color: _selectedSlot == currentSlot ? Colors.white : Colors.black),
                          selected: _selectedSlot == currentSlot,
                          onSelected: (isSelected) {
                            if (isSelected) _onSlotSelected(currentSlot);
                          },
                        );
                      }).toList(),
                    );
                  },
                ),
                const SizedBox(height: 20),
                if (_isPriceLoading)
                  const Center(child: CircularProgressIndicator())
                else if (_calculatedPrice != null)
                  Center(
                    child: Column(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(color: Colors.teal.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
                          child: Text('Tahmini Fiyat: $_calculatedPrice TL', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.teal)),
                        ),
                        const SizedBox(height: 20),
                        _isBookingLoading
                          ? const CircularProgressIndicator()
                          : SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              onPressed: _makeBooking,
                              style: ElevatedButton.styleFrom(backgroundColor: Colors.orange.shade700, padding: const EdgeInsets.symmetric(vertical: 16), textStyle: const TextStyle(fontSize: 16)),
                              child: const Text('Rezervasyonu Onayla'),
                            ),
                          )
                      ],
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