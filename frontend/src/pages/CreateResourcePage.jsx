// src/pages/CreateResourcePage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createResource } from '../services/api'; // Yeni import

function CreateResourcePage() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState('HIZMET');
  const [capacity, setCapacity] = useState(1);
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('');
  const [country, setCountry] = useState('');
  const [zipCode, setZipCode] = useState('');
  const [tags, setTags] = useState('');
  const [images, setImages] = useState('');
  const [cancellationPolicy, setCancellationPolicy] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();

    const newResource = {
      name,
      description,
      type,
      capacity: type === 'MEKAN' ? capacity : null,
      location: {
        address,
        city,
        country,
        zip_code: zipCode,
      },
      tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag),
      images: images.split(',').map(img => img.trim()).filter(img => img),
      cancellation_policy: cancellationPolicy,
    };
    
    try {
      // Karmaşık fetch bloğu yerine tek satırlık fonksiyon çağrısı
      await createResource(newResource);
      alert('Varlık başarıyla oluşturuldu!');
      navigate('/dashboard/resources');
    } catch (error) {
      alert(`Hata: ${error.message}`);
    }
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Yeni Varlık Ekle</h1>
      <form onSubmit={handleSubmit} className="max-w-lg bg-white p-8 shadow-md rounded-lg space-y-4">
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="name">Varlık Adı</label>
          <input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)} className="w-full p-2 border rounded" required />
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="description">Açıklama</label>
          <textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} className="w-full p-2 border rounded" />
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="type">Varlık Tipi</label>
          <select id="type" value={type} onChange={(e) => setType(e.target.value)} className="w-full p-2 border rounded">
            <option value="HIZMET">Hizmet (HIZMET)</option>
            <option value="MEKAN">Mekan (MEKAN)</option>
          </select>
        </div>
        {type === 'MEKAN' && (
          <div>
            <label className="block text-gray-700 font-bold mb-2" htmlFor="capacity">Kapasite</label>
            <input id="capacity" type="number" value={capacity} onChange={(e) => setCapacity(parseInt(e.target.value, 10))} className="w-full p-2 border rounded" min="1" />
          </div>
        )}
        
        <hr/>
        <p className="font-bold text-gray-700">Konum Bilgileri</p>
        <div>
          <label className="block text-gray-700 mb-1" htmlFor="address">Adres</label>
          <input id="address" type="text" value={address} onChange={(e) => setAddress(e.target.value)} className="w-full p-2 border rounded" />
        </div>
        <div className="grid grid-cols-3 gap-4">
            <div>
                <label className="block text-gray-700 mb-1" htmlFor="city">Şehir</label>
                <input id="city" type="text" value={city} onChange={(e) => setCity(e.target.value)} className="w-full p-2 border rounded" />
            </div>
            <div>
                <label className="block text-gray-700 mb-1" htmlFor="country">Ülke</label>
                <input id="country" type="text" value={country} onChange={(e) => setCountry(e.target.value)} className="w-full p-2 border rounded" />
            </div>
            <div>
                <label className="block text-gray-700 mb-1" htmlFor="zipCode">Posta Kodu</label>
                <input id="zipCode" type="text" value={zipCode} onChange={(e) => setZipCode(e.target.value)} className="w-full p-2 border rounded" />
            </div>
        </div>
        <hr/>
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="tags">Etiketler (Virgülle ayırın)</label>
          <input id="tags" type="text" value={tags} onChange={(e) => setTags(e.target.value)} className="w-full p-2 border rounded" placeholder="pilates, spor, özel ders"/>
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="images">Resim URL'leri (Virgülle ayırın)</label>
          <input id="images" type="text" value={images} onChange={(e) => setImages(e.target.value)} className="w-full p-2 border rounded" placeholder="https://.../resim1.jpg, https://.../resim2.jpg"/>
        </div>
        <div>
          <label className="block text-gray-700 font-bold mb-2" htmlFor="cancellation_policy">İptal Politikası</label>
          <textarea id="cancellation_policy" value={cancellationPolicy} onChange={(e) => setCancellationPolicy(e.target.value)} className="w-full p-2 border rounded" />
        </div>

        <div className="flex justify-end pt-4">
          <button type="submit" className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
            Varlığı Oluştur
          </button>
        </div>
      </form>
    </div>
  );
}

export default CreateResourcePage;
