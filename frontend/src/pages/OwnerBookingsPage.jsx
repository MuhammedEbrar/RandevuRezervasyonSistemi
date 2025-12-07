// src/pages/OwnerBookingsPage.jsx
import React, { useState, useEffect } from 'react';
import { getOwnerBookings, updateBookingStatus } from '../services/api';
import Navbar from '../components/Navbar';

function OwnerBookingsPage() {
    const [bookings, setBookings] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [processingId, setProcessingId] = useState(null);

    useEffect(() => {
        fetchBookings();
    }, []);

    const fetchBookings = async () => {
        try {
            const data = await getOwnerBookings();
            // Tarihe göre siralama (yeni en üstte)
            const sortedData = data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            setBookings(sortedData);
        } catch (err) {
            console.error('Rezervasyon yükleme hatası:', err);
            setError('Rezervasyonlar yüklenirken bir hata oluştu.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleStatusUpdate = async (bookingId, newStatus) => {
        if (!window.confirm(`Rezervasyonu ${newStatus === 'CONFIRMED' ? 'onaylamak' : 'reddetmek'} istediğinize emin misiniz?`)) {
            return;
        }

        setProcessingId(bookingId);
        try {
            await updateBookingStatus(bookingId, newStatus);
            setBookings(bookings.map(booking =>
                booking.booking_id === bookingId
                    ? { ...booking, status: newStatus }
                    : booking
            ));
            alert(`Rezervasyon başarıyla ${newStatus === 'CONFIRMED' ? 'onaylandı' : 'reddedildi'}.`);
        } catch (err) {
            console.error('Durum güncellenemedi:', err);
            alert('İşlem başarısız oldu.');
        } finally {
            setProcessingId(null);
        }
    };

    const formatDateTime = (dateString) => {
        return new Date(dateString).toLocaleString('tr-TR', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    const getStatusStyle = (status) => {
        switch (status) {
            case 'CONFIRMED': return 'bg-green-100 text-green-800';
            case 'PENDING': return 'bg-yellow-100 text-yellow-800';
            case 'CANCELLED': return 'bg-red-100 text-red-800';
            case 'REJECTED': return 'bg-gray-100 text-gray-800';
            case 'COMPLETED': return 'bg-blue-100 text-blue-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    if (isLoading) return <div className="text-center p-10">Yükleniyor...</div>;
    if (error) return <div className="text-center p-10 text-red-500">{error}</div>;

    return (
        <>
            <Navbar />
            <div className="container mx-auto p-8">
                <h1 className="text-3xl font-bold mb-6">Gelen Rezervasyon Talepleri</h1>

                {bookings.length === 0 ? (
                    <p className="text-gray-600">Henüz bir rezervasyon talebi bulunmuyor.</p>
                ) : (
                    <div className="bg-white shadow-md rounded-lg overflow-hidden">
                        <table className="min-w-full leading-normal">
                            <thead>
                                <tr>
                                    <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Hizmet / Mekan
                                    </th>
                                    <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Müşteri
                                    </th>
                                    <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Tarih
                                    </th>
                                    <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Tutar
                                    </th>
                                    <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        Durum
                                    </th>
                                    <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                        İşlemler
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {bookings.map((booking) => (
                                    <tr key={booking.booking_id}>
                                        <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                                            <p className="text-gray-900 whitespace-no-wrap font-semibold">
                                                {booking.resource?.name || 'Bilinmiyor'}
                                            </p>
                                        </td>
                                        <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                                            {booking.customer_id}
                                        </td>
                                        <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                                            <p className="text-gray-900 whitespace-no-wrap">
                                                {formatDateTime(booking.start_time)}
                                            </p>
                                            <p className="text-gray-500 text-xs text-center">⬇</p>
                                            <p className="text-gray-900 whitespace-no-wrap">
                                                {formatDateTime(booking.end_time)}
                                            </p>
                                        </td>
                                        <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm font-bold text-green-600">
                                            {booking.total_price} TL
                                        </td>
                                        <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                                            <span className={`relative inline-block px-3 py-1 font-semibold leading-tight rounded-full ${getStatusStyle(booking.status)}`}>
                                                <span className="relative">{booking.status}</span>
                                            </span>
                                        </td>
                                        <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                                            {booking.status === 'PENDING' && (
                                                <div className="flex space-x-2">
                                                    <button
                                                        onClick={() => handleStatusUpdate(booking.booking_id, 'CONFIRMED')}
                                                        disabled={processingId === booking.booking_id}
                                                        className="bg-green-500 hover:bg-green-700 text-white font-bold py-1 px-3 rounded text-xs"
                                                    >
                                                        Onayla
                                                    </button>
                                                    <button
                                                        onClick={() => handleStatusUpdate(booking.booking_id, 'REJECTED')}
                                                        disabled={processingId === booking.booking_id}
                                                        className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded text-xs"
                                                    >
                                                        Reddet
                                                    </button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </>
    );
}

export default OwnerBookingsPage;
