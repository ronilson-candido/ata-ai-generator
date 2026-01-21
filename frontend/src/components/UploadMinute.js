import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import { minutesService } from '../services/api';
import './UploadMinute.css';

function UploadMinute({ user, onLogout }) {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      if (!title) {
        setTitle(selectedFile.name.split('.')[0]);
      }
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Selecione um arquivo');
      return;
    }

    if (!title.trim()) {
      setError('Digite um título para a ata');
      return;
    }

    setUploading(true);
    setProgress(0);
    setError('');

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 1000);

      const result = await minutesService.uploadMinute(file, title);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      setTimeout(() => {
        navigate(`/minute/${result.id}`);
      }, 500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao processar arquivo');
      setUploading(false);
      setProgress(0);
    }
  };

  const formatFileSize = (bytes) => {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  };

  return (
    <div className="upload-page">
      <Navbar user={user} onLogout={onLogout} />
      
      <div className="upload-container">
        <div className="upload-header">
          <h1 className="glow-text">NOVA ATA DE REUNIÃO</h1>
          <p className="subtitle">Upload de áudio ou vídeo para transcrição com IA</p>
        </div>

        <div className="upload-content">
          <form onSubmit={handleSubmit} className="upload-form">
            <div className="form-section cyber-card">
              <h2>1. Informações da Ata</h2>
              
              <div className="form-group">
                <label htmlFor="title">Título da Reunião</label>
                <input
                  type="text"
                  id="title"
                  className="cyber-input"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Ex: Reunião Semanal - Sprint Planning"
                  required
                  disabled={uploading}
                />
              </div>
            </div>

            <div className="form-section cyber-card">
              <h2>2. Upload do Arquivo</h2>
              
              <div className="file-upload-area">
                <input
                  type="file"
                  id="file"
                  accept="audio/*,video/*"
                  onChange={handleFileChange}
                  disabled={uploading}
                  style={{display: 'none'}}
                />
                
                <label htmlFor="file" className="file-upload-label">
                  {file ? (
                    <div className="file-selected">
                      <div className="file-icon">📁</div>
                      <div className="file-details">
                        <div className="file-name">{file.name}</div>
                        <div className="file-size">{formatFileSize(file.size)}</div>
                      </div>
                    </div>
                  ) : (
                    <div className="file-prompt">
                      <div className="upload-icon">⬆️</div>
                      <p className="upload-text">Clique para selecionar o arquivo</p>
                      <p className="upload-hint">Formatos suportados: MP4, AVI, MOV, WAV, MP3, M4A, OGG</p>
                    </div>
                  )}
                </label>
              </div>

              {file && !uploading && (
                <button 
                  type="button" 
                  className="change-file-btn"
                  onClick={() => document.getElementById('file').click()}
                >
                  Alterar Arquivo
                </button>
              )}
            </div>

            {uploading && (
              <div className="progress-section cyber-card">
                <h3>Processando com IA...</h3>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{width: `${progress}%`}}
                  ></div>
                </div>
                <p className="progress-text">{progress}%</p>
                <p className="progress-status">
                  {progress < 30 && 'Extraindo áudio...'}
                  {progress >= 30 && progress < 70 && 'Transcrevendo com Whisper...'}
                  {progress >= 70 && progress < 100 && 'Gerando ata estruturada...'}
                  {progress === 100 && 'Concluído!'}
                </p>
              </div>
            )}

            {error && (
              <div className="error-message">{error}</div>
            )}

            <button
              type="submit"
              className="cyber-button submit-button"
              disabled={!file || !title || uploading}
            >
              {uploading ? 'PROCESSANDO...' : 'PROCESSAR COM IA'}
            </button>
          </form>

          <div className="info-panel cyber-card">
            <h3>ℹ️ Como funciona</h3>
            <ol className="info-list">
              <li>
                <strong>Upload:</strong> Envie um arquivo de áudio ou vídeo da reunião
              </li>
              <li>
                <strong>Extração:</strong> O sistema extrai o áudio do vídeo (se necessário)
              </li>
              <li>
                <strong>Transcrição:</strong> IA Whisper transcreve todo o conteúdo falado
              </li>
              <li>
                <strong>Estruturação:</strong> IA gera uma ata organizada com tópicos
              </li>
              <li>
                <strong>Resultado:</strong> Ata pronta para download e compartilhamento
              </li>
            </ol>

            <div className="tech-specs">
              <h4>⚙️ Especificações Técnicas</h4>
              <ul>
                <li>IA: OpenAI Whisper</li>
                <li>Precisão: ~95%</li>
                <li>Idiomas: Português, Inglês e mais</li>
                <li>Tempo: ~1-5 minutos</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadMinute;
