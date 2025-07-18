// src/hooks/useAuth.js
import { useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

export const useAuth = () => {
  const [auth, setAuth] = useState({ token: null, user: null });

  useEffect(() => {
    const token = localStorage.getItem('userToken');
    if (token) {
      try {
        const decodedUser = jwtDecode(token);
        setAuth({ token, user: decodedUser });
      } catch (error) {
        console.error("Geçersiz token:", error);
        setAuth({ token: null, user: null });
      }
    }
  }, []);

  return auth;
};