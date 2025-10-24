// src/pages/ResourceListPage.jsx
import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { getResources, deleteResource } from '../services/api';
import Navbar from '../components/Navbar';

function ResourceListPage() {
  const [resources, setResources] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const location = useLocation();

  // Business owner dashboard'tan mı yoksa public sayfadan mı geldiğimizi kontrol et
  const isOwnerView = location.pathname.startsWith('/dashboard');

  // Veri çekme fonksiyonu
  const loadResources = async () => {
    setIsLoading(true);
    try {
      const data = await getResources();
      setResources(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Component yüklendiğinde varlıkları çek
  useEffect(() => {
    loadResources();
  }, []);

  const handleDelete = async (resourceId) => {
    if (!window.confirm('Bu varlığı silmek istediğinize emin misiniz?')) {
      return;
    }

    try {
      await deleteResource(resourceId);
      // Silme başarılıysa, listeden anında kaldır
      setResources(resources.filter(resource => resource.resource_id !== resourceId));
      alert('Varlık başarıyla silindi.');
    } catch (err) {
      alert(`Hata: ${err.message}`);
    }
  };

  if (isLoading) {
    return (
      <>
        {!isOwnerView && <Navbar />}
        <div className="text-center p-20">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Yükleniyor...</p>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        {!isOwnerView && <Navbar />}
        <div className="text-center p-10 text-red-500">Hata: {error}</div>
      </>
    );
  }

  return (
    <>
      {!isOwnerView && <Navbar />}
      <div className="container mx-auto p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">
            {isOwnerView ? 'Varlıklarım' : 'Hizmetler ve Mekanlar'}
          </h1>
          {isOwnerView && (
            <Link
              to="/dashboard/resources/new"
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
            >
              + Yeni Varlık Ekle
            </Link>
          )}
        </div>

        {resources.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-lg shadow-md">
            <p className="text-gray-600 text-lg">
              {isOwnerView
                ? 'Henüz bir varlık eklemediniz.'
                : 'Henüz kayıtlı hizmet veya mekan bulunmamaktadır.'}
            </p>
          </div>
        ) : (
          <div className="bg-white shadow-md rounded-lg">
            <ul className="divide-y divide-gray-200">
              {resources.map(resource => (
                <li
                  key={resource.resource_id}
                  className="p-4 flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4 hover:bg-gray-50"
                >
                  {/* Görsel */}
                  {resource.images && resource.images.length > 0 ? (
                    <img
                      src={
                        resource.images[0].startsWith('/')
                          ? `${import.meta.env.VITE_API_BASE_URL}${resource.images[0]}`
                          : resource.images[0]
                      }
                      alt={resource.name}
                      className="w-24 h-24 object-cover rounded-md flex-shrink-0"
                    />
                  ) : (
                    <div className="w-24 h-24 bg-gray-200 rounded-md flex items-center justify-center text-gray-400 flex-shrink-0">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-10 w-10"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                        />
                      </svg>
                    </div>
                  )}

                  {/* Bilgiler */}
                  <div className="flex-grow">
                    <p className="font-semibold text-lg text-gray-800">{resource.name}</p>
                    <p className="text-sm text-gray-600 truncate">{resource.description}</p>
                    <div className="flex items-center mt-2 space-x-4">
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {resource.type}
                      </span>
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          resource.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {resource.is_active ? 'Aktif' : 'Pasif'}
                      </span>
                    </div>
                  </div>

                  {/* Butonlar */}
                  <div className="flex space-x-2 flex-shrink-0">
                    {isOwnerView ? (
                      <>
                        {/* Business Owner Butonları */}
                        <Link
                          to={`/dashboard/resources/edit/${resource.resource_id}`}
                          className="text-sm bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-3 rounded"
                        >
                          Düzenle
                        </Link>
                        <button
                          onClick={() => handleDelete(resource.resource_id)}
                          className="text-sm bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-3 rounded"
                        >
                          Sil
                        </button>
                        <Link
                          to={`/dashboard/resources/availability/${resource.resource_id}`}
                          className="text-sm bg-purple-500 hover:bg-purple-600 text-white font-bold py-2 px-3 rounded text-center"
                        >
                          Takvimi Yönet
                        </Link>
                      </>
                    ) : (
                      <>
                        {/* Müşteri Butonları */}
                        <Link
                          to={`/resources/${resource.resource_id}`}
                          className="text-sm bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                        >
                          Detayları Gör & Rezervasyon Yap
                        </Link>
                      </>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </>
  );
}

export default ResourceListPage;
