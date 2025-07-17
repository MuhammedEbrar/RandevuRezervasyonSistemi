import React from 'react';
import { useNavigate } from 'react-router-dom';

// 1. Backend'den gelecek verilere benzeyen sahte bir veri oluşturalım.
const mockResources = [
  { id: 1, name: 'Halı Saha 1', type: 'SPACE', location: 'Merkez', is_active: true },
  { id: 2, name: 'Tenis Dersi', type: 'SERVICE', location: 'Kort 3', is_active: true },
  { id: 3, name: 'Toplantı Odası A', type: 'SPACE', location: 'Plaza Kat 5', is_active: false },
  { id: 4, name: 'Online Yoga Seansı', type: 'SERVICE', location: 'Zoom', is_active: true },
];

function ResourceListPage() {
  const navigate = useNavigate();
  return (
    <div className="p-4 sm:p-6 md:p-8 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-800">Varlıklarım / Hizmetlerim</h1>
          <button 
            onClick={() => navigate('/dashboard/resources/new')}
            className="bg-teal-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-teal-600 transition-colors shadow-md">
            + Yeni Varlık Ekle
          </button>
        </div>

        {/* Varlıkları listeleyeceğimiz tablo */}
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <table className="min-w-full leading-normal">
            <thead>
              <tr className="border-b-2 border-gray-200 bg-gray-100">
                <th className="px-5 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Varlık Adı
                </th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Türü
                </th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Durum
                </th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Eylemler
                </th>
              </tr>
            </thead>
            <tbody>
              {/* Sahte verileri burada döngüye alıp her biri için bir satır oluşturalım */}
              {mockResources.map((resource) => (
                <tr key={resource.id} className="hover:bg-gray-50">
                  <td className="px-5 py-5 border-b border-gray-200 text-sm">
                    <p className="text-gray-900 whitespace-no-wrap font-semibold">{resource.name}</p>
                    <p className="text-gray-600 whitespace-no-wrap text-xs">{resource.location}</p>
                  </td>
                  <td className="px-5 py-5 border-b border-gray-200 text-sm">
                    <p className="text-gray-900 whitespace-no-wrap">
                      {resource.type === 'SPACE' ? 'Mekan' : 'Hizmet'}
                    </p>
                  </td>
                  <td className="px-5 py-5 border-b border-gray-200 text-sm">
                    <span className={`relative inline-block px-3 py-1 font-semibold leading-tight ${
                        resource.is_active ? 'text-green-900' : 'text-red-900'
                      }`}>
                      <span aria-hidden className={`absolute inset-0 ${
                          resource.is_active ? 'bg-green-200' : 'bg-red-200'
                        } opacity-50 rounded-full`}></span>
                      <span className="relative">{resource.is_active ? 'Aktif' : 'Pasif'}</span>
                    </span>
                  </td>
                  <td className="px-5 py-5 border-b border-gray-200 text-sm">
                     <button className="text-indigo-600 hover:text-indigo-900 font-medium">Düzenle</button>
                     <button className="text-red-600 hover:text-red-900 ml-4 font-medium">Sil</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default ResourceListPage;