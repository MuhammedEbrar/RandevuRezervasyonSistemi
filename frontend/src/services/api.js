// src/services/api.js

// API'ın ana adresini .env dosyasından oku
const API_URL = import.meta.env.VITE_API_BASE_URL;

// Hata yönetimini merkezileştiren yardımcı fonksiyon
const handleResponse = async (response) => {
  if (!response.ok) {
    // Backend'den gelen hata mesajını ayrıştır
    const errorData = await response.json().catch(() => ({ detail: 'Bilinmeyen bir sunucu hatası.' }));
    // Hata mesajını fırlat, böylece component'teki catch bloğu yakalayabilir
    throw new Error(JSON.stringify(errorData.detail) || 'Bir hata oluştu.');
  }
  // Eğer yanıt boşsa (204 No Content gibi), null döndür
  if (response.status === 204) {
    return null;
  }
  return response.json();
};

// Tüm API istekleri için temel bir fonksiyon
const apiFetch = async (endpoint, options = {}) => {
  const token = localStorage.getItem('userToken');
  const headers = {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true', // ngrok uyarısını atlamak için
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  return handleResponse(response);
};

// --- AUTH ENDPOINTS ---
export const loginUser = async (email, password) => {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'ngrok-skip-browser-warning': 'true',
        },
        body: new URLSearchParams({ 'username': email, 'password': password }),
    });
    return handleResponse(response);
};
export const registerUser = (userData) => apiFetch('/auth/register', { method: 'POST', body: JSON.stringify(userData) });

// --- RESOURCE ENDPOINTS ---
export const getResources = () => apiFetch('/resources/');
export const getResourceById = (resourceId) => apiFetch(`/resources/${resourceId}`);
export const createResource = (resourceData) => apiFetch('/resources/', { method: 'POST', body: JSON.stringify(resourceData) });
export const updateResource = (resourceId, resourceData) => apiFetch(`/resources/${resourceId}`, { method: 'PUT', body: JSON.stringify(resourceData) });
export const deleteResource = (resourceId) => apiFetch(`/resources/${resourceId}`, { method: 'DELETE' });

// --- AVAILABILITY ENDPOINTS --- (İSİMLER DÜZELTİLDİ)
export const getAvailability = (resourceId) => apiFetch(`/resources/${resourceId}/availability/`);
export const createAvailability = (resourceId, scheduleData) => apiFetch(`/resources/${resourceId}/availability/`, { method: 'POST', body: JSON.stringify(scheduleData) });
export const deleteAvailability = (resourceId, scheduleId) => apiFetch(`/resources/${resourceId}/availability/${scheduleId}`, { method: 'DELETE' });

// --- BOOKING ENDPOINTS ---
export const getAvailableSlots = (resourceId, dateString) => apiFetch(`/resources/${resourceId}/availability/available_slots?start_date=${dateString}&end_date=${dateString}`);
export const calculatePrice = (resourceId, startTime, endTime) => apiFetch('/bookings/calculate_price', { method: 'POST', body: JSON.stringify({ resource_id: resourceId, start_time: startTime, end_time: endTime }) });
export const createBooking = (bookingData) => apiFetch('/bookings/', { method: 'POST', body: JSON.stringify(bookingData) });
export const getMyBookings = () => apiFetch('/bookings/customer');
