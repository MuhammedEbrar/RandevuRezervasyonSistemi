// src/components/LoginForm.jsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/auth/login`;
      const response = await fetch(apiUrl,  //orjinal satır bu
        {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          'username': email,
          'password': password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(`Giriş Başarısız: ${data.detail || 'Bilinmeyen bir hata oluştu.'}`);
      } else {
        localStorage.setItem('userToken', data.access_token);
        navigate('/dashboard'); // Yönlendirme
      }
    } catch (error) {
      console.error('Sunucuya bağlanırken bir hata oluştu:', error);
      alert('Sunucuya bağlanılamıyor. Backend\'in çalıştığından emin misin?');
    }
  };

  // EKSİK OLAN JSX KISMI BURADA
  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <input
          className="w-full p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
          type="email"
          placeholder="e-mail"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div className="mb-6">
        <input
          className="w-full p-3 bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
          type="password"
          placeholder="şifre"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit" className="w-full p-3 bg-teal-500 text-white font-bold rounded-lg hover:bg-teal-600 transition-colors">
        GİRİŞ YAP
      </button>
    </form>
  );
};

export default LoginForm;