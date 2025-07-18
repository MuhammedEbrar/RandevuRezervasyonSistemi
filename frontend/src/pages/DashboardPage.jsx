// src/pages/DashboardPage.jsx
import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth'; // Yeni hook'umuzu import et

function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth(); // Kullanıcı bilgilerini al

  const handleLogout = () => {
    localStorage.removeItem('userToken');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="p-10 text-center bg-white rounded-lg shadow-xl">
            <h1 className="text-4xl font-bold mb-4">Dashboard</h1>
            {/* Kullanıcının ismini göster (eğer varsa) */}
            <p className="text-xl mb-8">Hoş geldiniz, {user?.email}!</p>

            {/* --- ROL TABANLI BUTON GÖSTERİMİ --- */}
            <div className="space-x-4">
              {user?.role === 'BUSINESS_OWNER' && (
                <Link 
                  to="/dashboard/resources" 
                  className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                >
                  Varlıklarımı Yönet
                </Link>
              )}

              {user?.role === 'CUSTOMER' && (
                <Link 
                  to="/my-bookings" // Henüz bu sayfayı yapmadık ama linki koyalım
                  className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                >
                  Rezervasyonlarım
                </Link>
              )}

              <button
                onClick={handleLogout}
                className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
              >
                Çıkış Yap
              </button>
            </div>
        </div>
    </div>
  );
}
export default DashboardPage;