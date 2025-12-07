// lib/home_page.dart
// MODERN DASHBOARD TASARIMI ve ROL BAZLI GİRİŞ (TEAL TEMA)

import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:mobile/auth_page.dart';
import 'package:mobile/explore_page.dart';
import 'package:mobile/my_bookings_page.dart';
import 'package:mobile/resource_list_page.dart';
import 'package:mobile/owner_bookings_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _storage = const FlutterSecureStorage();
  bool _isLoggedIn = false;
  String? _userRole;

  @override
  void initState() {
    super.initState();
    _checkLoginStatus();
  }

  void _checkLoginStatus() async {
    String? token = await _storage.read(key: 'auth_token');
    String? role = await _storage.read(key: 'user_role');
    setState(() {
      _isLoggedIn = token != null;
      _userRole = role;
    });
  }

  void _logout() async {
    await _storage.delete(key: 'auth_token');
    await _storage.delete(key: 'user_role'); // Also clear role
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Başarıyla çıkış yapıldı.')),
      );
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(
            builder: (context) => const AuthPage(initialLoginView: true)),
        (route) => false,
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
            // 2. DASHBOARD GRID (Menü Kartları) veya ROL SEÇİMİ
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

                  // İçerik Alanı
                  _isLoggedIn
                      ? Column(
                          children: _userRole == 'BUSINESS_OWNER'
                              ? [
                                  // İŞLETME SAHİBİ MENÜSÜ
                                  _buildMenuCard(
                                    title: 'İşletme Yönetimi',
                                    icon: Icons.store_mall_directory_rounded,
                                    color: Colors.teal,
                                    onTap: () {
                                      Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                              builder: (context) =>
                                                  const ResourceListPage()));
                                    },
                                  ),
                                  const SizedBox(height: 16),
                                  _buildMenuCard(
                                    title: 'Gelen Talepler',
                                    icon: Icons.notifications_active_rounded,
                                    color: Colors.orange,
                                    onTap: () {
                                      Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                              builder: (context) =>
                                                  const OwnerBookingsPage()));
                                    },
                                  ),
                                ]
                              : [
                                  // MÜŞTERİ MENÜSÜ
                                  _buildMenuCard(
                                    title: 'Hizmetleri Keşfet',
                                    icon: Icons.search_rounded,
                                    color: Colors.deepOrangeAccent,
                                    onTap: () => Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                            builder: (context) =>
                                                const ExplorePage())),
                                  ),
                                  const SizedBox(height: 16),
                                  _buildMenuCard(
                                    title: 'Rezervasyonlarım',
                                    icon: Icons.calendar_month_rounded,
                                    color: Colors.blueAccent,
                                    onTap: () {
                                      Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                              builder: (context) =>
                                                  const MyBookingsPage()));
                                    },
                                  ),
                                ],
                        )
                      : _buildRoleSelectionCards(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAuthButtons() {
    return Center(
      child: Container(
        margin: const EdgeInsets.only(top: 10),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.25),
          borderRadius: BorderRadius.circular(30),
          border: Border.all(color: Colors.white.withOpacity(0.6), width: 1.5),
        ),
        child: _isLoggedIn
            ? InkWell(
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
              )
            : Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  InkWell(
                    borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(30),
                        bottomLeft: Radius.circular(30)),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) =>
                                const AuthPage(initialLoginView: true)),
                      ).then((_) => _checkLoginStatus());
                    },
                    child: const Padding(
                      padding:
                          EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: Text('Giriş Yap',
                          style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 14)),
                    ),
                  ),
                  Container(
                      width: 1,
                      height: 20,
                      color: Colors.white.withOpacity(0.5)),
                  InkWell(
                    borderRadius: const BorderRadius.only(
                        topRight: Radius.circular(30),
                        bottomRight: Radius.circular(30)),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) =>
                                const AuthPage(initialLoginView: false)),
                      ).then((_) => _checkLoginStatus());
                    },
                    child: const Padding(
                      padding:
                          EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: Text('Kayıt Ol',
                          style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 14)),
                    ),
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
              ? [const Color(0xFF004D40), const Color(0xFF111827)]
              : [const Color(0xFF009688), const Color(0xFF4DB6AC)],
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
          Text(
            _isLoggedIn
                ? 'Panelinizi Yönetin\nve İşlemleri Takip Edin'
                : 'Devam etmek için\nLütfen bir rol seçin',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 26,
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
        width: double.infinity,
        padding: const EdgeInsets.all(24),
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

  Widget _buildRoleSelectionCards() {
    return Column(
      children: [
        _buildRoleCard(
          title: 'MÜŞTERİ',
          description: 'Hizmetleri keşfet ve randevu al.',
          icon: Icons.person_outline_rounded,
          color: Colors.blue,
          isBusiness: false,
        ),
        const SizedBox(height: 16),
        _buildRoleCard(
          title: 'İŞ YERİ',
          description: 'İşletmeni yönet ve randevuları takip et.',
          icon: Icons.store_outlined,
          color: Colors.orange,
          isBusiness: true,
        ),
        const SizedBox(height: 24),
        TextButton(
          onPressed: () {
            Navigator.push(context,
                MaterialPageRoute(builder: (context) => const ExplorePage()));
          },
          child: const Text('Giriş yapmadan keşfet >>',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }

  Widget _buildRoleCard({
    required String title,
    required String description,
    required IconData icon,
    required Color color,
    required bool isBusiness,
  }) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => AuthPage(
              initialLoginView: false,
              initialIsBusiness: isBusiness,
            ),
          ),
        ).then((_) => _checkLoginStatus());
      },
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
          border: Border.all(color: color.withOpacity(0.3), width: 1),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 32),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: color)),
                  const SizedBox(height: 4),
                  Text(description,
                      style: TextStyle(fontSize: 14, color: Colors.grey[600])),
                ],
              ),
            ),
            Icon(Icons.arrow_forward_ios_rounded,
                color: Colors.grey[400], size: 16),
          ],
        ),
      ),
    );
  }
}
