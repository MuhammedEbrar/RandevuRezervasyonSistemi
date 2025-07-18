// src/components/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';

// Bu component, 'children' adında özel bir prop alır.
// Bu, <ProtectedRoute>...</ProtectedRoute> etiketleri arasına yazdığımız component'lerdir.
const ProtectedRoute = ({ children }) => {
  // 1. Tarayıcı hafızasından token'ı kontrol et
    const token = localStorage.getItem('userToken');

  // 2. Eğer token yoksa, kullanıcıyı giriş sayfasına yönlendir
    if (!token) {
    // Navigate component'i, kullanıcıyı belirtilen yola programatik olarak yönlendirir.
    return <Navigate to="/login" replace />;
    }

  // 3. Eğer token varsa, hiçbir şey yapma ve arasına yazılan component'in
  //    (yani children'ın) normal şekilde ekrana çizilmesine izin ver.
    return children;
};

export default ProtectedRoute;