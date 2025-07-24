// lib/payment_page.dart

import 'package:flutter/material.dart';
import 'package:mobile/booking_success_page.dart';

class PaymentPage extends StatelessWidget {
  final String bookingPrice; // Fiyatı bir önceki sayfadan alacağız

  const PaymentPage({
    super.key,
    required this.bookingPrice,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ödeme'),
        backgroundColor: Colors.blueGrey,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.payment, size: 100, color: Colors.blueGrey),
              const SizedBox(height: 20),
              const Text(
                'Ödenecek Tutar',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              Text(
                '$bookingPrice TL',
                style: const TextStyle(fontSize: 36, color: Colors.teal, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 40),
              ElevatedButton(
                onPressed: () {
                  // Ödeme başarılıymış gibi davranıp başarı sayfasına yönlendiriyoruz
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (context) => const BookingSuccessPage()),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: const EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                ),
                child: const Text('Ödemeyi Onayla'),
              )
            ],
          ),
        ),
      ),
    );
  }
}