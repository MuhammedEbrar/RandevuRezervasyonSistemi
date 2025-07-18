// src/pages/MyBookingsPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function MyBookingsPage() {
  const [bookings, setBookings] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMyBookings = async () => {
      const token = localStorage.getItem('userToken');
      if (!token) {
        setError('Rezervasyonlarınızı görmek için giriş yapmalısınız.');
        setIsLoading(false);
        return;
      }

      const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/customer/bookings`;
      try {
        const response = await fetch(apiUrl, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Rezervasyonlar alınamadı.');
        }

        const data = await response.json();
        setBookings(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMyBookings();
  }, []); // Sadece sayfa ilk yüklendiğinde çalışır

  if (isLoading) return <p className="text-center p-10">Yükleniyor...</p>;
  if (error) return <p className="text-center p-10 text-red-500">Hata: {error}</p>;

  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Rezervasyonlarım</h1>
        <Link to="/dashboard" className="text-blue-500 hover:underline">
          &larr; Dashboard'a Geri Dön
        </Link>
      </div>

      {bookings.length === 0 ? (
        <div className="text-center py-10 bg-white rounded-lg shadow-md">
            <p className="text-gray-500">Henüz hiç rezervasyon yapmadınız.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map(booking => (
            <div key={booking.booking_id} className="bg-white p-4 rounded-lg shadow-md flex flex-col sm:flex-row items-start sm:items-center justify-between">
              <div className="flex-grow">
                <p className="font-bold text-lg">{booking.resource.name}</p>
                <p className="text-sm text-gray-600">
                  {new Date(booking.start_time).toLocaleString('tr-TR', { dateStyle: 'medium', timeStyle: 'short' })}
                </p>
                <p className="text-sm mt-1">
                  Toplam Ücret: <strong>{booking.total_price} TL</strong>
                </p>
              </div>
              <div className="mt-2 sm:mt-0">
                <span className={`px-3 py-1 text-sm font-semibold rounded-full 
                  ${booking.status === 'CONFIRMED' ? 'bg-green-200 text-green-800' : 
                    booking.status === 'PENDING' ? 'bg-yellow-200 text-yellow-800' : 
                    'bg-red-200 text-red-800'}`}>
                  {booking.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MyBookingsPage;
