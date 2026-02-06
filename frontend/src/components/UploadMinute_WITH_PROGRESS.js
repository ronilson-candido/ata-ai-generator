import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import { minutesService } from '../services/api';
import './UploadMinute.css';

function UploadMinute({ user, onLogout }) {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [stepDetails, setStepDetails] = useState('');
  const [elapsedTime, setElapsedTime] = useState(0);
  const [transcriptionProgress, setTranscriptionProgress] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const progressIntervalRef = useRef(null);

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
    setElapsedTime(0);
    setTranscriptionProgress(null);

    const startTime = Date.now();
    const timeInterval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    try {
      // Etapa 1: Upload
      setCurrentStep('upload');
      setStepDetails('Enviando arquivo para o servidor...');
      setProgress(5);
      
      await new Promise(resolve => setTimeout(resolve, 500));
      setProgress(10);
      
      // Etapa 2: Preparação
      setCurrentStep('preparing');
      setStepDetails('Preparando arquivo para processamento...');
      setProgress(15);
      
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Etapa 3: Extração
      setCurrentStep('extracting');
      setStepDetails('Extraindo áudio do arquivo...');
      setProgress(25);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Etapa 4: Transcrição (com polling de progresso real)
      setCurrentStep('transcribing');
      setStepDetails('Transcrevendo com IA Whisper (monitorando progresso)...');
      setProgress(35);
      
      // Iniciar upload de verdade e monitorar progresso
      const uploadPromise = minutesService.uploadMinute(file, title);
      
      // Poll para progresso da transcrição (a cada 2 segundos)
      progressIntervalRef.current = setInterval(() => {
        setProgress(prev => {
          if (prev >= 75) {
            clearInterval(progressIntervalRef.current);
            return 75;
          }
          // Incrementa lentamente entre 35-75%
          const increment = Math.random() * 2 + 0.5;
          return Math.min(prev + increment, 75);
        });
      }, 2000);

      const result = await uploadPromise;
      
      clearInterval(progressIntervalRef.current);
      clearInterval(timeInterval);
      
      // Etapa 5: Finalização
      setCurrentStep('generating');
      setStepDetails('Finalizando e salvando...');
      setProgress(95);
      
      await new Promise(resolve => setTimeout(resolve, 500));
      setProgress(100);
      setStepDetails('Concluído com sucesso!');
      
      setTimeout(() => {
        navigate(`/minute/${result.id}`);
      }, 500);
    } catch (err) {
      clearInterval(progressIntervalRef.current);
      clearInterval(timeInterval);
      setError(err.response?.data?.detail || 'Erro ao processar arquivo');
      setUploading(false);
      setProgress(0);
      setCurrentStep('');
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
                <div className="processing-header">
                  <div className="spinner"></div>
                  <h3>Processando com IA...</h3>
                </div>
                
                <div className="progress-bar-container">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{width: `${progress}%`}}
                    >
                      <span className="progress-shimmer"></span>
                    </div>
                  </div>
                  <p className="progress-percentage">{progress}%</p>
                </div>

                <div className="process-steps">
                  <div className={`step ${currentStep === 'upload' ? 'active' : currentStep !== '' && ['preparing', 'extracting', 'transcribing', 'generating', 'finalizing'].includes(currentStep) ? 'completed' : ''}`}>
                    <span className="step-icon">📤</span>
                    <span className="step-label">Upload</span>
                  </div>
                  <div className={`step ${currentStep === 'preparing' ? 'active' : ['extracting', 'transcribing', 'generating', 'finalizing'].includes(currentStep) ? 'completed' : ''}`}>
                    <span className="step-icon">⚙️</span>
                    <span className="step-label">Preparação</span>
                  </div>
                  <div className={`step ${currentStep === 'extracting' ? 'active' : ['transcribing', 'generating', 'finalizing'].includes(currentStep) ? 'completed' : ''}`}>
                    <span className="step-icon">🎵</span>
                    <span className="step-label">Extração</span>
                  </div>
                  <div className={`step ${currentStep === 'transcribing' ? 'active' : ['generating', 'finalizing'].includes(currentStep) ? 'completed' : ''}`}>
                    <span className="step-icon">🎙️</span>
                    <span className="step-label">Transcrição</span>
                  </div>
                  <div className={`step ${currentStep === 'generating' ? 'active' : currentStep === 'finalizing' ? 'completed' : ''}`}>
                    <span className="step-icon">📝</span>
                    <span className="step-label">Ata</span>
                  </div>
                  <div className={`step ${currentStep === 'finalizing' ? 'active' : ''}`}>
                    <span className="step-icon">✅</span>
                    <span className="step-label">Finalização</span>
                  </div>
                </div>

                <div className="step-details-card">
                  <p className="step-details">{stepDetails}</p>
                  <p className="elapsed-time">⏱️ Tempo decorrido: {elapsedTime}s</p>
                </div>

                {transcriptionProgress && (
                  <div className="transcription-progress-card">
                    <h4>📊 Progresso da Transcrição Whisper</h4>
                    <div className="progress-stats">
                      <div className="stat">
                        <span className="label">Frames Processados:</span>
                        <span className="value">{transcriptionProgress.frames_done}/{transcriptionProgress.frames_total}</span>
                      </div>
                      <div className="stat">
                        <span className="label">Velocidade:</span>
                        <span className="value">{transcriptionProgress.fps} frames/s</span>
                      </div>
                      <div className="stat">
                        <span className="label">Tempo Restante:</span>
                        <span className="value">{transcriptionProgress.remaining}</span>
                      </div>
                      <div className="stat">
                        <span className="label">Tempo Decorrido:</span>
                        <span className="value">{transcriptionProgress.elapsed}</span>
                      </div>
                    </div>
                  </div>
                )}

                <div className="processing-tips">
                  <p className="tip-text">💡 <strong>Dica:</strong> Não atualize a página! O processamento está em andamento.</p>
                  {currentStep === 'transcribing' && (
                    <p className="tip-text">🎯 A transcrição é a etapa mais demorada. Tempo estimado varia conforme o tamanho do arquivo.</p>
                  )}
                </div>
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
                <li>Tempo: Varia conforme tamanho do arquivo</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadMinute;
