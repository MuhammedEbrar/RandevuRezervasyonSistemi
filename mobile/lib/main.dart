// lib/main.dart (GÜNCELLENDİ)


import 'package:flutter/material.dart';
import 'package:mobile/splash_screen.dart'; // SplashScreen'i dahil ediyoruz


void main() {
  runApp(const MyApp());
}


class MyApp extends StatelessWidget {
  const MyApp({super.key});


  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      // Başlangıç sayfası olarak artık SplashScreen'i gösteriyoruz
      home: SplashScreen(),
    );
  }
}
