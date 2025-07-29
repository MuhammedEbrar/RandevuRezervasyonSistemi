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

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (password !== confirmPassword) {
      alert("Şifreler eşleşmiyor!");
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
      // Karmaşık fetch bloğu yerine tek satırlık fonksiyon çağrısı
      await registerUser(newUser);
      alert('Kayıt Başarılı! Şimdi giriş yapabilirsiniz.');
      // İsteğe bağlı: Kullanıcıyı otomatik olarak giriş sekmesine yönlendirebiliriz
      // veya formu temizleyebiliriz.
    } catch (error) {
      alert(`Kayıt Başarısız: ${error.message}`);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
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
