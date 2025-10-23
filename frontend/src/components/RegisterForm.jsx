// src/components/RegisterForm.jsx
import React, { useState } from 'react';
import { registerUser } from '../services/api'; // Yeni import

const RegisterForm = () => {
  const [role, setRole] = useState('BUSINESS_OWNER');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErrors({});
    setSuccessMessage('');

    // Frontend validasyonları
    const newErrors = {};

    if (password !== confirmPassword) {
      newErrors.confirmPassword = "Şifreler eşleşmiyor!";
    }

    if (password.length < 8) {
      newErrors.password = "Şifreniz en az 8 karakterli olmalıdır.";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    const newUser = {
      first_name: firstName,
      last_name: lastName,
      phone_number: phone,
      email: email,
      password: password,
      role: role,
    };

    try {
      await registerUser(newUser);
      setSuccessMessage('Kayıt Başarılı! Şimdi giriş yapabilirsiniz.');
      // Formu temizle
      setFirstName('');
      setLastName('');
      setPhone('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
    } catch (error) {
      // Backend'den gelen hataları parse et
      try {
        const errorData = JSON.parse(error.message);
        const backendErrors = {};

        if (Array.isArray(errorData)) {
          errorData.forEach(err => {
            const field = err.loc[err.loc.length - 1]; // Son loc elemanı field adı

            // Kullanıcı dostu mesajlar
            if (field === 'password' && err.type === 'string_too_short') {
              backendErrors.password = 'Şifreniz en az 8 karakterli olmalıdır.';
            } else if (field === 'email') {
              backendErrors.email = 'Geçerli bir e-posta adresi giriniz.';
            } else if (field === 'role') {
              backendErrors.role = 'Geçersiz kullanıcı rolü.';
            } else {
              backendErrors[field] = err.msg || 'Geçersiz değer.';
            }
          });
        } else if (errorData.detail) {
          backendErrors.general = errorData.detail;
        }

        setErrors(backendErrors);
      } catch {
        setErrors({ general: 'Bir hata oluştu. Lütfen tekrar deneyin.' });
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
        {/* Başarı Mesajı */}
        {successMessage && (
          <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded-md">
            {successMessage}
          </div>
        )}

        {/* Genel Hata Mesajı */}
        {errors.general && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {errors.general}
          </div>
        )}

        {/* İŞ YERİ / MÜŞTERİ BUTONLARI */}
        <div className="bg-gray-200 p-1 rounded-full relative flex w-full mb-6">
            <div
                className="absolute bg-white shadow-md w-1/2 h-full rounded-full transition-transform duration-300 ease-in-out"
                style={{ transform: role === 'BUSINESS_OWNER' ? 'translateX(0%)' : 'translateX(100%)' }}
            ></div>
            <button type="button" onClick={() => setRole('BUSINESS_OWNER')} className="relative w-1/2 py-2 text-center z-10 font-semibold text-gray-700">İŞ YERİ</button>
            <button type="button" onClick={() => setRole('CUSTOMER')} className="relative w-1/2 py-2 text-center z-10 font-semibold text-gray-700">MÜŞTERİ</button>
        </div>

        {/* Form Alanları */}
        <div className="grid grid-cols-2 gap-4 mb-4">
            {/* İsim */}
            <div className="relative">
              <input
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className={`p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 w-full ${errors.first_name ? 'ring-2 ring-red-500' : 'focus:ring-teal-500'}`}
                placeholder="İsim"
                required
              />
              {errors.first_name && (
                <span className="absolute right-3 top-3 text-red-500 text-xl" title={errors.first_name}>⚠</span>
              )}
            </div>

            {/* Email */}
            <div className="relative">
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={`p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 w-full ${errors.email ? 'ring-2 ring-red-500' : 'focus:ring-teal-500'}`}
                type="email"
                placeholder="e-mail"
                required
              />
              {errors.email && (
                <div className="mt-1 text-red-500 text-sm flex items-center">
                  <span className="mr-1">⚠</span> {errors.email}
                </div>
              )}
            </div>

            {/* Soyisim */}
            <div className="relative">
              <input
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className={`p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 w-full ${errors.last_name ? 'ring-2 ring-red-500' : 'focus:ring-teal-500'}`}
                placeholder="Soyisim"
                required
              />
              {errors.last_name && (
                <span className="absolute right-3 top-3 text-red-500 text-xl" title={errors.last_name}>⚠</span>
              )}
            </div>

            {/* Şifre */}
            <div className="relative">
              <input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 w-full ${errors.password ? 'ring-2 ring-red-500' : 'focus:ring-teal-500'}`}
                type="password"
                placeholder="Şifre"
                required
              />
              {errors.password && (
                <div className="mt-1 text-red-500 text-sm flex items-center">
                  <span className="mr-1">⚠</span> {errors.password}
                </div>
              )}
            </div>

            {/* Telefon */}
            <div className="relative">
              <input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className={`p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 w-full ${errors.phone_number ? 'ring-2 ring-red-500' : 'focus:ring-teal-500'}`}
                type="tel"
                placeholder="Telefon"
              />
              {errors.phone_number && (
                <span className="absolute right-3 top-3 text-red-500 text-xl" title={errors.phone_number}>⚠</span>
              )}
            </div>

            {/* Şifre Tekrar */}
            <div className="relative">
              <input
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className={`p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 w-full ${errors.confirmPassword ? 'ring-2 ring-red-500' : 'focus:ring-teal-500'}`}
                type="password"
                placeholder="Şifre tekrar"
                required
              />
              {errors.confirmPassword && (
                <div className="mt-1 text-red-500 text-sm flex items-center">
                  <span className="mr-1">⚠</span> {errors.confirmPassword}
                </div>
              )}
            </div>
        </div>

        <button type="submit" className="w-1/2 mx-auto block p-3 bg-teal-500 text-white font-bold rounded-lg hover:bg-teal-600 transition-colors">
            TAMAM
        </button>
    </form>
  );
};

export default RegisterForm;
