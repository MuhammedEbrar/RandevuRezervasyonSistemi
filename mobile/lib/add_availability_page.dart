// lib/add_availability_page.dart

import 'package:flutter/material.dart';
import 'package:mobile/resource_service.dart';

class AddAvailabilityPage extends StatefulWidget {
  final String resourceId;
  const AddAvailabilityPage({super.key, required this.resourceId});

  @override
  State<AddAvailabilityPage> createState() => _AddAvailabilityPageState();
}

class _AddAvailabilityPageState extends State<AddAvailabilityPage> {
  final _resourceService = ResourceService();
  bool _isLoading = false;

  String _selectedDay = 'MONDAY';
  TimeOfDay _startTime = const TimeOfDay(hour: 9, minute: 0);
  TimeOfDay _endTime = const TimeOfDay(hour: 17, minute: 0);
  String _selectedType = 'REGULAR';
  bool _isAvailable = true;

  final List<String> _days = [
    'MONDAY',
    'TUESDAY',
    'WEDNESDAY',
    'THURSDAY',
    'FRIDAY',
    'SATURDAY',
    'SUNDAY'
  ];

  Future<void> _selectTime(bool isStart) async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: isStart ? _startTime : _endTime,
    );
    if (picked != null) {
      setState(() {
        if (isStart) {
          _startTime = picked;
        } else {
          _endTime = picked;
        }
      });
    }
  }

  String _formatTimeOfDay(TimeOfDay time) {
    final hour = time.hour.toString().padLeft(2, '0');
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute'; // HH:MM
  }

  void _saveSchedule() async {
    setState(() => _isLoading = true);

    bool success = await _resourceService.createAvailabilitySchedule(
      resourceId: widget.resourceId,
      dayOfWeek: _selectedDay,
      startTime: _formatTimeOfDay(_startTime),
      endTime: _formatTimeOfDay(_endTime),
      type: _selectedType,
      isAvailable: _isAvailable,
    );

    setState(() => _isLoading = false);

    if (success && mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Kural eklendi')));
      Navigator.pop(context, true); // true dönerse listeyi yeniletebiliriz
    } else {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Hata oluştu')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Müsaitlik Ekle / Düzenle')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            DropdownButtonFormField<String>(
              value: _selectedDay,
              decoration: const InputDecoration(labelText: 'Gün'),
              items: _days
                  .map((day) => DropdownMenuItem(value: day, child: Text(day)))
                  .toList(),
              onChanged: (val) => setState(() => _selectedDay = val!),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ListTile(
                    title: const Text('Başlangıç Saati'),
                    subtitle: Text(_formatTimeOfDay(_startTime)),
                    trailing: const Icon(Icons.access_time),
                    onTap: () => _selectTime(true),
                  ),
                ),
                Expanded(
                  child: ListTile(
                    title: const Text('Bitiş Saati'),
                    subtitle: Text(_formatTimeOfDay(_endTime)),
                    trailing: const Icon(Icons.access_time),
                    onTap: () => _selectTime(false),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _selectedType,
              decoration: const InputDecoration(labelText: 'Kural Tipi'),
              items: const [
                DropdownMenuItem(
                    value: 'REGULAR', child: Text('Düzenli (Haftalık)')),
                DropdownMenuItem(
                    value: 'EXCEPTION', child: Text('İstisna (Tek Seferlik)')),
              ],
              onChanged: (val) => setState(() => _selectedType = val!),
            ),
            SwitchListTile(
              title: const Text('Müsait mi?'),
              value: _isAvailable,
              onChanged: (val) => setState(() => _isAvailable = val),
            ),
            const Spacer(),
            _isLoading
                ? const CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _saveSchedule,
                    style: ElevatedButton.styleFrom(
                        minimumSize: const Size(double.infinity, 50)),
                    child: const Text('Kaydet'),
                  ),
          ],
        ),
      ),
    );
  }
}
