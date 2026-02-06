import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import { minutesService } from '../services/api';
import './MinuteDetail.css';

function MinuteDetail({ user, onLogout }) {
  const { id } = useParams();
  const [minute, setMinute] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('ata');
  const [audioUrl, setAudioUrl] = useState(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [activeSegment, setActiveSegment] = useState(null);
  const audioRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadMinute();
  }, [id]);

  const loadMinute = async () => {
    try {
      const data = await minutesService.getMinute(id);
      setMinute(data);
      
      // Se tem áudio, carregar URL
      if (data.audio_path) {
        const audioUrl = `${process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}/minutes/${id}/audio`;
        setAudioUrl(audioUrl);
      }
    } catch (error) {
      console.error('Error loading minute:', error);
      navigate('/history');
    } finally {
      setLoading(false);
    }
  };

  const handleAudioTimeUpdate = () => {
    if (audioRef.current) {
      const time = audioRef.current.currentTime;
      setCurrentTime(time);
      
      // Encontrar segmento ativo baseado no tempo atual
      if (minute?.segments) {
        const active = minute.segments.find(seg => 
          time >= seg.start && time <= seg.end
        );
        setActiveSegment(active);
      }
    }
  };

  const handleSegmentClick = (segment) => {
    if (audioRef.current && segment) {
      audioRef.current.currentTime = segment.start;
      audioRef.current.play();
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
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

        {/* Player de Áudio */}
        {audioUrl && (
          <div className="audio-player-section cyber-card">
            <h3>🎵 Áudio da Reunião</h3>
            <div className="audio-player-controls">
              <audio
                ref={audioRef}
                src={audioUrl}
                controls
                onTimeUpdate={handleAudioTimeUpdate}
                className="audio-player"
              />
              <div className="audio-info">
                <span className="current-time">{formatTime(currentTime)}</span>
                <span className="separator">/</span>
                <span className="total-time">{formatTime(minute.audio_duration || 0)}</span>
              </div>
            </div>
            {activeSegment && (
              <div className="current-segment-display">
                <p className="segment-label">🎙️ Falando agora:</p>
                <p className="segment-text">"{activeSegment.text}"</p>
              </div>
            )}
          </div>
        )}

        <div className="detail-stats grid-4">
          <div className="stat-item cyber-card">
            <span className="stat-label">Arquivo</span>
            <span className="stat-value">{minute.original_filename}</span>
          </div>
          <div className="stat-item cyber-card">
            <span className="stat-label">Duração</span>
            <span className="stat-value">{Math.round(minute.audio_duration)}s</span>
          </div>
          <div className="stat-item cyber-card">
            <span className="stat-label">Processamento</span>
            <span className="stat-value">{Math.round(minute.processing_time)}s</span>
          </div>
          <div className="stat-item cyber-card">
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
              ATA ESTRUTURADA
            </button>
            <button
              className={`tab-btn ${activeTab === 'transcricao' ? 'active' : ''}`}
              onClick={() => setActiveTab('transcricao')}
            >
              TRANSCRIÇÃO COMPLETA
            </button>
            {minute.segments && minute.segments.length > 0 && (
              <button
                className={`tab-btn ${activeTab === 'timeline' ? 'active' : ''}`}
                onClick={() => setActiveTab('timeline')}
              >
                LINHA DO TEMPO
              </button>
            )}
          </div>

          {activeTab === 'ata' ? (
            <div className="content-panel cyber-card">
              <div className="panel-header">
                <h2>Ata Estruturada</h2>
                <button onClick={downloadMarkdown} className="cyber-button">
                  BAIXAR MARKDOWN
                </button>
              </div>
              <div className="markdown-content">
                <pre>{minute.structured_minutes}</pre>
              </div>
            </div>
          ) : activeTab === 'transcricao' ? (
            <div className="content-panel cyber-card">
              <div className="panel-header">
                <h2>Transcrição Completa</h2>
                <button onClick={downloadTranscription} className="cyber-button">
                  BAIXAR TRANSCRIÇÃO
                </button>
              </div>
              <div className="transcription-content">
                <p>{minute.transcription}</p>
              </div>
            </div>
          ) : (
            <div className="content-panel cyber-card">
              <div className="panel-header">
                <h2>Linha do Tempo com Minutagem</h2>
                <p className="timeline-hint">💡 Clique em qualquer trecho para ouvir o áudio daquele momento</p>
              </div>
              <div className="timeline-content">
                {minute.segments && minute.segments.map((segment, index) => (
                  <div
                    key={index}
                    className={`timeline-segment ${activeSegment?.start === segment.start ? 'active' : ''}`}
                    onClick={() => handleSegmentClick(segment)}
                  >
                    <div className="segment-time">
                      <span className="time-badge">{formatTime(segment.start)}</span>
                      <span className="time-separator">→</span>
                      <span className="time-badge">{formatTime(segment.end)}</span>
                    </div>
                    <div className="segment-text-content">
                      <p>{segment.text}</p>
                    </div>
                    {activeSegment?.start === segment.start && (
                      <div className="playing-indicator">
                        <span className="playing-icon">▶️</span>
                        <span>Reproduzindo</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MinuteDetail;
