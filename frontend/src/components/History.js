import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import { minutesService } from '../services/api';
import './History.css';

function History({ user, onLogout }) {
  const [minutes, setMinutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadMinutes();
  }, []);

  const loadMinutes = async () => {
    try {
      const data = await minutesService.getMyMinutes(0, 1000);
      setMinutes(data);
    } catch (error) {
      console.error('Error loading minutes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    
    if (window.confirm('Tem certeza que deseja excluir esta ata?')) {
      try {
        await minutesService.deleteMinute(id);
        setMinutes(minutes.filter(m => m.id !== id));
      } catch (error) {
        alert('Erro ao excluir ata');
      }
    }
  };

  const filteredMinutes = minutes.filter(minute =>
    minute.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    minute.original_filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
    <div className="history-page">
      <Navbar user={user} onLogout={onLogout} />
      
      <div className="history-container">
        <div className="history-header">
          <div>
            <h1 className="glow-text">HISTÓRICO DE ATAS</h1>
            <p className="subtitle">Todas as suas atas geradas com IA</p>
          </div>
          <button 
            onClick={() => navigate('/upload')} 
            className="cyber-button"
          >
            + NOVA ATA
          </button>
        </div>

        <div className="search-bar cyber-card">
          <input
            type="text"
            className="cyber-input"
            placeholder="Buscar por título ou arquivo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="cyber-loader"></div>
            <p>Carregando histórico...</p>
          </div>
        ) : filteredMinutes.length === 0 ? (
          <div className="empty-state cyber-card">
            <div className="empty-icon">📋</div>
            <h3>{searchTerm ? 'Nenhuma ata encontrada' : 'Nenhuma ata gerada ainda'}</h3>
            <p>{searchTerm ? 'Tente outro termo de busca' : 'Comece fazendo upload de um arquivo'}</p>
          </div>
        ) : (
          <>
            <div className="results-count">
              <span>{filteredMinutes.length} {filteredMinutes.length === 1 ? 'ata encontrada' : 'atas encontradas'}</span>
            </div>

            <div className="minutes-list">
              {filteredMinutes.map((minute, index) => (
                <div 
                  key={minute.id}
                  className="minute-item cyber-card"
                  style={{animationDelay: `${index * 0.05}s`}}
                  onClick={() => navigate(`/minute/${minute.id}`)}
                >
                  <div className="minute-item-header">
                    <div className="minute-title-section">
                      <h3>{minute.title}</h3>
                      <span className="minute-date">{formatDate(minute.created_at)}</span>
                    </div>
                    <button
                      className="delete-btn"
                      onClick={(e) => handleDelete(minute.id, e)}
                      title="Excluir ata"
                    >
                      Excluir
                    </button>
                  </div>

                  <div className="minute-item-details">
                    <div className="detail-item">
                      <span className="detail-label">Arquivo:</span>
                      <span className="detail-text">{minute.original_filename}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Duração:</span>
                      <span className="detail-text">{Math.round(minute.audio_duration)}s</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Processamento:</span>
                      <span className="detail-text">{Math.round(minute.processing_time)}s</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Tamanho:</span>
                      <span className="detail-text">{minute.file_size?.toFixed(2)} MB</span>
                    </div>
                  </div>

                  <div className="minute-item-footer">
                    <span className="view-link">Ver detalhes →</span>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default History;
