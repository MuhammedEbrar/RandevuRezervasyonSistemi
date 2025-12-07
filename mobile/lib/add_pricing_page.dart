// lib/add_pricing_page.dart

import 'package:flutter/material.dart';
import 'package:mobile/resource_service.dart';

class AddPricingPage extends StatefulWidget {
  final String resourceId;
  const AddPricingPage({super.key, required this.resourceId});

  @override
  State<AddPricingPage> createState() => _AddPricingPageState();
}

class _AddPricingPageState extends State<AddPricingPage> {
  final _resourceService = ResourceService();
  final _basePriceController = TextEditingController();
  final _minDurationController = TextEditingController();
  final _maxDurationController = TextEditingController();

  bool _isLoading = false;
  String _durationType =
      'PER_HOUR'; // FIXED, PER_HOUR, PER_DAY (Backend Enum'a göre)

  // Basitlik için tüm günler seçili varsayalım, detaylı checkbox listesi eklenebilir
  // Backend List<String>? applicableDays istiyor.

  @override
  void dispose() {
    _basePriceController.dispose();
    _minDurationController.dispose();
    _maxDurationController.dispose();
    super.dispose();
  }

  void _saveRule() async {
    if (_basePriceController.text.isEmpty) return;

    setState(() => _isLoading = true);

    bool success = await _resourceService.createPricingRule(
      resourceId: widget.resourceId,
      basePrice: double.tryParse(_basePriceController.text) ?? 0.0,
      durationType: _durationType,
      minDuration: int.tryParse(_minDurationController.text),
      maxDuration: int.tryParse(_maxDurationController.text),
      applicableDays:
          null, // Null gönderilirse backend muhtemelen tüm günler kabul eder veya iş mantığına bağlı
    );

    setState(() => _isLoading = false);

    if (success && mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Fiyat kuralı eklendi')));
      Navigator.pop(context, true);
    } else {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Hata oluştu')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Fiyatlandırma Kuralı Ekle')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextFormField(
              controller: _basePriceController,
              decoration: const InputDecoration(
                  labelText: 'Taban Fiyat (TL)', border: OutlineInputBorder()),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _durationType,
              decoration: const InputDecoration(
                  labelText: 'Fiyatlandırma Tipi',
                  border: OutlineInputBorder()),
              items: const [
                DropdownMenuItem(value: 'FIXED', child: Text('Sabit Fiyat')),
                DropdownMenuItem(value: 'PER_HOUR', child: Text('Saatlik')),
                DropdownMenuItem(value: 'PER_DAY', child: Text('Günlük')),
                DropdownMenuItem(value: 'PER_MINUTE', child: Text('Dakikalık')),
              ],
              onChanged: (val) => setState(() => _durationType = val!),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _minDurationController,
              decoration: const InputDecoration(
                  labelText: 'Min. Süre (Dakika) [Opsiyonel]',
                  hintText: 'Örn: 30',
                  border: OutlineInputBorder()),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _maxDurationController,
              decoration: const InputDecoration(
                  labelText: 'Max. Süre (Dakika) [Opsiyonel]',
                  hintText: 'Örn: 120',
                  border: OutlineInputBorder()),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 32),
            _isLoading
                ? const CircularProgressIndicator()
                : ElevatedButton(
                    onPressed: _saveRule,
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
