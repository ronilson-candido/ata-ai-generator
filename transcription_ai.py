from faster_whisper import WhisperModel
import torch
import tempfile
import os
import subprocess
import re
import time
import sys
from io import StringIO
from pydub import AudioSegment
import ffmpeg
from config import Config
import threading

class TranscriptionEngine:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.model_name = Config.WHISPER_MODEL  # Lê do config
    
    def load_model(self):
        if not self.model_loaded:
            try:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                compute_type = "float16" if device == "cuda" else "int8"
                
                print(f"Carregando modelo Faster-Whisper '{self.model_name}' na {device.upper()} (compute_type={compute_type})...")
                
                try:
                    self.model = WhisperModel(
                        self.model_name, 
                        device=device,
                        compute_type=compute_type,
                        cpu_threads=4,
                        num_workers=1
                    )
                    print(f"Modelo '{self.model_name}' carregado com sucesso!")
                except Exception as e:
                    print(f"Não foi possível carregar '{self.model_name}': {e}")
                    print("Tentando 'small'...")
                    try:
                        self.model_name = "small"
                        self.model = WhisperModel("small", device=device, compute_type=compute_type)
                        print("Modelo 'small' carregado com sucesso!")
                    except:
                        print("Não foi possível carregar 'small', usando 'base'...")
                        self.model_name = "base"
                        self.model = WhisperModel("base", device=device, compute_type=compute_type)
                        print("Modelo 'base' carregado (qualidade reduzida)!")
                
                self.model_loaded = True
                
            except Exception as e:
                print(f"Erro ao carregar modelo: {e}")
                raise e
    
    def transcribe_audio(self, audio_path, with_segments: bool = False):
        """Transcreve áudio com Whisper e opcionalmente retorna segmentos temporais."""
        try:
            if not self.model_loaded:
                self.load_model()
            
            print(f"Transcrevendo áudio: {audio_path}")
            print(f"Arquivo existe? {os.path.exists(audio_path)}, Tamanho: {os.path.getsize(audio_path) if os.path.exists(audio_path) else 0}")
            
            # Prompt melhorado para contexto técnico em português brasileiro
            technical_prompt = (
                "Esta é uma reunião de trabalho em português brasileiro sobre desenvolvimento de software, "
                "programação de PLCs, simuladores, sistemas embarcados, comunicação industrial, "
                "integração de sistemas, data access, bibliotecas, APIs, compiladores, "
                "configurações de hardware e software. "
                "Transcreva exatamente o que é falado, mantendo todos os termos técnicos, "
                "nomes de produtos, siglas e expressões coloquiais do português brasileiro. "
                "Preste atenção especial a: PLC, WPS, PCC, simulador, compilação, binário, "
                "conexão, USB, CAN, download, runtime, bloco, hardware, memória, ponteiro, "
                "equipamento, configuração, implementação, biblioteca, telegrama."
            )
            
            # Parâmetros otimizados para VELOCIDADE (faster-whisper)
            speed_mode = str(Config.WHISPER_SPEED_MODE) == "1"
            if speed_mode:
                beam_size = Config.WHISPER_BEAM_SIZE 
                temperature = [Config.WHISPER_TEMPERATURE] 
            else:
                beam_size = 3 
                temperature = [0.0, 0.2]  

            # Transcrever com VAD e chunk otimizado
            segments, info = self.model.transcribe(
                audio_path,
                language='pt',
                task='transcribe',
                beam_size=beam_size,
                temperature=temperature,
                initial_prompt=technical_prompt,
                vad_filter=True,  
                vad_parameters=dict(
                    threshold=0.5,
                    min_speech_duration_ms=250,
                    min_silence_duration_ms=1000
                ),
                word_timestamps=with_segments, 
            )
            
            transcription_parts = []
            segments_list = []
            
            for segment in segments:
                transcription_parts.append(segment.text)
                if with_segments:
                    segments_list.append({
                        "start": segment.start,
                        "end": segment.end,
                        "text": segment.text
                    })
            
            transcription = " ".join(transcription_parts).strip()
            
            transcription = self._post_process_transcription(transcription)
            
            print(f"Transcrição concluída: {len(transcription)} caracteres")
            print(f"Modelo usado: {self.model_name}")
            print(f"Duração detectada: {info.duration:.1f}s")
            print(f"Resultado: {transcription[:100] if transcription else '(vazio)'}")
            
            if with_segments:
                return transcription, segments_list
            return transcription
            
        except Exception as e:
            error_msg = f"Erro na transcrição: {str(e)}"
            print(error_msg)
            if with_segments:
                return error_msg, []
            return error_msg
    
    def _post_process_transcription(self, text: str) -> str:
        """Aplica correções comuns em transcrições PT-BR"""
        if not text:
            return text
        
        # Correções comuns de palavras mal transcritas
        corrections = {
            # Termos técnicos comuns
            ' pê ele cê ': ' PLC ',
            ' pê éle cê ': ' PLC ',
            ' pê-ele-cê ': ' PLC ',
            'pelicê': 'PLC',
            'pelesê': 'PLC',
            'pelicicê': 'PLC',
            ' dê pê ésse ': ' WPS ',
            ' dê-pê-ésse ': ' WPS ',
            'uébesê': 'USB',
            'u-es-be': 'USB',
            'cána': 'CAN',
            'cã network': 'CAN',
            ' jotaene ai ': ' JNI ',
            'jotaneai': 'JNI',
            'daón lóud': 'download',
            'daunloud': 'download',
            'rátime': 'runtime',
            'rãtaime': 'runtime',
            'bildar': 'buildar',
            'ápiai': 'API',
            
            # Expressões comuns mal transcritas
            'né ': ', né? ',
            ' tipo ': ' tipo, ',
            ' ó ': ', ó, ',
            ' tá ': ' está ',
        }
        
        result = text
        for wrong, correct in corrections.items():
            result = result.replace(wrong, correct)
        
        # Remove espaços múltiplos
        import re
        result = re.sub(r'\s+', ' ', result)
        
        return result.strip()
    
    def convert_to_wav(self, audio_path):
        """Converter qualquer formato de áudio para WAV 16kHz mono"""
        try:
            ext = os.path.splitext(audio_path)[1].lower()
            print(f"\n=== CONVERSÃO DE ÁUDIO ===")
            print(f"Arquivo original: {audio_path}")
            print(f"Extensão: {ext}")
            print(f"Tamanho: {os.path.getsize(audio_path)} bytes")
            
            if ext == '.wav':
                print("Arquivo já é WAV, pulando conversão")
                return audio_path  
            
            output_path = audio_path.replace(ext, '.wav')
            print(f"Output: {output_path}")
            
            # Tentar com ffmpeg (mais robusto para WebM/Opus)
            try:
                print("Tentando conversão com ffmpeg...")
                cmd = [
                    'ffmpeg', '-i', audio_path,
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',
                    '-ac', '1',
                    '-y',  # Overwrite
                    output_path
                ]
                print(f"Comando: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    output_size = os.path.getsize(output_path)
                    print(f"FFmpeg sucesso! Output size: {output_size} bytes")
                    return output_path
                else:
                    print(f"FFmpeg falhou: {result.stderr}")
            except Exception as ffmpeg_err:
                print(f"FFmpeg erro: {ffmpeg_err}")
            
            # Fallback com pydub
            try:
                print("Tentando fallback com pydub...")
                audio = AudioSegment.from_file(audio_path)
                audio = audio.set_frame_rate(16000).set_channels(1)
                audio.export(output_path, format="wav")
                output_size = os.path.getsize(output_path)
                print(f"Pydub sucesso! Output size: {output_size} bytes")
                return output_path
            except Exception as pydub_err:
                print(f"Pydub falhou: {pydub_err}")
            
            print("AVISO: Conversão falhou, tentando usar arquivo original")
            return audio_path
            
        except Exception as e:
            print(f"Erro geral na conversão: {e}")
            return audio_path

transcription_engine = TranscriptionEngine()

def transcribe_audio(audio_path, with_segments: bool = False):
    try:
        wav_path = transcription_engine.convert_to_wav(audio_path)
        return transcription_engine.transcribe_audio(wav_path, with_segments=with_segments)
        
    except Exception as e:
        if with_segments:
            return f"Erro no processo de transcrição: {str(e)}", []
        return f"Erro no processo de transcrição: {str(e)}"


def transcribe_with_speakers(audio_path, with_diarization: bool = True):
    """
    Transcreve áudio com timestamps e identificação de locutores.
    
    Retorna string formatada:
    (0:00) Pessoa 1: Texto...
    (0:15) Pessoa 2: Texto...
    """
    try:
        wav_path = transcription_engine.convert_to_wav(audio_path)
        transcription, segments = transcription_engine.transcribe_audio(wav_path, with_segments=True)
        
        if not segments:
            return transcription, {}
        
        speaker_segments = []
        if with_diarization:
            try:
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
                from backend.diarization import diarize_audio
                
                print("[DIARIZAÇÃO] Iniciando identificação de locutores...")
                diar_segments = diarize_audio(wav_path)
                
                if diar_segments:
                    speaker_segments = _align_speakers_with_segments(segments, diar_segments)
                    print(f"[DIARIZAÇÃO] {len(speaker_segments)} segmentos com locutores identificados")
                else:
                    print("[DIARIZAÇÃO] Sem segmentos de locutores (token ausente ou pyannote não instalado)")
                    speaker_segments = [{"start": s["start"], "end": s["end"], "text": s["text"], "speaker": None} for s in segments]
            except Exception as e:
                print(f"[DIARIZAÇÃO] Módulo indisponível ({type(e).__name__}). Continuando sem identificação de locutores.")
                speaker_segments = [{"start": s["start"], "end": s["end"], "text": s["text"], "speaker": None} for s in segments]
        else:
            speaker_segments = [{"start": s["start"], "end": s["end"], "text": s["text"], "speaker": None} for s in segments]
        
        formatted_lines = []
        for seg in speaker_segments:
            timestamp = _format_timestamp(seg["start"])
            speaker_label = seg.get("speaker") or ""
            text = seg["text"].strip()
            
            if speaker_label:
                speaker_num = speaker_label.replace("SPEAKER_", "").replace("Speaker", "")
                try:
                    speaker_num = int(speaker_num) + 1  # SPEAKER_00 -> Pessoa 1
                    speaker_label = f"Pessoa {speaker_num}: "
                except:
                    speaker_label = f"{speaker_label}: "
            
            formatted_lines.append(f"({timestamp}) {speaker_label}{text}")
        
        result = _group_by_speaker(formatted_lines, speaker_segments)
        
        structured_data = {
            "transcription": transcription,
            "segments": speaker_segments,
            "formatted": result
        }
        
        return result, structured_data
        
    except Exception as e:
        error_msg = f"Erro na transcrição com locutores: {str(e)}"
        print(error_msg)
        return error_msg, {}


def _format_timestamp(seconds: float) -> str:
    """Converte segundos para formato (M:SS) ou (MM:SS)"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def _align_speakers_with_segments(whisper_segments, diar_segments):
    """Associa cada segmento Whisper ao locutor com maior sobreposição temporal"""
    result = []
    
    for seg in whisper_segments:
        start = seg["start"]
        end = seg["end"]
        text = seg["text"]
        
        best_speaker = None
        max_overlap = 0
        
        for diar in diar_segments:
            diar_start = diar["start"]
            diar_end = diar["end"]
            
            overlap_start = max(start, diar_start)
            overlap_end = min(end, diar_end)
            overlap = max(0, overlap_end - overlap_start)
            
            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = diar["speaker"]
        
        result.append({
            "start": start,
            "end": end,
            "text": text,
            "speaker": best_speaker
        })
    
    return result


def _group_by_speaker(formatted_lines, segments):
    """Agrupa linhas consecutivas do mesmo locutor em parágrafos"""
    if not formatted_lines:
        return ""
    
    grouped = []
    current_speaker = None
    current_group = []
    
    for i, line in enumerate(formatted_lines):
        seg = segments[i] if i < len(segments) else {}
        speaker = seg.get("speaker")
        
        if speaker != current_speaker and current_group:
            # Novo locutor, fechar grupo anterior
            grouped.append(" ".join(current_group))
            grouped.append("")  # Linha em branco entre locutores
            current_group = []
        
        current_group.append(line)
        current_speaker = speaker
    
    if current_group:
        grouped.append(" ".join(current_group))
    
    return "\n".join(grouped)

def get_transcription_status():
    return {
        "model_loaded": transcription_engine.model_loaded,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }