    // src/App.jsx
    import { Routes, Route, Navigate } from 'react-router-dom';
    import AuthPage from './pages/AuthPage';
    import DashboardPage from './pages/DashboardPage';
    import ResourceListPage from './pages/ResourceListPage';
    import CreateResourcePage from './pages/CreateResourcePage';
    import ResourceEditPage from './pages/ResourceEditPage';
    import AvailabilityPage from './pages/AvailabilityPage';
    import ResourceDetailPage from './pages/ResourceDetailPage';
    import MyBookingsPage from './pages/MyBookingsPage'; // Yeni import
    import ProtectedRoute from './components/ProtectedRoute';

    function App() {
      const token = localStorage.getItem('userToken');

      return (
        <Routes>
          {/* Herkese Açık Rotalar */}
          <Route path="/login" element={<AuthPage />} />
          <Route path="/register" element={<AuthPage />} />
          <Route path="/resources/:resourceId" element={<ResourceDetailPage />} />

          {/* Korumalı Rotalar */}
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/dashboard/resources" element={<ProtectedRoute><ResourceListPage /></ProtectedRoute>} />
          <Route path="/dashboard/resources/new" element={<ProtectedRoute><CreateResourcePage /></ProtectedRoute>} />
          <Route path="/dashboard/resources/edit/:resourceId" element={<ProtectedRoute><ResourceEditPage /></ProtectedRoute>} />
          <Route path="/dashboard/resources/availability/:resourceId" element={<ProtectedRoute><AvailabilityPage /></ProtectedRoute>} />
          <Route path="/my-bookings" element={<ProtectedRoute><MyBookingsPage /></ProtectedRoute>} /> {/* Yeni Rota */}

          {/* Varsayılan Yönlendirme */}
          <Route path="*" element={token ? <Navigate to="/dashboard" /> : <Navigate to="/login" />} />
        </Routes>
      );
    }

    export default App;
    