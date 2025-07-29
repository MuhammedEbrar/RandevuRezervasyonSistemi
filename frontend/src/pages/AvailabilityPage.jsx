// src/pages/AvailabilityPage.jsx
import React from 'react';
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getAvailability, createAvailability, deleteAvailability } from '../services/api'; // Yeni import

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

  // Mevcut kuralları çeken fonksiyon
  const loadSchedules = async () => {
    setIsLoading(true);
    try {
      const data = await getAvailability(resourceId);
      setSchedules(data);
    } catch (error) {
      alert(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSchedules();
  }, [resourceId]);

  const handleDelete = async (scheduleId) => {
    if (!window.confirm('Bu kuralı silmek istediğinize emin misiniz?')) return;
    try {
      await deleteAvailability(resourceId, scheduleId);
      // Listeyi anında güncelle
      setSchedules(schedules.filter(s => s.schedule_id !== scheduleId));
      alert('Kural başarıyla silindi.');
    } catch (error) {
      alert(`Hata: ${error.message}`);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const newSchedule = {
      type: ruleType,
      day_of_week: ruleType === 'REGULAR' ? dayOfWeek : null,
      specific_date: ruleType === 'EXCEPTION' ? specificDate : null,
      start_time: startTime,
      end_time: endTime,
      is_available: isAvailable,
    };

    try {
      const createdSchedule = await createAvailability(resourceId, newSchedule);
      // Listeyi anında güncelle
      setSchedules([...schedules, createdSchedule]);
      alert('Kural başarıyla eklendi.');
    } catch (error) {
      alert(`Hata: ${error.message}`);
    }
  };

  if (isLoading) return <p>Yükleniyor...</p>;

  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Müsaitlik Takvimini Yönet</h1>
        <Link to="/dashboard/resources" className="text-blue-500 hover:underline">
          &larr; Varlık Listesine Geri Dön
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Mevcut Kuralları Listeleme */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Mevcut Kurallar</h2>
          {schedules.length > 0 ? (
            <ul className="divide-y divide-gray-200">
              {schedules.map(schedule => (
                <li key={schedule.schedule_id} className="py-3 flex justify-between items-center">
                  <div>
                    <span className="font-bold">{schedule.day_of_week || new Date(schedule.specific_date + 'T00:00:00').toLocaleDateString()}</span>
                    <span className="text-gray-600 ml-2">{schedule.start_time.slice(0,5)} - {schedule.end_time.slice(0,5)}</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${schedule.is_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {schedule.is_available ? 'Müsait' : 'Kapalı'}
                    </span>
                    <button onClick={() => handleDelete(schedule.schedule_id)} className="text-gray-400 hover:text-red-600">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p>Bu varlık için henüz bir müsaitlik kuralı eklenmemiş.</p>
          )}
        </div>

        {/* Yeni Kural Ekleme Formu */}
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
                <input type="date" value={specificDate} onChange={(e) => setSpecificDate(e.target.value)} className="w-full p-2 border rounded" required/>
              </div>
            )}
            
            <div className="flex space-x-4">
              <div className="w-1/2">
                <label className="block text-gray-700 font-bold mb-2">Başlangıç Saati</label>
                <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} className="w-full p-2 border rounded" required/>
              </div>
              <div className="w-1/2">
                <label className="block text-gray-700 font-bold mb-2">Bitiş Saati</label>
                <input type="time" value={endTime} onChange={(e) => setEndTime(e.target.value)} className="w-full p-2 border rounded" required/>
              </div>
            </div>

            <div>
              <label className="flex items-center space-x-2">
                <input type="checkbox" checked={isAvailable} onChange={(e) => setIsAvailable(e.target.checked)} className="h-5 w-5"/>
                <span>Bu saatlerde müsait</span>
              </label>
            </div>

            <div className="pt-2">
              <button type="submit" className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded">
                Kuralı Ekle
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default AvailabilityPage;
