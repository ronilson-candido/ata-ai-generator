import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import { minutesService } from '../services/api';
import './MinuteDetail.css';

function MinuteDetail({ user, onLogout }) {
  const { id } = useParams();
  const [minute, setMinute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('ata');
  const navigate = useNavigate();

  useEffect(() => {
    loadMinute();
  }, [id]);

  const loadMinute = async () => {
    try {
      const data = await minutesService.getMinute(id);
      setMinute(data);
    } catch (error) {
      console.error('Error loading minute:', error);
      navigate('/history');
    } finally {
      setLoading(false);
    }
  };

  const downloadMarkdown = () => {
    const blob = new Blob([minute.structured_minutes], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${minute.title}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadTranscription = () => {
    const blob = new Blob([minute.transcription], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${minute.title}_transcricao.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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

  if (loading) {
    return (
      <div className="minute-detail-page">
        <Navbar user={user} onLogout={onLogout} />
        <div className="loading-state">
          <div className="cyber-loader"></div>
          <p>Carregando ata...</p>
        </div>
      </div>
    );
  }

  if (!minute) {
    return null;
  }

  return (
    <div className="minute-detail-page">
      <Navbar user={user} onLogout={onLogout} />
      
      <div className="minute-detail-container">
        <div className="detail-header">
          <button onClick={() => navigate('/history')} className="back-btn">
            ← Voltar
          </button>
          <h1 className="glow-text">{minute.title}</h1>
          <p className="detail-date">Gerado em {formatDate(minute.created_at)}</p>
        </div>

        <div className="detail-stats grid-4">
          <div className="stat-item cyber-card">
            <span className="stat-icon">📁</span>
            <span className="stat-label">Arquivo</span>
            <span className="stat-value">{minute.original_filename}</span>
          </div>
          <div className="stat-item cyber-card">
            <span className="stat-icon">⏱️</span>
            <span className="stat-label">Duração</span>
            <span className="stat-value">{Math.round(minute.audio_duration)}s</span>
          </div>
          <div className="stat-item cyber-card">
            <span className="stat-icon">⚡</span>
            <span className="stat-label">Processamento</span>
            <span className="stat-value">{Math.round(minute.processing_time)}s</span>
          </div>
          <div className="stat-item cyber-card">
            <span className="stat-icon">💾</span>
            <span className="stat-label">Tamanho</span>
            <span className="stat-value">{minute.file_size?.toFixed(2)} MB</span>
          </div>
        </div>

        <div className="content-section">
          <div className="tabs">
            <button
              className={`tab-btn ${activeTab === 'ata' ? 'active' : ''}`}
              onClick={() => setActiveTab('ata')}
            >
              📋 ATA ESTRUTURADA
            </button>
            <button
              className={`tab-btn ${activeTab === 'transcricao' ? 'active' : ''}`}
              onClick={() => setActiveTab('transcricao')}
            >
              📝 TRANSCRIÇÃO COMPLETA
            </button>
          </div>

          {activeTab === 'ata' ? (
            <div className="content-panel cyber-card">
              <div className="panel-header">
                <h2>Ata Estruturada</h2>
                <button onClick={downloadMarkdown} className="cyber-button">
                  ⬇️ BAIXAR MARKDOWN
                </button>
              </div>
              <div className="markdown-content">
                <pre>{minute.structured_minutes}</pre>
              </div>
            </div>
          ) : (
            <div className="content-panel cyber-card">
              <div className="panel-header">
                <h2>Transcrição Completa</h2>
                <button onClick={downloadTranscription} className="cyber-button">
                  ⬇️ BAIXAR TRANSCRIÇÃO
                </button>
              </div>
              <div className="transcription-content">
                <p>{minute.transcription}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MinuteDetail;
