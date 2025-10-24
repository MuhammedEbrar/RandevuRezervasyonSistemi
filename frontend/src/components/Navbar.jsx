// src/components/Navbar.jsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('userToken');
    localStorage.removeItem('userInfo');
    navigate('/login');
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  // User bilgisini al
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
  const isLoggedIn = !!localStorage.getItem('userToken');

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          {/* Logo / Ana Başlık */}
          <Link to="/resources" className="text-2xl font-bold hover:text-blue-200 transition-colors">
            Randevu Sistemi
          </Link>

          {/* Hamburger Menü Butonu (Mobil) */}
          <button
            onClick={toggleMenu}
            className="md:hidden focus:outline-none hover:bg-blue-700 p-2 rounded transition-colors"
            aria-label="Menüyü Aç/Kapa"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {isMenuOpen ? (
                <path d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>

          {/* Desktop Menü */}
          <div className="hidden md:flex items-center space-x-6">
            {isLoggedIn ? (
              <>
                <span className="text-sm">
                  Hoş geldin, <span className="font-semibold">{userInfo.full_name || userInfo.email}</span>
                </span>
                {/* <Link
                  to="/profile"
                  className="hover:text-blue-200 transition-colors"
                >
                  Profilim
                </Link> */}
                <Link
                  to="/my-bookings"
                  className="hover:text-blue-200 transition-colors"
                >
                  Rezervasyonlarım
                </Link>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded-lg transition-colors font-semibold"
                >
                  Çıkış Yap
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="hover:text-blue-200 transition-colors"
                >
                  Giriş Yap
                </Link>
                <Link
                  to="/register"
                  className="bg-green-500 hover:bg-green-600 px-4 py-2 rounded-lg transition-colors font-semibold"
                >
                  Kayıt Ol
                </Link>
              </>
            )}
          </div>
        </div>

        {/* Mobil Menü (Dropdown) */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-blue-500 pt-4">
            {isLoggedIn ? (
              <div className="flex flex-col space-y-3">
                <div className="text-sm pb-2 border-b border-blue-500">
                  Hoş geldin, <span className="font-semibold">{userInfo.full_name || userInfo.email}</span>
                </div>
                {/* <Link
                  to="/profile"
                  className="hover:bg-blue-700 px-4 py-2 rounded transition-colors"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Profilim
                </Link> */}
                <Link
                  to="/my-bookings"
                  className="hover:bg-blue-700 px-4 py-2 rounded transition-colors"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Rezervasyonlarım
                </Link>
                <button
                  onClick={() => {
                    handleLogout();
                    setIsMenuOpen(false);
                  }}
                  className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded transition-colors font-semibold text-left"
                >
                  Çıkış Yap
                </button>
              </div>
            ) : (
              <div className="flex flex-col space-y-3">
                <Link
                  to="/login"
                  className="hover:bg-blue-700 px-4 py-2 rounded transition-colors"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Giriş Yap
                </Link>
                <Link
                  to="/register"
                  className="bg-green-500 hover:bg-green-600 px-4 py-2 rounded transition-colors font-semibold"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Kayıt Ol
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
