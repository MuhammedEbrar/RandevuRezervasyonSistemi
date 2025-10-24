// src/pages/MyBookingsPage.jsx
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getMyBookings, cancelBooking } from '../services/api';
import Navbar from '../components/Navbar';

function MyBookingsPage() {
  const [bookings, setBookings] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cancellingId, setCancellingId] = useState(null);
  const navigate = useNavigate();

  // Durum çevirileri
  const statusTranslations = {
    'CONFIRMED': 'Onaylandı',
    'PENDING': 'Beklemede',
    'CANCELLED': 'İptal Edildi',
    'COMPLETED': 'Tamamlandı'
  };

  useEffect(() => {
    fetchMyBookings();
  }, []);

  const fetchMyBookings = async () => {
    const token = localStorage.getItem('userToken');
    if (!token) {
      setError('Rezervasyonlarınızı görmek için giriş yapmalısınız.');
      setIsLoading(false);
      return;
    }

    try {
      const data = await getMyBookings();
      setBookings(data);
      setError(null);
    } catch (err) {
      console.error('Rezervasyon yükleme hatası:', err);
      setError('Rezervasyonlar yüklenirken bir hata oluştu.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelBooking = async (bookingId) => {
    if (!window.confirm('Bu rezervasyonu iptal etmek istediğinizden emin misiniz?')) {
      return;
    }

    setCancellingId(bookingId);
    try {
      await cancelBooking(bookingId);
      // Rezervasyonu listeden güncelle
      setBookings(bookings.map(booking =>
        booking.booking_id === bookingId
          ? { ...booking, status: 'CANCELLED' }
          : booking
      ));
      alert('Rezervasyon başarıyla iptal edildi.');
    } catch (err) {
      console.error('İptal hatası:', err);
      alert('Rezervasyon iptal edilirken bir hata oluştu. Lütfen tekrar deneyin.');
    } finally {
      setCancellingId(null);
    }
  };

  const getStatusStyle = (status) => {
    switch (status) {
      case 'CONFIRMED':
        return 'bg-green-100 text-green-800 border border-green-300';
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800 border border-yellow-300';
      case 'CANCELLED':
        return 'bg-red-100 text-red-800 border border-red-300';
      case 'COMPLETED':
        return 'bg-blue-100 text-blue-800 border border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border border-gray-300';
    }
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <>
        <Navbar />
        <div className="container mx-auto p-8">
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Rezervasyonlarınız yükleniyor...</p>
          </div>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div className="container mx-auto p-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <div className="text-red-600 text-5xl mb-4">⚠</div>
            <h2 className="text-xl font-semibold text-red-800 mb-2">Hata</h2>
            <p className="text-red-600 mb-4">{error}</p>
            <Link to="/resources" className="inline-block bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700">
              Ana Sayfaya Dön
            </Link>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="container mx-auto p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Rezervasyonlarım</h1>
        </div>

      {bookings.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-lg shadow-md">
          <div className="text-gray-400 text-6xl mb-4">📅</div>
          <p className="text-gray-600 text-lg mb-6">Henüz hiç rezervasyon yapmadınız.</p>
          <p className="text-gray-500 mb-6">Hizmet ve mekanları keşfederek rezervasyon yapabilirsiniz!</p>
          <button
            onClick={() => navigate('/resources')}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 font-semibold shadow-md transition-colors"
          >
            Hizmet ve Mekanları Keşfet
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map(booking => (
            <div
              key={booking.booking_id}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border border-gray-200"
            >
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                {/* Sol taraf - Rezervasyon Bilgileri */}
                <div className="flex-grow">
                  <h3 className="font-bold text-xl text-gray-800 mb-2">
                    {booking.resource.name}
                  </h3>

                  <div className="space-y-1 text-sm text-gray-600">
                    <div className="flex items-center">
                      <span className="font-semibold mr-2">📅 Başlangıç:</span>
                      <span>{formatDateTime(booking.start_time)}</span>
                    </div>

                    {booking.end_time && (
                      <div className="flex items-center">
                        <span className="font-semibold mr-2">📅 Bitiş:</span>
                        <span>{formatDateTime(booking.end_time)}</span>
                      </div>
                    )}

                    <div className="flex items-center mt-2">
                      <span className="font-semibold mr-2">💰 Toplam Ücret:</span>
                      <span className="text-lg font-bold text-green-600">
                        {booking.total_price} TL
                      </span>
                    </div>

                    {booking.notes && (
                      <div className="flex items-start mt-2">
                        <span className="font-semibold mr-2">📝 Not:</span>
                        <span className="text-gray-500">{booking.notes}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Sağ taraf - Durum ve Aksiyonlar */}
                <div className="flex flex-col items-end gap-3">
                  <span className={`px-4 py-2 text-sm font-semibold rounded-full ${getStatusStyle(booking.status)}`}>
                    {statusTranslations[booking.status] || booking.status}
                  </span>

                  {(booking.status === 'CONFIRMED' || booking.status === 'PENDING') && (
                    <button
                      onClick={() => handleCancelBooking(booking.booking_id)}
                      disabled={cancellingId === booking.booking_id}
                      className={`px-4 py-2 rounded-lg font-semibold text-sm transition-colors
                        ${cancellingId === booking.booking_id
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : 'bg-red-600 text-white hover:bg-red-700'
                        }`}
                    >
                      {cancellingId === booking.booking_id ? 'İptal Ediliyor...' : '🚫 Rezervasyonu İptal Et'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {bookings.length > 0 && (
        <div className="mt-8 text-center">
          <button
            onClick={() => navigate('/resources')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 font-semibold transition-colors"
          >
            Yeni Rezervasyon Yap
          </button>
        </div>
      )}
    </div>
    </>
  );
}

export default MyBookingsPage;
