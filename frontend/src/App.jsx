// src/App.jsx
import { Routes, Route } from 'react-router-dom';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import ResourceListPage from './pages/ResourceListPage';
import CreateResourcePage from './pages/CreateResourcePage';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage />} />
      <Route path="/register" element={<AuthPage />} />
      <Route path="/dashboard" element={<DashboardPage />} /> {/* Yeni Rota */}
      <Route path="/dashboard/resources" element={<ResourceListPage />} />
      <Route path="/dashboard/resources/new" element={<CreateResourcePage />} />
      <Route path="/*" element={<AuthPage />} />
    </Routes>
  );
}
export default App;