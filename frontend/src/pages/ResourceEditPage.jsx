// src/pages/ResourceEditPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

function ResourceEditPage() {
  const { resourceId } = useParams();
  const navigate = useNavigate();
  
  // formData'yı başlangıçta null yapalım ki veri gelmeden formu çizmeye çalışmasın
  const [formData, setFormData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchResourceData = async () => {
      const token = localStorage.getItem('userToken');
      const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/resources/${resourceId}`;
      try {
        const response = await fetch(apiUrl, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Veri alınamadı.');

        const data = await response.json();
        
        // Gelen veriyi state'e doldur
        setFormData({
          name: data.name || '',
          description: data.description || '',
          type: data.type || 'HIZMET',
          capacity: data.capacity || 1,
          address: data.location?.address || '',
          city: data.location?.city || '',
          country: data.location?.country || '',
          zip_code: data.location?.zip_code || '',
          tags: (data.tags || []).join(', '),
          images: (data.images || []).join(', '),
          cancellation_policy: data.cancellation_policy || '',
        });
      } catch (error) {
        alert('Hata oluştu: ' + error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchResourceData();
  }, [resourceId]);

  // Formdaki her değişiklikte state'i güncelleyen fonksiyon
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Form gönderme fonksiyonu
  const handleSubmit = async (event) => {
    event.preventDefault();
    const token = localStorage.getItem('userToken');

    const resourceToUpdate = {
        name: formData.name, description: formData.description, type: formData.type,
        capacity: formData.type === 'MEKAN' ? parseInt(formData.capacity) : null,
        location: { address: formData.address, city: formData.city, country: formData.country, zip_code: formData.zip_code },
        tags: formData.tags.split(',').map(t => t.trim()).filter(Boolean),
        images: formData.images.split(',').map(i => i.trim()).filter(Boolean),
        cancellation_policy: formData.cancellation_policy,
    };
    
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/resources/${resourceId}`;
    try {
      const response = await fetch(apiUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(resourceToUpdate),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(JSON.stringify(errorData.detail) || 'Varlık güncellenemedi.');
      }
      
      alert('Varlık başarıyla güncellendi!');
      navigate('/dashboard/resources');
    } catch (error) {
      alert(`Hata: ${error.message}`);
    }
  };

  // Veri yüklenirken veya formData henüz doldurulmamışken bekleme ekranı göster
  if (isLoading || !formData) return <p className="text-center p-10">Yükleniyor...</p>;

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Varlığı Düzenle: {formData.name}</h1>
      <form onSubmit={handleSubmit} className="max-w-lg bg-white p-8 shadow-md rounded-lg space-y-4">
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="name">Varlık Adı</label>
          <input name="name" value={formData.name} onChange={handleChange} className="w-full p-2 border rounded" required />
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="description">Açıklama</label>
          <textarea name="description" value={formData.description} onChange={handleChange} className="w-full p-2 border rounded" />
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="type">Varlık Tipi</label>
          <select name="type" value={formData.type} onChange={handleChange} className="w-full p-2 border rounded">
            <option value="HIZMET">Hizmet</option>
            <option value="MEKAN">Mekan</option>
          </select>
        </div>
        {formData.type === 'MEKAN' && (
          <div>
            <label className="block text-gray-700 font-bold mb-2" htmlFor="capacity">Kapasite</label>
            <input type="number" name="capacity" value={formData.capacity} onChange={handleChange} className="w-full p-2 border rounded" min="1" />
          </div>
        )}
        <hr/>
        <p className="font-bold text-gray-700">Konum Bilgileri</p>
        <div>
            <label className="block text-gray-700 mb-1" htmlFor="address">Adres</label>
            <input name="address" value={formData.address} onChange={handleChange} className="w-full p-2 border rounded" />
        </div>
        <div className="grid grid-cols-3 gap-4">
            <div><label className="block text-gray-700 mb-1" htmlFor="city">Şehir</label><input name="city" value={formData.city} onChange={handleChange} className="w-full p-2 border rounded" /></div>
            <div><label className="block text-gray-700 mb-1" htmlFor="country">Ülke</label><input name="country" value={formData.country} onChange={handleChange} className="w-full p-2 border rounded" /></div>
            <div><label className="block text-gray-700 mb-1" htmlFor="zip_code">Posta Kodu</label><input name="zip_code" value={formData.zip_code} onChange={handleChange} className="w-full p-2 border rounded" /></div>
        </div>
        <hr/>
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="tags">Etiketler (Virgülle ayırın)</label>
          <input name="tags" value={formData.tags} onChange={handleChange} className="w-full p-2 border rounded" />
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="images">Resim URL'leri (Virgülle ayırın)</label>
          <input name="images" value={formData.images} onChange={handleChange} className="w-full p-2 border rounded" />
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="cancellation_policy">İptal Politikası</label>
          <textarea name="cancellation_policy" value={formData.cancellation_policy} onChange={handleChange} className="w-full p-2 border rounded" />
        </div>
        <div className="flex justify-end pt-4">
          <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Değişiklikleri Kaydet</button>
        </div>
      </form>
    </div>
  );
}

export default ResourceEditPage;

