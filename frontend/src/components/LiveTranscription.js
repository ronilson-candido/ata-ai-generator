import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import { minutesService } from '../services/api';
import './LiveTranscription.css';

function LiveTranscription({ user, onLogout }) {
  const recognitionRef = useRef(null);
  const recorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);

  const [mode, setMode] = useState('mic'); // mic | tab
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interim, setInterim] = useState('');
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [title, setTitle] = useState('Transcrição ao vivo');
  const [saving, setSaving] = useState(false);
  const [supportError, setSupportError] = useState('');
  const [statusMessage, setStatusMessage] = useState('Pronto para começar');
  const [debugInfo, setDebugInfo] = useState('');
  const navigate = useNavigate();

  const logDebug = (message) => {
    setDebugInfo((prev) => {
      const next = `${new Date().toLocaleTimeString()} - ${message}`;
      return prev ? `${prev}\n${next}` : next;
    });
  };

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSupportError('Seu navegador não suporta reconhecimento de voz (Web Speech API). Tente usar o Chrome ou Edge para habilitar a transcrição ao vivo.');
      return undefined;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'pt-BR';
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      let finalText = '';
      let interimText = '';

      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i];
        if (result.isFinal) {
          finalText += `${result[0].transcript.trim()} `;
        } else {
          interimText += `${result[0].transcript.trim()} `;
        }
      }

      if (finalText) {
        setTranscript((prev) => `${prev}${finalText}`);
      }
      setInterim(interimText);
    };

    recognition.onerror = (event) => {
      setStatusMessage(`Erro: ${event.error}`);
      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
      setStatusMessage('Transcrição pausada');
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.stop();
      if (recorderRef.current) {
        recorderRef.current.stop();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);

  const stopStreams = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  };

  const startMic = async () => {
    if (!recognitionRef.current) return;

    setRecordedBlob(null);
    setTranscript('');
    setInterim('');
    setStatusMessage('Ouvindo...');

    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      recognitionRef.current.start();
      setListening(true);
    } catch (err) {
      setSupportError('Não foi possível acessar o microfone. Verifique as permissões do navegador.');
    }
  };

  const startTabCapture = async () => {
    if (!navigator.mediaDevices?.getDisplayMedia) {
      setSupportError('Seu navegador não permite captura da guia (getDisplayMedia indisponível). Use Chrome/Edge mais recente.');
      logDebug('getDisplayMedia ausente');
      return;
    }

    if (!window.isSecureContext && window.location.hostname !== 'localhost') {
      setSupportError('A captura da guia exige HTTPS ou localhost. Acesse via https:// ou use localhost.');
      logDebug('Contexto não seguro (precisa https/localhost)');
      return;
    }

    setTranscript('');
    setInterim('');
    setRecordedBlob(null);
    setStatusMessage('Solicitando captura da guia...');
    logDebug('Chamando getDisplayMedia');

    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: true, // necessário para compartilhar a guia
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
        },
        preferCurrentTab: true,
      });
      const hasAudio = stream.getAudioTracks && stream.getAudioTracks().length > 0;
      if (!hasAudio) {
        setSupportError('A captura da guia não retornou áudio. Selecione uma aba/janela com áudio e marque "Compartilhar áudio".');
        logDebug('Stream sem trilhas de áudio');
        stopStreams();
        return;
      }

      streamRef.current = stream;
      chunksRef.current = [];

      // Preferir áudio puro; se falhar, tentar vídeo+áudio
      const audioOnlyStream = new MediaStream(stream.getAudioTracks());

      const tryStartRecorder = (mediaStream, mimeCandidates, label) => {
        chunksRef.current = [];
        let chosen = '';
        for (const mime of mimeCandidates) {
          if (!mime || MediaRecorder.isTypeSupported(mime)) {
            chosen = mime;
            break;
          }
        }

        try {
          const options = chosen ? { mimeType: chosen } : undefined;
          const recorder = new MediaRecorder(mediaStream, options);
          recorderRef.current = recorder;
          logDebug(`Criando MediaRecorder (${label}) com mime: ${chosen || 'padrão'}`);

          recorder.onstart = () => {
            logDebug(`MediaRecorder (${label}) iniciado`);
          };

          recorder.onerror = (event) => {
            logDebug(`MediaRecorder (${label}) erro: ${event.error?.name || 'erro'} - ${event.error?.message || ''}`);
          };

          recorder.ondataavailable = (event) => {
            if (event.data && event.data.size > 0) {
              chunksRef.current.push(event.data);
            }
          };

          recorder.onstop = () => {
            const blob = new Blob(chunksRef.current, { type: recorder.mimeType || chosen || 'video/webm' });
            setRecordedBlob(blob);
            setStatusMessage('Captura encerrada. Pronto para salvar.');
            logDebug(`Recorder stop (${label}). Blob size: ${blob.size}, type: ${blob.type}`);
            stopStreams();
          };

          recorder.start();
          setListening(true);
          setStatusMessage('Capturando áudio da guia...');
          logDebug(`Recorder start (${label})`);
          return true;
        } catch (err) {
          logDebug(`Recorder (${label}) falhou: ${err.name || 'erro'} - ${err.message || ''}`);
          return false;
        }
      };

      const audioOk = tryStartRecorder(audioOnlyStream, [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        ''
      ], 'audio-only');

      if (!audioOk) {
        const videoOk = tryStartRecorder(stream, [
          'video/webm;codecs=vp8,opus',
          'video/webm;codecs=vp9,opus',
          'video/webm',
          ''
        ], 'video+audio');

        if (!videoOk) {
          setSupportError('MediaRecorder não conseguiu iniciar. Tente outro navegador (Chrome/Edge), atualize ou verifique se a aba permite áudio compartilhado.');
          stopStreams();
          return;
        }
      }
    } catch (err) {
      console.error('getDisplayMedia error', err);
      setSupportError(`Não foi possível capturar a guia: ${err.name || 'Erro'}. Dica: escolha a opção "Guia do Chrome"/"Chrome Tab" e marque "Compartilhar áudio".`);
      logDebug(`Erro getDisplayMedia: ${err.name || 'sem nome'} - ${err.message || ''}`);
      stopStreams();
    }
  };

  const handleStart = async () => {
    if (mode === 'tab') {
      await startTabCapture();
    } else {
      await startMic();
    }
  };

  const handleStop = () => {
    if (mode === 'tab') {
      if (recorderRef.current && recorderRef.current.state !== 'inactive') {
        recorderRef.current.stop();
      }
      stopStreams();
    } else if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setListening(false);
    setStatusMessage('Transcrição pausada');
  };

  const switchMode = (newMode) => {
    if (listening) {
      handleStop();
    }
    setMode(newMode);
    setTranscript('');
    setInterim('');
    setRecordedBlob(null);
    setSupportError('');
    setStatusMessage(newMode === 'tab' ? 'Pronto para capturar áudio da guia' : 'Pronto para começar');
  };

  const handleSave = async () => {
    setSaving(true);

    try {
      if (mode === 'tab') {
        if (!recordedBlob) {
          setStatusMessage('Grave algo antes de salvar');
          setSaving(false);
          return;
        }
        logDebug(`Salvando blob: size=${recordedBlob.size}, type=${recordedBlob.type}`);
        // Usar o mimeType correto do blob e extensão apropriada
        const fileName = recordedBlob.type?.includes('audio') ? 'captura-audio.webm' : 'captura-video.webm';
        const file = new File([recordedBlob], fileName, { type: recordedBlob.type || 'audio/webm' });
        logDebug(`Enviando arquivo: ${fileName}, mimeType: ${file.type}`);
        const saved = await minutesService.uploadMinute(file, title || 'Captura da guia');
        logDebug(`Upload completo. ID: ${saved?.id}`);
        setStatusMessage('Captura enviada para transcrição');
        setRecordedBlob(null);
        if (saved?.id) {
          navigate(`/minute/${saved.id}`);
        }
      } else {
        if (!transcript.trim() && !interim.trim()) {
          setStatusMessage('Não há texto para salvar');
          setSaving(false);
          return;
        }

        const textToSave = `${transcript}${interim}`.trim();
        const saved = await minutesService.saveLiveTranscription(title || 'Transcrição ao vivo', textToSave);
        setStatusMessage('Transcrição salva com sucesso');
        setTranscript('');
        setInterim('');
        if (saved?.id) {
          navigate(`/minute/${saved.id}`);
        }
      }
    } catch (error) {
      setStatusMessage(error.response?.data?.detail || 'Erro ao salvar');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="live-page">
      <Navbar user={user} onLogout={onLogout} />

      <div className="live-container">
        <div className="live-header">
          <div>
            <p className="eyebrow">CAPTURA AO VIVO</p>
            <p className="subtitle">Use o microfone para transcrever instantaneamente o que está sendo dito.</p>
          </div>
          <div className="actions">
            <button
              className={`cyber-button ${listening ? 'danger' : ''}`}
              onClick={listening ? handleStop : handleStart}
              disabled={!!supportError || saving}
            >
              {listening ? 'PAUSAR' : 'INICIAR'}
            </button>
            <button
              className="cyber-button-secondary"
              onClick={handleSave}
              disabled={saving || (mode === 'mic' && !transcript && !interim) || (mode === 'tab' && !recordedBlob)}
            >
              {saving ? 'SALVANDO...' : 'SALVAR ATA'}
            </button>
          </div>
        </div>

        <div className="mode-tabs">
          <button
            className={`mode-tab ${mode === 'mic' ? 'active' : ''}`}
            onClick={() => switchMode('mic')}
            disabled={saving}
          >
            Microfone (texto em tempo real)
          </button>
          <button
            className={`mode-tab ${mode === 'tab' ? 'active' : ''}`}
            onClick={() => switchMode('tab')}
            disabled={saving}
          >
            Capturar áudio da guia (gravar + transcrever)
          </button>
        </div>

        {supportError && (
          <div className="support-alert">{supportError}</div>
        )}
        {debugInfo && (
          <div className="debug-box">
            <div className="debug-title">Log rápido (para diagnósticos locais)</div>
            <pre>{debugInfo}</pre>
          </div>
        )}

        <div className="live-grid">
          <div className="live-card">
            <div className="card-header">
              <div>
                <p className="label">Título</p>
                <input
                  type="text"
                  className="cyber-input"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Ex: Reunião de alinhamento"
                  disabled={saving}
                />
              </div>
              <div className={`status-chip ${listening ? 'active' : 'idle'}`}>
                {listening ? 'Ouvindo' : 'Parado'}
              </div>
            </div>

            <div className="transcript-box">
              <div className="transcript-text">
                {mode === 'mic' ? (
                  <>
                    {transcript || 'A transcrição aparecerá aqui...'}
                    <span className="interim">{interim}</span>
                  </>
                ) : (
                  recordedBlob ? 'Captura pronta para enviar.' : 'Grave o áudio da guia para transcrever.'
                )}
              </div>
            </div>

            <div className="status-row">
              <span>{statusMessage}</span>
              <span className="hint">
                {mode === 'mic' ? 'Dica: mantenha o microfone próximo e fale claramente.' : 'Dica: escolha a aba com áudio e marque "Compartilhar áudio".'}
              </span>
            </div>
          </div>

          <div className="live-card side">
            <ul className="tips">
              {mode === 'mic' ? (
                <>
                  <li>1. Clique em INICIAR e autorize o microfone.</li>
                  <li>2. Fale; o texto em cinza é parcial.</li>
                  <li>3. Pause quando quiser e clique em SALVAR ATA.</li>
                </>
              ) : (
                <>
                  <li>1. Clique em INICIAR e escolha a guia/janela com áudio (marque "Compartilhar áudio").</li>
                  <li>2. Quando terminar, clique em PAUSAR para gerar o arquivo.</li>
                  <li>3. Clique em SALVAR ATA para enviar e transcrever.</li>
                </>
              )}
            </ul>

            <div className="tag-grid">
              <span className="tag">Português (pt-BR)</span>
              <span className="tag">{mode === 'mic' ? 'Tempo real' : 'Captura da guia'}</span>
              <span className="tag">{mode === 'mic' ? 'Sem upload' : 'Upload automático'}</span>
            </div>

            <div className="note">
              <strong>Observação:</strong> A captura de áudio da aba depende do navegador. No modo "Capturar guia", selecione a aba com áudio e marque "Compartilhar áudio".
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LiveTranscription;
