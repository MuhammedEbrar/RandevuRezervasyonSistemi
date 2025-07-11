// src/pages/DashboardPage.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';

function DashboardPage() {
  const navigate = useNavigate();

  // Çıkış yapma fonksiyonu
  const handleLogout = () => {
    localStorage.removeItem('userToken'); // Token'ı sil
    navigate('/login'); // Giriş sayfasına yönlendir
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="p-10 text-center bg-white rounded-lg shadow-xl">
            <h1 className="text-4xl font-bold mb-4">Dashboard</h1>
            <p className="text-xl mb-8">Başarıyla giriş yaptınız. Hoş geldiniz!</p>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
            >
              Çıkış Yap
            </button>
        </div>
    </div>
  );
}
export default DashboardPage;