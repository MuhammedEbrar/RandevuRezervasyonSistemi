import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function CreateResourcePage() {
  const navigate = useNavigate();

  // Formdaki her bir alan için state'leri tanımlayalım
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState('SERVICE'); // Varsayılan olarak 'Hizmet' seçili

  const handleSubmit = (event) => {
    event.preventDefault(); // Formun sayfayı yenilemesini engelle
    const newResource = { name, description, type };
    console.log('Yeni Varlık Bilgileri:', newResource);
    alert('Yeni varlık konsola yazdırıldı! (Henüz backend yok)');
    // İleride burada backend'e istek atılacak
  };

  return (
    <div className="p-4 sm:p-6 md:p-8 bg-gray-50 min-h-screen">
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-6">Yeni Varlık / Hizmet Oluştur</h1>

        <form onSubmit={handleSubmit}>
          {/* Varlık Adı */}
          <div className="mb-4">
            <label htmlFor="name" className="block text-gray-700 font-bold mb-2">Varlık Adı</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              placeholder="Örn: Halı Saha 1, Yoga Dersi"
              required
            />
          </div>

          {/* Açıklama */}
          <div className="mb-4">
            <label htmlFor="description" className="block text-gray-700 font-bold mb-2">Açıklama</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
              rows="4"
              placeholder="Varlık veya hizmet hakkında kısa bir açıklama..."
            ></textarea>
          </div>

          {/* Varlık Türü */}
          <div className="mb-6">
            <label htmlFor="type" className="block text-gray-700 font-bold mb-2">Türü</label>
            <select
              id="type"
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
            >
              <option value="SERVICE">Hizmet (Örn: Ders, Danışmanlık)</option>
              <option value="SPACE">Mekan (Örn: Saha, Oda, Masa)</option>
            </select>
          </div>

          {/* Butonlar */}
          <div className="flex items-center justify-end gap-4">
             <button 
                type="button" 
                onClick={() => navigate('/dashboard/resources')}
                className="bg-gray-200 text-gray-800 font-bold py-2 px-6 rounded-lg hover:bg-gray-300 transition-colors">
               İptal
             </button>
             <button 
                type="submit"
                className="bg-teal-500 text-white font-bold py-2 px-6 rounded-lg hover:bg-teal-600 transition-colors">
               Oluştur
             </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateResourcePage;