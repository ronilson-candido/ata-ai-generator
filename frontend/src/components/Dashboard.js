import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import { minutesService } from '../services/api';
import './Dashboard.css';

function Dashboard({ user, onLogout }) {
  const [recentMinutes, setRecentMinutes] = useState([]);
  const [stats, setStats] = useState({ total: 0, totalTime: 0 });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const minutes = await minutesService.getMyMinutes(0, 5);
      setRecentMinutes(minutes);
      
      const allMinutes = await minutesService.getMyMinutes(0, 1000);
      const totalTime = allMinutes.reduce((sum, m) => sum + (m.processing_time || 0), 0);
      setStats({
        total: allMinutes.length,
        totalTime: totalTime
      });
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="dashboard-page">
      <Navbar user={user} onLogout={onLogout} />
      
      <div className="dashboard-container">
        <div className="dashboard-header">
          <div className="dashboard-title-section">
            <img src="/logo.svg" alt="Cyber Lab" className="dashboard-logo" />
            <div>
              <h1 className="glow-text">BEM-VINDO, {user.username.toUpperCase()}</h1>
              <p className="subtitle">Sistema de Transcrição e Geração de Atas com IA</p>
            </div>
          </div>
          <div className="dashboard-actions">
            <button 
              onClick={() => navigate('/live')} 
              className="cyber-button-secondary"
            >
              AO VIVO
            </button>
            <button 
              onClick={() => navigate('/upload')} 
              className="cyber-button"
            >
              + NOVA ATA
            </button>
          </div>
        </div>

        <div className="stats-grid grid-3">
          <div className="stat-card cyber-card animate-slide-up">
            <div className="stat-icon">📄</div>
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Atas Geradas</div>
          </div>

          <div className="stat-card cyber-card animate-slide-up" style={{animationDelay: '0.1s'}}>
            <div className="stat-icon">⏱️</div>
            <div className="stat-value">{Math.round(stats.totalTime / 60)}min</div>
            <div className="stat-label">Tempo Processado</div>
          </div>

          <div className="stat-card cyber-card animate-slide-up" style={{animationDelay: '0.2s'}}>
            <div className="stat-icon">✅</div>
            <div className="stat-value">100%</div>
            <div className="stat-label">Taxa de Sucesso</div>
          </div>
        </div>

        <div className="recent-section">
          <div className="section-header">
            <h2>Atas Recentes</h2>
            <button 
              onClick={() => navigate('/history')} 
              className="cyber-button-secondary"
            >
              VER TODAS
            </button>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="cyber-loader"></div>
              <p>Carregando...</p>
            </div>
          ) : recentMinutes.length === 0 ? (
            <div className="empty-state cyber-card">
              <div className="empty-icon">📋</div>
              <h3>Nenhuma ata gerada ainda</h3>
              <p>Comece fazendo upload de um arquivo de áudio ou vídeo</p>
              <button 
                onClick={() => navigate('/upload')} 
                className="cyber-button"
                style={{marginTop: '20px'}}
              >
                CRIAR PRIMEIRA ATA
              </button>
            </div>
          ) : (
            <div className="minutes-grid">
              {recentMinutes.map((minute, index) => (
                <div 
                  key={minute.id} 
                  className="minute-card cyber-card"
                  style={{animationDelay: `${index * 0.1}s`}}
                  onClick={() => navigate(`/minute/${minute.id}`)}
                >
                  <div className="minute-header">
                    <h3>{minute.title}</h3>
                    <span className="minute-date">{formatDate(minute.created_at)}</span>
                  </div>
                  <div className="minute-info">
                    <div className="info-item">
                      <span className="info-label">Arquivo:</span>
                      <span className="info-value">{minute.original_filename}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Duração:</span>
                      <span className="info-value">{Math.round(minute.audio_duration)}s</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Processamento:</span>
                      <span className="info-value">{Math.round(minute.processing_time)}s</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
