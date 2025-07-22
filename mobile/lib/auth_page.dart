// lib/auth_page.dart (Son Tasarım)


import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:mobile/auth_service.dart';
import 'package:mobile/home_page.dart';
import 'package:mobile/main.dart'; // Tema değiştirici için dahil ettik

class AuthPage extends StatefulWidget {
  const AuthPage({super.key});

  @override
  State<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<AuthPage> {
  bool _isLoginView = true;
  bool _isBusinessRole = false;
  bool _isLoading = false;

  final _loginFormKey = GlobalKey<FormState>();
  final _registerFormKey = GlobalKey<FormState>();

  final _loginEmailController = TextEditingController();
  final _loginPasswordController = TextEditingController();
  final _registerFirstNameController = TextEditingController();
  final _registerLastNameController = TextEditingController();
  final _registerPhoneController = TextEditingController();
  final _registerEmailController = TextEditingController();
  final _registerPasswordController = TextEditingController();
  final _registerPasswordConfirmController = TextEditingController();
  
  final _authService = AuthService();

  void _submitForm() async {
    setState(() { _isLoading = true; });
    final formKey = _isLoginView ? _loginFormKey : _registerFormKey;
    if (formKey.currentState?.validate() ?? false) {
      if (_isLoginView) {
        bool success = await _authService.login(_loginEmailController.text, _loginPasswordController.text);
        if (success && mounted) {
          Navigator.pushReplacement(context, MaterialPageRoute(builder: (context) => const HomePage()));
        } else if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Giriş başarısız.')));
        }
      } else {
        await _authService.register(
          email: _registerEmailController.text, password: _registerPasswordController.text, firstName: _registerFirstNameController.text, lastName: _registerLastNameController.text, phone: _registerPhoneController.text, role: _isBusinessRole ? 'BUSINESS_OWNER' : 'CUSTOMER',
        );
        if(mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Kayıt isteği gönderildi.')));
          setState(() { _isLoginView = true; });
        }
      }
    }
    if(mounted) { setState(() { _isLoading = false; }); }
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: isDarkMode ? [const Color(0xff1a2a2a), const Color(0xff121212)] : [Colors.teal.shade50, Colors.blueGrey.shade100],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(24),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                child: Container(
                  constraints: const BoxConstraints(maxWidth: 400),
                  padding: const EdgeInsets.all(24.0),
                  decoration: BoxDecoration(
                    color: Theme.of(context).scaffoldBackgroundColor.withOpacity(isDarkMode ? 0.3 : 0.6),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: Colors.white.withOpacity(0.1)),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Align(
                        alignment: Alignment.topRight,
                        child: IconButton(
                          splashRadius: 20,
                          icon: Icon(isDarkMode ? Icons.light_mode_outlined : Icons.dark_mode_outlined),
                          onPressed: () {
                            themeNotifier.value = isDarkMode ? ThemeMode.light : ThemeMode.dark;
                          },
                        ),
                      ),
                      Text('Randevu Rezervasyon Sistemi', textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold, color: isDarkMode ? Colors.tealAccent.shade100 : Colors.teal.shade800)),
                      const SizedBox(height: 24),
                      _buildAuthTabs(),
                      const SizedBox(height: 24),
                      AnimatedSwitcher(
                        duration: const Duration(milliseconds: 300),
                        transitionBuilder: (child, animation) => FadeTransition(opacity: animation, child: child),
                        child: _isLoginView ? _buildLoginForm() : _buildRegisterForm(),
                      ),
                      const SizedBox(height: 24),
                      _isLoading ? const CircularProgressIndicator() : _buildSubmitButton(),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildAuthTabs() {
    return Container(
      decoration: BoxDecoration(color: Theme.of(context).scaffoldBackgroundColor.withOpacity(0.5), borderRadius: BorderRadius.circular(12)),
      child: Row(
        children: [
          Expanded(child: _buildToggleTab('Giriş Yap', true)),
          Expanded(child: _buildToggleTab('Kayıt Ol', false)),
        ],
      ),
    );
  }

  Widget _buildToggleTab(String text, bool isLoginTab) {
    final bool isSelected = _isLoginView == isLoginTab;
    return GestureDetector(
      onTap: () => setState(() => _isLoginView = isLoginTab),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? Colors.teal : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(child: Text(text, style: TextStyle(color: isSelected ? Colors.white : Theme.of(context).textTheme.bodyLarge?.color, fontWeight: FontWeight.bold))),
      ),
    );
  }

  Widget _buildLoginForm() {
    return Form(
      key: _loginFormKey,
      child: Column(
        key: const ValueKey('login_form'),
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildTextField(controller: _loginEmailController, label: 'E-mail', icon: Icons.email_outlined, validator: (v) => v!.isEmpty ? 'Lütfen e-mail girin' : null),
          const SizedBox(height: 16),
          _buildTextField(controller: _loginPasswordController, label: 'Şifre', icon: Icons.lock_outline, isPassword: true, validator: (v) => v!.isEmpty ? 'Lütfen şifre girin' : null),
        ],
      ),
    );
  }

  Widget _buildRegisterForm() {
    return Form(
      key: _registerFormKey,
      child: Column(
        key: const ValueKey('register_form'),
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(color: Theme.of(context).scaffoldBackgroundColor.withOpacity(0.5), borderRadius: BorderRadius.circular(12)),
            child: Row(
              children: [
                Expanded(child: _buildRoleButton('İŞ YERİ', true)),
                Expanded(child: _buildRoleButton('MÜŞTERİ', false)),
              ],
            ),
          ),
          const SizedBox(height: 20),
          _buildTextField(controller: _registerFirstNameController, label: 'İsim', icon: Icons.person_outline, validator: (v) => v!.isEmpty ? 'İsim gerekli' : null),
          const SizedBox(height: 16),
          _buildTextField(controller: _registerLastNameController, label: 'Soyisim', icon: Icons.person_outline, validator: (v) => v!.isEmpty ? 'Soyisim gerekli' : null),
          const SizedBox(height: 16),
          _buildTextField(controller: _registerEmailController, label: 'E-mail', icon: Icons.email_outlined, validator: (v) => v!.isEmpty ? 'E-mail gerekli' : null, keyboardType: TextInputType.emailAddress),
          const SizedBox(height: 16),
          _buildTextField(controller: _registerPhoneController, label: 'Telefon', icon: Icons.phone_outlined, keyboardType: TextInputType.phone),
          const SizedBox(height: 16),
          _buildTextField(controller: _registerPasswordController, label: 'Şifre', icon: Icons.lock_outline, isPassword: true, validator: (v) => v!.isEmpty ? 'Şifre gerekli' : null),
          const SizedBox(height: 16),
          _buildTextField(controller: _registerPasswordConfirmController, label: 'Şifre Tekrar', icon: Icons.lock_outline, isPassword: true, validator: (v) {
            if (v!.isEmpty) return 'Şifre tekrarı gerekli';
            if (v != _registerPasswordController.text) return 'Şifreler uyuşmuyor';
            return null;
          }),
        ],
      ),
    );
  }

  Widget _buildRoleButton(String text, bool isBusiness) {
    bool isSelected = _isBusinessRole == isBusiness;
    return GestureDetector(
      onTap: () => setState(() => _isBusinessRole = isBusiness),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? Colors.teal : Colors.transparent,
          borderRadius: BorderRadius.circular(10),
        ),
        child: Center(child: Text(text, style: TextStyle(color: isSelected ? Colors.white : Theme.of(context).textTheme.bodyLarge?.color, fontWeight: FontWeight.bold))),
      ),
    );
  }

  Widget _buildTextField({required TextEditingController controller, required String label, required IconData icon, bool isPassword = false, String? Function(String?)? validator, TextInputType? keyboardType}) {
    return TextFormField(
      controller: controller,
      obscureText: isPassword,
      validator: validator,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, color: Colors.grey[500]),
        contentPadding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 16.0),
      ),
    );
  }

  Widget _buildSubmitButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _submitForm,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.teal,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          elevation: 5,
          shadowColor: Colors.teal.withOpacity(0.4),
        ),
        child: const Text('TAMAM', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
      ),
    );
  }
}