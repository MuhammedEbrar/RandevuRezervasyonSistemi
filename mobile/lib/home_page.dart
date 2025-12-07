// lib/home_page.dart
// MODERN DASHBOARD TASARIMI ve ANIMASYONLU LOGIN SHEET (TEAL TEMA)

import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:mobile/auth_page.dart';
import 'package:mobile/explore_page.dart';
import 'package:mobile/my_bookings_page.dart';
import 'package:mobile/resource_list_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _storage = const FlutterSecureStorage();
  bool _isLoggedIn = false;

  @override
  void initState() {
    super.initState();
    _checkLoginStatus();
  }

  void _checkLoginStatus() async {
    String? token = await _storage.read(key: 'auth_token');
    setState(() {
      _isLoggedIn = token != null;
    });
  }

  void _logout() async {
    await _storage.delete(key: 'auth_token');
    setState(() {
      _isLoggedIn = false;
    });
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Başarıyla çıkış yapıldı.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    // Tema renklerini alalım
    final theme = Theme.of(context);
    final isDarkMode = theme.brightness == Brightness.dark;

    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          _buildAuthButtons(),
          const SizedBox(width: 20), // Kenardan boşluk
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // -----------------------------------------------------------------
            // 1. MODERN HEADER ALANI (Yeşil Gradient)
            // -----------------------------------------------------------------
            _buildHeader(theme, isDarkMode),

            // -----------------------------------------------------------------
            // 2. DASHBOARD GRID (Menü Kartları)
            // -----------------------------------------------------------------
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'İşlemler',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isDarkMode ? Colors.white : Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Grid Yapısı
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    childAspectRatio: 1.1,
                    children: [
                      _buildMenuCard(
                        title: 'Hizmetleri\nKeşfet',
                        icon: Icons.search_rounded,
                        color: Colors.deepOrangeAccent,
                        onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (context) => const ExplorePage())),
                      ),
                      _buildMenuCard(
                        title: 'Rezervasyonlarım',
                        icon: Icons.calendar_month_rounded,
                        color: Colors.blueAccent,
                        onTap: () {
                          if (_isLoggedIn) {
                            Navigator.push(
                                context,
                                MaterialPageRoute(
                                    builder: (context) =>
                                        const MyBookingsPage()));
                          } else {
                            _showLoginSheet();
                          }
                        },
                      ),
                      _buildMenuCard(
                        title: 'İşletme\nYönetimi',
                        icon: Icons.store_mall_directory_rounded,
                        color: Colors.teal,
                        onTap: () {
                          if (_isLoggedIn) {
                            Navigator.push(
                                context,
                                MaterialPageRoute(
                                    builder: (context) =>
                                        const ResourceListPage()));
                          } else {
                            _showLoginSheet();
                          }
                        },
                      ),
                      _buildMenuCard(
                        title: 'Profil\nAyarları',
                        icon: Icons.person_rounded,
                        color: Colors.purpleAccent,
                        onTap: () {
                          _showLoginSheet(
                              message:
                                  "Profil özellikleri yakında eklenecek. Lütfen giriş yapın.");
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAuthButtons() {
    if (_isLoggedIn) {
      return Center(
        child: Container(
          margin: const EdgeInsets.only(top: 10),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.25),
            borderRadius: BorderRadius.circular(30),
            border:
                Border.all(color: Colors.white.withOpacity(0.6), width: 1.5),
          ),
          child: InkWell(
            borderRadius: BorderRadius.circular(30),
            onTap: _logout,
            child: const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.logout_rounded, color: Colors.white, size: 20),
                  SizedBox(width: 8),
                  Text('Çıkış Yap',
                      style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 14)),
                ],
              ),
            ),
          ),
        ),
      );
    }

    return Center(
      child: Container(
        margin: const EdgeInsets.only(top: 10),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextButton(
              onPressed: () async {
                await Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) =>
                          const AuthPage(initialLoginView: true)),
                );
                _checkLoginStatus();
              },
              style: TextButton.styleFrom(
                foregroundColor: Colors.white,
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                  side: BorderSide(
                      color: Colors.white.withOpacity(0.7), width: 1.5),
                ),
              ),
              child: const Text('Giriş Yap',
                  style: TextStyle(fontWeight: FontWeight.bold)),
            ),
            const SizedBox(width: 12),
            ElevatedButton(
              onPressed: () async {
                await Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) =>
                          const AuthPage(initialLoginView: false)),
                );
                _checkLoginStatus();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: Colors.teal,
                padding:
                    const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
                elevation: 3,
              ),
              child: const Text('Kayıt Ol',
                  style: TextStyle(fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(ThemeData theme, bool isDarkMode) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(24, 100, 24, 40),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isDarkMode
              ? [
                  const Color(0xFF004D40),
                  const Color(0xFF111827)
                ] // Dark Teal -> Dark Gray
              : [
                  const Color(0xFF009688),
                  const Color(0xFF4DB6AC)
                ], // Teal -> Light Teal
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: const BorderRadius.only(
          bottomLeft: Radius.circular(32),
          bottomRight: Radius.circular(32),
        ),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF009688).withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(Icons.verified_user_rounded,
                color: Colors.white, size: 32),
          ),
          const SizedBox(height: 24),
          Text(
            _isLoggedIn ? 'Tekrar Hoşgeldin!' : 'Hoşgeldiniz,',
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 18,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Hizmetleri Keşfedin\nve Randevu Alın',
            style: TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
              height: 1.2,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuCard({
    required String title,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 32),
            ),
            const SizedBox(height: 16),
            Text(
              title,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // --- MODERN LOGIN SHEET (Bottom Sheet) ---
  void _showLoginSheet({String? message}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        decoration: BoxDecoration(
          color: Theme.of(context).scaffoldBackgroundColor,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withOpacity(0.2),
                blurRadius: 20,
                offset: const Offset(0, -5)),
          ],
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.lock_rounded,
                  size: 48, color: Theme.of(context).primaryColor),
            ),
            const SizedBox(height: 24),
            Text(
              'Giriş Yapmanız Gerekiyor',
              style: Theme.of(context)
                  .textTheme
                  .headlineSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              message ??
                  'Bu özelliğe erişmek ve devam etmek için lütfen oturum açın veya kayıt olun.',
              style: Theme.of(context)
                  .textTheme
                  .bodyMedium
                  ?.copyWith(color: Colors.grey),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  Navigator.push(
                          context,
                          MaterialPageRoute(
                              builder: (context) =>
                                  const AuthPage(initialLoginView: true)))
                      .then((_) => _checkLoginStatus());
                },
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                  elevation: 0,
                ),
                child: const Text('Giriş Yap / Kayıt Ol'),
              ),
            ),
            const SizedBox(height: 12),
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Şimdilik Vazgeç',
                  style: TextStyle(
                      color: Colors.grey, fontWeight: FontWeight.w600)),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
