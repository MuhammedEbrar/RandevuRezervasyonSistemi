// src/components/LoginForm.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../services/api'; // Yeni import

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      // Karmaşık fetch bloğu yerine tek satırlık fonksiyon çağrısı
      const data = await loginUser(email, password);

      // Token ve user bilgilerini kaydet
      localStorage.setItem('userToken', data.access_token);
      localStorage.setItem('userInfo', JSON.stringify(data.user));

      // Role'e göre yönlendirme
      if (data.user.role === 'BUSINESS_OWNER') {
        navigate('/dashboard'); // İşletme sahibi dashboard'a gider
      } else {
        navigate('/resources'); // Müşteri hizmet listesine gider
      }
    } catch (error) {
      // api.js'ten fırlatılan hata mesajını burada yakalıyoruz
      alert(`Giriş Başarısız: ${error.message}`);
    }
  };

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
