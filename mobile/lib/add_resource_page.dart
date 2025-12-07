// lib/add_resource_page.dart

import 'package:flutter/material.dart';
import 'package:mobile/resource_service.dart';

class AddResourcePage extends StatefulWidget {
  const AddResourcePage({super.key});

  @override
  State<AddResourcePage> createState() => _AddResourcePageState();
}

class _AddResourcePageState extends State<AddResourcePage> {
  final _formKey = GlobalKey<FormState>();

  // Controllers
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _capacityController = TextEditingController(text: '1');

  // Location Controllers
  final _addressController = TextEditingController();
  final _cityController = TextEditingController();
  final _countryController = TextEditingController();
  final _zipCodeController = TextEditingController();

  // Other Controllers
  final _tagsController = TextEditingController();
  final _imagesController = TextEditingController();
  final _cancelPolicyController = TextEditingController();

  // State Variables
  String _selectedType = 'HIZMET';
  bool _isLoading = false;
  final _resourceService = ResourceService();

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _capacityController.dispose();
    _addressController.dispose();
    _cityController.dispose();
    _countryController.dispose();
    _zipCodeController.dispose();
    _tagsController.dispose();
    _imagesController.dispose();
    _cancelPolicyController.dispose();
    super.dispose();
  }

  void _saveResource() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    // Listeleri hazırla
    List<String> tags = _tagsController.text
        .split(',')
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();
    List<String> images = _imagesController.text
        .split(',')
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();

    bool success = await _resourceService.createResource(
      name: _nameController.text,
      description: _descriptionController.text,
      type: _selectedType,
      capacity: _selectedType == 'MEKAN'
          ? int.tryParse(_capacityController.text)
          : null,
      location: {
        'address': _addressController.text,
        'city': _cityController.text,
        'country': _countryController.text,
        'zip_code': _zipCodeController.text,
      },
      tags: tags,
      images: images,
      cancellationPolicy: _cancelPolicyController.text.isNotEmpty
          ? _cancelPolicyController.text
          : null,
    );

    setState(() => _isLoading = false);

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Varlık başarıyla oluşturuldu')));
      Navigator.pop(context);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('Varlık oluşturulamadı, lütfen tekrar deneyin')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Yeni Varlık Ekle'),
        backgroundColor: Colors.blueGrey,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSectionTitle('Temel Bilgiler'),
                    TextFormField(
                      controller: _nameController,
                      decoration: const InputDecoration(
                          labelText: 'Varlık Adı',
                          border: OutlineInputBorder()),
                      validator: (value) => value == null || value.isEmpty
                          ? 'Lütfen bir isim girin'
                          : null,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _descriptionController,
                      decoration: const InputDecoration(
                          labelText: 'Açıklama', border: OutlineInputBorder()),
                      maxLines: 3,
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      value: _selectedType,
                      decoration: const InputDecoration(
                          labelText: 'Varlık Tipi',
                          border: OutlineInputBorder()),
                      items: const [
                        DropdownMenuItem(
                            value: 'HIZMET', child: Text('Hizmet (HIZMET)')),
                        DropdownMenuItem(
                            value: 'MEKAN', child: Text('Mekan (MEKAN)')),
                      ],
                      onChanged: (value) {
                        if (value != null)
                          setState(() => _selectedType = value);
                      },
                    ),
                    if (_selectedType == 'MEKAN') ...[
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _capacityController,
                        decoration: const InputDecoration(
                            labelText: 'Kapasite',
                            border: OutlineInputBorder()),
                        keyboardType: TextInputType.number,
                      ),
                    ],
                    const SizedBox(height: 24),
                    _buildSectionTitle('Konum Bilgileri'),
                    TextFormField(
                      controller: _addressController,
                      decoration: const InputDecoration(
                          labelText: 'Adres', border: OutlineInputBorder()),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _cityController,
                            decoration: const InputDecoration(
                                labelText: 'Şehir',
                                border: OutlineInputBorder()),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: TextFormField(
                            controller: _countryController,
                            decoration: const InputDecoration(
                                labelText: 'Ülke',
                                border: OutlineInputBorder()),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _zipCodeController,
                      decoration: const InputDecoration(
                          labelText: 'Posta Kodu',
                          border: OutlineInputBorder()),
                    ),
                    const SizedBox(height: 24),
                    _buildSectionTitle('Diğer Detaylar'),
                    TextFormField(
                      controller: _tagsController,
                      decoration: const InputDecoration(
                        labelText: 'Etiketler (Virgülle ayırın)',
                        hintText: 'spor, pilates, havuz',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _imagesController,
                      decoration: const InputDecoration(
                        labelText: 'Resim URL\'leri (Virgülle ayırın)',
                        hintText: 'https://site.com/resim1.jpg',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _cancelPolicyController,
                      decoration: const InputDecoration(
                        labelText: 'İptal Politikası',
                        border: OutlineInputBorder(),
                      ),
                      maxLines: 2,
                    ),
                    const SizedBox(height: 32),
                    ElevatedButton(
                      onPressed: _saveResource,
                      style: ElevatedButton.styleFrom(
                        minimumSize: const Size(double.infinity, 50),
                        backgroundColor: Colors.blueGrey,
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('Kaydet'),
                    ),
                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.blueGrey)),
          const Divider(),
        ],
      ),
    );
  }
}
