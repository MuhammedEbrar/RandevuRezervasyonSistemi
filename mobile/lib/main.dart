// lib/main.dart (TEMA DESTEKLİ YENİ HALİ)

import 'package:flutter/material.dart';
import 'package:mobile/auth_page.dart';

// Tema değiştirme işlemini yönetmek için global bir değişken
final ValueNotifier<ThemeMode> themeNotifier = ValueNotifier(ThemeMode.light);

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // themeNotifier'daki değişikliği dinleyip uygulamayı yeniden çizer
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: themeNotifier,
      builder: (_, ThemeMode currentMode, __) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'Randevu Rezervasyon Sistemi',

          // Gündüz Modu Teması
          theme: ThemeData(
            brightness: Brightness.light,
            primarySwatch: Colors.teal,
            scaffoldBackgroundColor: Colors.grey[100],
            // Form elemanlarının tema ayarları
            inputDecorationTheme: InputDecorationTheme(
              filled: true,
              fillColor: Colors.white.withOpacity(0.8),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Colors.teal)),
            ),
            // İmleç rengini tema ile uyumlu yapıyoruz
            textSelectionTheme: const TextSelectionThemeData(
              cursorColor: Colors.teal,
            ),
          ),

          // Gece Modu Teması
          darkTheme: ThemeData(
            brightness: Brightness.dark,
            primarySwatch: Colors.teal,
            scaffoldBackgroundColor: const Color(0xff121212),
            // Gece modunda form elemanları
            inputDecorationTheme: InputDecorationTheme(
              filled: true,
              fillColor: Colors.black.withOpacity(0.3),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Colors.tealAccent)),
            ),
            // Gece modunda imleç rengi
            textSelectionTheme: const TextSelectionThemeData(
              cursorColor: Colors.tealAccent,
            ),
          ),

          // Hangi temanın aktif olacağını belirler
          themeMode: currentMode,

          home: const AuthPage(),
        );
      },
    );
  }
}