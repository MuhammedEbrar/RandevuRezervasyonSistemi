// src/pages/AuthPage.jsx
import React, { useState } from 'react';
import LoginForm from '../components/LoginForm';
import RegisterForm from '../components/RegisterForm';

function AuthPage() {
  const [mode, setMode] = useState('login'); // 'login' ya da 'register' olabilir

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
        {/* Üst Başlık */}
        <h1 className="text-teal-600 text-3xl font-bold text-center mb-6">
          Randevu Rezervasyon Sistemi
        </h1>

        {/* Kayan Menü (Toggle Switch) */}
        <div className="bg-gray-200 p-1 rounded-full relative flex w-full max-w-xs mx-auto mb-8">
            <div
                className="absolute bg-white shadow-md w-1/2 h-full rounded-full transition-transform duration-300 ease-in-out"
            style={{ transform: mode === 'login' ? 'translateX(0%)' : 'translateX(100%)' }}
        ></div>
        <button type="button" onClick={() => setMode('login')} className="relative w-1/2 py-2 text-center z-10 font-bold text-gray-700">Giriş Yap</button>
        <button type="button" onClick={() => setMode('register')} className="relative w-1/2 py-2 text-center z-10 font-bold text-gray-700">Kayıt Ol</button>
        </div>

        {/* Koşullu Form Görüntüleme */}
        {mode === 'login' ? <LoginForm /> : <RegisterForm />}
      </div>
    </div>
  );
}

export default AuthPage;