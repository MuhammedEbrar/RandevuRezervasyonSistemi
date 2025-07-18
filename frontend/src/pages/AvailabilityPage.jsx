// src/pages/AvailabilityPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function AvailabilityPage() {
  const { resourceId } = useParams();
  const [schedules, setSchedules] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Form state'leri
  const [ruleType, setRuleType] = useState('REGULAR');
  const [dayOfWeek, setDayOfWeek] = useState('MONDAY');
  const [specificDate, setSpecificDate] = useState('');
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('17:00');
  const [isAvailable, setIsAvailable] = useState(true);

  // Mevcut kuralları çeken useEffect
  useEffect(() => {
    const fetchSchedules = async () => {
      setIsLoading(true);
      const token = localStorage.getItem('userToken');
      const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/resources/${resourceId}/availability/`;
      try {
        const response = await fetch(apiUrl, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Takvim verisi alınamadı.');
        const data = await response.json();
        setSchedules(data);
      } catch (error) {
        alert(error.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchSchedules();
  }, [resourceId]);

  // Form gönderme fonksiyonu
  const handleSubmit = async (event) => {
    event.preventDefault();
    const token = localStorage.getItem('userToken');

    let newRule = {
      type: ruleType,
      start_time: startTime,
      end_time: endTime,
      is_available: isAvailable,
    };

    if (ruleType === 'REGULAR') {
      newRule.day_of_week = dayOfWeek;
    } else {
      if (!specificDate) {
        alert('Lütfen istisna için bir tarih seçin.');
        return;
      }
      newRule.specific_date = specificDate;
    }

    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/resources/${resourceId}/availability/`;
    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newRule),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(JSON.stringify(errorData.detail));
      }

      const createdSchedule = await response.json();
      setSchedules([...schedules, createdSchedule]);
      alert('Yeni kural başarıyla eklendi!');

    } catch (error) {
      alert(`Hata: ${error.message}`);
    }
  };

  // Silme Fonksiyonu
  const handleDelete = async (scheduleId) => {
    if (!window.confirm('Bu kuralı silmek istediğinize emin misiniz?')) return;
    
    const token = localStorage.getItem('userToken');
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/resources/${resourceId}/availability/${scheduleId}`; 

    try {
        const response = await fetch(apiUrl, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` },
        });

        if (!response.ok) {
            throw new Error('Kural silinemedi.');
        }

        setSchedules(schedules.filter(s => s.schedule_id !== scheduleId));
        alert('Kural başarıyla silindi.');
    } catch (error) {
        alert(`Hata: ${error.message}`);
    }
  }

  if (isLoading) return <p>Yükleniyor...</p>;

  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Müsaitlik Takvimini Yönet</h1>
        <Link to="/dashboard/resources" className="text-blue-500 hover:underline">
          &larr; Varlık Listesine Geri Dön
        </Link>
      </div>

      <div className="mb-8 bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Mevcut Kurallar</h2>
        {schedules.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {schedules.map(schedule => (
              <li key={schedule.schedule_id} className="py-3 flex justify-between items-center">
                <div className="flex flex-col">
                    <span className="font-semibold">
                      {schedule.type === 'REGULAR' ? schedule.day_of_week : new Date(schedule.specific_date + 'T00:00:00').toLocaleDateString('tr-TR')}
                    </span>
                    <span className="text-sm text-gray-600">
                      {schedule.start_time.slice(0,5)} - {schedule.end_time.slice(0,5)}
                    </span>
                </div>
                <div className="flex items-center space-x-4">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${schedule.is_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                        {schedule.is_available ? 'Müsait' : 'Kapalı'}
                    </span>
                    <button onClick={() => handleDelete(schedule.schedule_id)} className="text-red-500 hover:text-red-700">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 012 0v6a1 1 0 11-2 0V8z" clipRule="evenodd" /></svg>
                    </button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>Bu varlık için henüz bir müsaitlik kuralı eklenmemiş.</p>
        )}
      </div>

      {/* --- YENİ KURAL EKLEME FORMU (TAM HALİ) --- */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Yeni Kural Ekle</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 font-bold mb-2">Kural Tipi</label>
            <select value={ruleType} onChange={(e) => setRuleType(e.target.value)} className="w-full p-2 border rounded">
              <option value="REGULAR">Haftanın Günü (Tekrarlayan)</option>
              <option value="EXCEPTION">Belirli Bir Tarih (İstisna)</option>
            </select>
          </div>

          {ruleType === 'REGULAR' ? (
            <div>
              <label className="block text-gray-700 font-bold mb-2">Gün Seç</label>
              <select value={dayOfWeek} onChange={(e) => setDayOfWeek(e.target.value)} className="w-full p-2 border rounded">
                <option value="MONDAY">Pazartesi</option>
                <option value="TUESDAY">Salı</option>
                <option value="WEDNESDAY">Çarşamba</option>
                <option value="THURSDAY">Perşembe</option>
                <option value="FRIDAY">Cuma</option>
                <option value="SATURDAY">Cumartesi</option>
                <option value="SUNDAY">Pazar</option>
              </select>
            </div>
          ) : (
            <div>
              <label className="block text-gray-700 font-bold mb-2">Tarih Seç</label>
              <input type="date" value={specificDate} onChange={(e) => setSpecificDate(e.target.value)} className="w-full p-2 border rounded" />
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 font-bold mb-2">Başlangıç Saati</label>
              <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} className="w-full p-2 border rounded" />
            </div>
            <div>
              <label className="block text-gray-700 font-bold mb-2">Bitiş Saati</label>
              <input type="time" value={endTime} onChange={(e) => setEndTime(e.target.value)} className="w-full p-2 border rounded" />
            </div>
          </div>

          <div>
            <label className="flex items-center space-x-2">
              <input type="checkbox" checked={isAvailable} onChange={(e) => setIsAvailable(e.target.checked)} className="h-5 w-5 rounded border-gray-300 text-teal-600 focus:ring-teal-500" />
              <span>Bu saatlerde müsait</span>
            </label>
          </div>

          <div className="flex justify-end">
            <button type="submit" className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
              Kuralı Ekle
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AvailabilityPage;
