import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import AdminDashboard from './components/AdminDashboard';
import UploadMinute from './components/UploadMinute';
import History from './components/History';
import MinuteDetail from './components/MinuteDetail';
import LiveTranscription from './components/LiveTranscription';
import { authService } from './services/api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      authService.getCurrentUser()
        .then(userData => {
          setUser(userData);
          setLoading(false);
        })
        .catch(() => {
          localStorage.removeItem('token');
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="cyber-loader"></div>
        <p>Inicializando sistema...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={
            user ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />
          } />
          <Route path="/register" element={
            user ? <Navigate to="/dashboard" /> : <Register onLogin={handleLogin} />
          } />
          <Route path="/dashboard" element={
            user ? <Dashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />
          } />
          <Route path="/upload" element={
            user ? <UploadMinute user={user} onLogout={handleLogout} /> : <Navigate to="/login" />
          } />
          <Route path="/history" element={
            user ? <History user={user} onLogout={handleLogout} /> : <Navigate to="/login" />
          } />
          <Route path="/live" element={
            user ? <LiveTranscription user={user} onLogout={handleLogout} /> : <Navigate to="/login" />
          } />
          <Route path="/minute/:id" element={
            user ? <MinuteDetail user={user} onLogout={handleLogout} /> : <Navigate to="/login" />
          } />
          <Route path="/admin" element={
            user && user.is_admin ? <AdminDashboard user={user} onLogout={handleLogout} /> : <Navigate to="/dashboard" />
          } />
          <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
