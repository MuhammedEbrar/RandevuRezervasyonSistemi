// lib/main.dart
// MODERN VE PROFESYONEL TEMA TASARIMI (TEAL / YEŞİL)

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:mobile/home_page.dart';

// Tema değiştirme işlemini yönetmek için global bir değişken
final ValueNotifier<ThemeMode> themeNotifier = ValueNotifier(ThemeMode.light);

void main() {
  // Status bar rengini şeffaf yapalım
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
  ));
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // -------------------------------------------------------------------------
    // RENK PALETİ (TEAL & GREEN)
    // -------------------------------------------------------------------------
    const primaryColor = Colors.teal; // Ana Renk
    const secondaryColor = Color(0xFF00796B); // Koyu Teal
    const accentColor = Color(0xFF4DB6AC); // Açık Teal
    const errorColor = Color(0xFFEF4444);

    // Gündüz Modu Arka Plan
    const scaffoldLight = Color(0xFFF0FDF9); // Mint/Teal tintli çok açık gri

    // Gece Modu Arka Plan
    const scaffoldDark = Color(0xFF111827); // Cool Gray 900

    return ValueListenableBuilder<ThemeMode>(
      valueListenable: themeNotifier,
      builder: (_, ThemeMode currentMode, __) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'Randevu Rezervasyon Sistemi',

          // -------------------------------------------------------------------
          // GÜNDÜZ MODU (LIGHT THEME)
          // -------------------------------------------------------------------
          theme: ThemeData(
            useMaterial3: true,
            brightness: Brightness.light,
            primaryColor: primaryColor,
            scaffoldBackgroundColor: scaffoldLight,

            // Renk Şeması
            colorScheme: ColorScheme.fromSeed(
              seedColor: primaryColor,
              primary: primaryColor,
              secondary: secondaryColor,
              error: errorColor,
              brightness: Brightness.light,
              surface: Colors.white,
            ),

            // AppBar Teması
            appBarTheme: const AppBarTheme(
              backgroundColor: primaryColor,
              foregroundColor: Colors.white,
              elevation: 0,
              centerTitle: true,
              titleTextStyle: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.5),
            ),

            // Kart Teması
            cardTheme: CardTheme(
              color: Colors.white,
              elevation: 2,
              shadowColor: Colors.teal.withOpacity(0.1),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16)),
              margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
            ),

            // Buton Teması (Elevated)
            elevatedButtonTheme: ElevatedButtonThemeData(
              style: ElevatedButton.styleFrom(
                backgroundColor: primaryColor,
                foregroundColor: Colors.white,
                elevation: 3,
                shadowColor: primaryColor.withOpacity(0.4),
                padding:
                    const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
                textStyle: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.5),
              ),
            ),

            // Input (TextFormField) Teması
            inputDecorationTheme: InputDecorationTheme(
              filled: true,
              fillColor: Colors.white,
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
              border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none),
              enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.grey.shade200)),
              focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: primaryColor, width: 2)),
              errorBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: errorColor)),
              labelStyle: TextStyle(
                  color: Colors.grey.shade600, fontWeight: FontWeight.w500),
              prefixIconColor: primaryColor,
            ),
          ),

          // -------------------------------------------------------------------
          // GECE MODU (DARK THEME)
          // -------------------------------------------------------------------
          darkTheme: ThemeData(
            useMaterial3: true,
            brightness: Brightness.dark,
            primaryColor: primaryColor,
            scaffoldBackgroundColor: scaffoldDark,
            colorScheme: ColorScheme.fromSeed(
              seedColor: primaryColor,
              primary: accentColor,
              secondary: primaryColor,
              error: errorColor,
              brightness: Brightness.dark,
              surface: const Color(0xFF1F2937),
            ),
            appBarTheme: const AppBarTheme(
              backgroundColor: Color(0xFF1F2937),
              foregroundColor: Colors.white,
              elevation: 0,
              centerTitle: true,
            ),
            cardTheme: CardTheme(
              color: const Color(0xFF1F2937),
              elevation: 4,
              shadowColor: Colors.black.withOpacity(0.3),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16)),
            ),
            elevatedButtonTheme: ElevatedButtonThemeData(
              style: ElevatedButton.styleFrom(
                backgroundColor: primaryColor,
                foregroundColor: Colors.white,
                padding:
                    const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
                textStyle:
                    const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
            ),
            inputDecorationTheme: InputDecorationTheme(
              filled: true,
              fillColor: const Color(0xFF374151),
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
              border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none),
              focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: accentColor)),
              labelStyle: const TextStyle(color: Colors.grey),
              prefixIconColor: accentColor,
            ),
          ),

          // Tema Modu
          themeMode: currentMode,
          home: const HomePage(),
        );
      },
    );
  }
}
