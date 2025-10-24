// src/pages/ResourceDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { 
  getResourceById, 
  getAvailableSlots, 
  calculatePrice, 
  createBooking 
} from '../services/api';
import { useAuth } from '../hooks/useAuth';

function ResourceDetailPage() {
  const { resourceId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth(); // Giriş yapmış kullanıcı bilgisini al

  const [resource, setResource] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date());
  
  const [availableSlots, setAvailableSlots] = useState([]);
  const [slotsLoading, setSlotsLoading] = useState(false);

  const [selectedSlot, setSelectedSlot] = useState(null);
  const [calculatedPrice, setCalculatedPrice] = useState(null);
  const [priceLoading, setPriceLoading] = useState(false);

  // Varlık detayını çeken effect
  useEffect(() => {
    const fetchResource = async () => {
      setIsLoading(true);
      try {
        const data = await getResourceById(resourceId);
        setResource(data);
      } catch (error) {
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchResource();
  }, [resourceId]);

  // Müsait saatleri çeken effect
  useEffect(() => {
    if (!selectedDate || !resource) return;
    const fetchSlots = async () => {
      setSlotsLoading(true);
      setAvailableSlots([]);
      setSelectedSlot(null);
      setCalculatedPrice(null);

      const year = selectedDate.getFullYear();
      const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
      const day = String(selectedDate.getDate()).padStart(2, '0');
      const dateString = `${year}-${month}-${day}`;
      
      try {
        const data = await getAvailableSlots(resourceId, dateString);
        setAvailableSlots(data);
      } catch (error) {
        console.error(error);
      } finally {
        setSlotsLoading(false);
      }
    };
    fetchSlots();
  }, [selectedDate, resourceId, resource]);

  // Fiyatı hesaplayan effect
  useEffect(() => {
    if (!selectedSlot) {
        setCalculatedPrice(null);
        return;
    }
    const fetchPrice = async () => {
        setPriceLoading(true);
        try {
            const data = await calculatePrice(resourceId, selectedSlot.start_time, selectedSlot.end_time);
            setCalculatedPrice(data.total_price);
        } catch (error) {
            console.error("Fiyat hesaplama hatası:", error);
            setCalculatedPrice(null);
        } finally {
            setPriceLoading(false);
        }
    };
    fetchPrice();
  }, [selectedSlot, resourceId]);

  const handleBooking = async () => {
    if (!selectedSlot) {
        alert("Lütfen bir saat dilimi seçin.");
        return;
    }
    if (!user) {
        alert("Rezervasyon yapmak için lütfen giriş yapın.");
        navigate('/login');
        return;
    }
    
    const bookingData = {
        resource_id: resourceId,
        start_time: selectedSlot.start_time,
        end_time: selectedSlot.end_time,
    };

    try {
        await createBooking(bookingData);
        alert('Rezervasyonunuz başarıyla oluşturuldu!');
        navigate('/my-bookings');
    } catch (error) {
        alert(`Rezervasyon oluşturulamadı: ${error.message}`);
    }
  };

  if (isLoading) return <p>Yükleniyor...</p>;
  if (!resource) return <p>Varlık bulunamadı.</p>;

  return (
    <div className="container mx-auto p-8">
      {resource.images && resource.images.length > 0 && (
         <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <img
              src={resource.images[0].startsWith('/')
                ? `${import.meta.env.VITE_API_BASE_URL}${resource.images[0]}`
                : resource.images[0]
              }
              alt={resource.name}
              className="w-full h-96 object-cover rounded-lg shadow-lg"
            />
            <div className="hidden md:grid grid-cols-2 gap-4">
                {resource.images.slice(1, 5).map((img, index) => (
                    <img
                      key={index}
                      src={img.startsWith('/')
                        ? `${import.meta.env.VITE_API_BASE_URL}${img}`
                        : img
                      }
                      alt={`${resource.name} ${index + 2}`}
                      className="w-full h-full object-cover rounded-lg shadow-md"
                    />
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
              {slotsLoading ? (
                <p>Saatler yükleniyor...</p>
              ) : availableSlots.length > 0 ? (
                <div className="grid grid-cols-3 gap-2">
                  {availableSlots.map((slot, index) => (
                    <button 
                        key={index} 
                        onClick={() => setSelectedSlot(slot)}
                        className={`p-2 border rounded-md text-center transition-colors ${selectedSlot?.start_time === slot.start_time ? 'bg-teal-500 text-white' : 'hover:bg-teal-100'}`}
                    >
                      {new Date(slot.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">Bu tarih için müsait saat bulunmamaktadır.</p>
              )}
            </div>

            {priceLoading && <p className="mt-4 text-center">Fiyat hesaplanıyor...</p>}
            {calculatedPrice !== null && (
              <div className="mt-4 text-center p-4 bg-gray-100 rounded-lg">
                  <p className="font-semibold text-lg">Toplam Ücret: {calculatedPrice} TL</p>
                  <button onClick={handleBooking} className="mt-4 w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
                      Rezervasyon Yap
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
