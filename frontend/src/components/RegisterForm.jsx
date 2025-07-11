// src/components/RegisterForm.jsx

import React, { useState } from 'react';

const RegisterForm = () => {
  // 1. Tüm inputlar için state'leri tanımla
  const [role, setRole] = useState('BUSINESS_OWNER');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Şifrelerin eşleşip eşleşmediğini kontrol et
    if (password !== confirmPassword) {
      alert("Şifreler eşleşmiyor!");
      return; // Fonksiyonu burada durdur
    }

    const newUser = {
      first_name: firstName,
      last_name: lastName,
      phone_number: phone,
      email: email,
      password: password,
      role: role, // 'BUSINESS_OWNER' veya 'CUSTOMER'
    };

    console.log("Gönderilecek Yeni Kullanıcı Verisi:", newUser);

    try {
      // Backend'deki /auth/register endpoint'ine istek gönder
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newUser),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(`Kayıt Başarısız: ${data.detail || 'Bilinmeyen bir hata oluştu.'}`);
      } else {
        alert('Kayıt Başarılı! Şimdi giriş yapabilirsiniz.');
        // İsteğe bağlı: Kullanıcıyı giriş sekmesine yönlendirebiliriz.
      }
    } catch (error) {
      alert('Sunucuya bağlanılamıyor.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
        {/* İŞ YERİ / MÜŞTERİ BUTONLARI (EKSİK OLAN KISIM) */}
        <div className="bg-gray-200 p-1 rounded-full relative flex w-full mb-6">
            <div
                className="absolute bg-white shadow-md w-1/2 h-full rounded-full transition-transform duration-300 ease-in-out"
                style={{ transform: role === 'BUSINESS_OWNER' ? 'translateX(0%)' : 'translateX(100%)' }}
            ></div>
            <button type="button" onClick={() => setRole('BUSINESS_OWNER')} className="relative w-1/2 py-2 text-center z-10 font-semibold text-gray-700">İŞ YERİ</button>
            <button type="button" onClick={() => setRole('CUSTOMER')} className="relative w-1/2 py-2 text-center z-10 font-semibold text-gray-700">MÜŞTERİ</button>
        </div>

        {/* Form Alanları (value ve onChange eklendi) */}
        <div className="grid grid-cols-2 gap-4 mb-4">
            <input value={firstName} onChange={(e) => setFirstName(e.target.value)} className="p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500" placeholder="İsim" required/>
            <input value={email} onChange={(e) => setEmail(e.target.value)} className="p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500" type="email" placeholder="e-mail" required/>
            <input value={lastName} onChange={(e) => setLastName(e.target.value)} className="p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500" placeholder="Soyisim" required/>
            <input value={password} onChange={(e) => setPassword(e.target.value)} className="p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500" type="password" placeholder="Şifre" required/>
            <input value={phone} onChange={(e) => setPhone(e.target.value)} className="p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500" type="tel" placeholder="Telefon"/>
            <input value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} className="p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500" type="password" placeholder="Şifre tekrar" required/>
        </div>

        <button type="submit" className="w-1/2 mx-auto block p-3 bg-teal-500 text-white font-bold rounded-lg hover:bg-teal-600 transition-colors">
            TAMAM
        </button>
    </form>
  );
};

export default RegisterForm;