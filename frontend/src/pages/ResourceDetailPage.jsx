// src/pages/ResourceDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

function ResourceDetailPage() {
  const { resourceId } = useParams();
  const navigate = useNavigate();
  const [resource, setResource] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [availableSlots, setAvailableSlots] = useState([]);
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [calculatedPrice, setCalculatedPrice] = useState(null);
  const [isBooking, setIsBooking] = useState(false);

  // Varlık detayını çeken useEffect
  useEffect(() => {
    const fetchResource = async () => {
      setIsLoading(true);
      const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/resources/${resourceId}`;
      try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error('Varlık bulunamadı.');
        const data = await response.json();
        setResource(data);
      } catch (error) {
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchResource();
  }, [resourceId]);

  // Müsait saatleri çeken useEffect
  useEffect(() => {
    if (!selectedDate || !resource) return;
    setSelectedSlot(null);
    setCalculatedPrice(null);
    const fetchAvailableSlots = async () => {
      setSlotsLoading(true);
      setAvailableSlots([]);
      const year = selectedDate.getFullYear();
      const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
      const day = String(selectedDate.getDate()).padStart(2, '0');
      const dateString = `${year}-${month}-${day}`;
      const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/resources/${resourceId}/availability/available_slots?start_date=${dateString}&end_date=${dateString}`;
      try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error('Müsait saatler alınamadı.');
        const data = await response.json();
        setAvailableSlots(data);
      } catch (error) {
        console.error(error);
      } finally {
        setSlotsLoading(false);
      }
    };
    fetchAvailableSlots();
  }, [selectedDate, resourceId, resource]);

  // Fiyat hesaplayan useEffect
  useEffect(() => {
    if (!selectedSlot) {
      setCalculatedPrice(null);
      return;
    }
    const calculatePrice = async () => {
      const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/bookings/calculate_price`;
      try {
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            resource_id: resourceId,
            start_time: selectedSlot.start_time,
            end_time: selectedSlot.end_time,
          }),
        });
        if (!response.ok) throw new Error('Fiyat hesaplanamadı.');
        const data = await response.json();
        setCalculatedPrice(data.total_price);
      } catch (error) {
        alert(error.message);
      }
    };
    calculatePrice();
  }, [selectedSlot, resourceId]);

  // Rezervasyon yapan fonksiyon
  const handleBooking = async () => {
    const token = localStorage.getItem('userToken');
    if (!token) {
      alert('Rezervasyon yapmak için lütfen giriş yapın.');
      navigate('/login');
      return;
    }
    if (!selectedSlot) {
      alert('Lütfen bir saat dilimi seçin.');
      return;
    }
    setIsBooking(true);
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/bookings/`;
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          resource_id: resourceId,
          start_time: selectedSlot.start_time,
          end_time: selectedSlot.end_time,
        }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Rezervasyon oluşturulamadı.');
      }
      alert('Rezervasyonunuz başarıyla oluşturuldu!');
      navigate('/my-bookings');
    } catch (error) {
      alert(`Hata: ${error.message}`);
    } finally {
      setIsBooking(false);
    }
  };

  if (isLoading) return <p className="text-center p-10">Yükleniyor...</p>;
  if (!resource) return <p className="text-center p-10">Varlık bulunamadı.</p>;

  return (
    <div className="container mx-auto p-4 md:p-8">
      {resource.images && resource.images.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <img src={resource.images[0]} alt={resource.name} className="w-full h-64 md:h-96 object-cover rounded-lg shadow-lg"/>
            <div className="hidden md:grid grid-cols-2 gap-4">
                {resource.images.slice(1, 5).map((img, index) => (
                    <img key={index} src={img} alt={`${resource.name} ${index + 2}`} className="w-full h-full object-cover rounded-lg shadow-md"/>
                ))}
            </div>
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2">
          <h1 className="text-4xl font-bold mb-2">{resource.name}</h1>
          {resource.location && <p className="text-gray-600 mb-4">{resource.location.city}, {resource.location.country}</p>}
          <hr className="my-4" />
          <h2 className="text-2xl font-semibold mb-2">Açıklama</h2>
          <p className="text-gray-800">{resource.description}</p>
          <hr className="my-4" />
          <h2 className="text-2xl font-semibold mb-2">İptal Politikası</h2>
          <p className="text-gray-700">{resource.cancellation_policy}</p>
        </div>
        <div className="md:col-span-1">
          <div className="p-6 border rounded-lg shadow-lg sticky top-8">
            <h2 className="text-2xl font-semibold mb-4">Tarih Seçin</h2>
            <DatePicker selected={selectedDate} onChange={(date) => setSelectedDate(date)} inline minDate={new Date()} />
            <div className="mt-6">
              <h3 className="text-xl font-semibold mb-2">Müsait Saatler ({selectedDate.toLocaleDateString()})</h3>
              {slotsLoading ? ( <p>Saatler yükleniyor...</p> ) : 
               availableSlots.length > 0 ? (
                <div className="grid grid-cols-3 gap-2">
                  {availableSlots.map((slot, index) => (
                    <button key={index} onClick={() => setSelectedSlot(slot)} className={`p-2 border rounded-md text-center transition-colors text-sm ${selectedSlot?.start_time === slot.start_time ? 'bg-teal-500 text-white' : 'hover:bg-teal-100'}`}>
                      {new Date(slot.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </button>
                  ))}
                </div>
              ) : ( <p className="text-gray-500">Bu tarih için müsait saat bulunmamaktadır.</p> )}
            </div>
            {selectedSlot && (
              <div className="mt-6 pt-6 border-t">
                {calculatedPrice !== null ? (
                  <p className="text-2xl font-bold text-center mb-4">Ücret: {calculatedPrice} TL</p>
                ) : (
                  <p className="text-center">Fiyat hesaplanıyor...</p>
                )}
                <button onClick={handleBooking} disabled={isBooking || calculatedPrice === null} className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-lg transition-colors disabled:bg-gray-400">
                  {isBooking ? 'İşleniyor...' : 'Rezervasyon Yap'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResourceDetailPage;
