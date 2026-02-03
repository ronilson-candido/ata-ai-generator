import whisper
import torch
import tempfile
import os
import subprocess
from pydub import AudioSegment
import ffmpeg

class TranscriptionEngine:
    def __init__(self):
        self.model = None
        self.model_loaded = False
    
    def load_model(self):
        if not self.model_loaded:
            try:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                print(f"Carregando modelo Whisper na {device.upper()}...")
                
                self.model = whisper.load_model("base", device=device)
                self.model_loaded = True
                print("Modelo Whisper carregado com sucesso!")
                
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
            
            result = self.model.transcribe(
                audio_path,
                language='pt',
                task='transcribe',
                fp16=False,
                verbose=False,
                temperature=0.2,
                initial_prompt=(
                    "Português do Brasil. Transcreva falas técnicas sobre desenvolvimento, PLC, "
                    "simuladores, integrações, modbus, telegramas, JNI. Não traduza nomes próprios."
                )
            )
            
            transcription = result.get("text", "").strip()
            segments = result.get("segments", []) if with_segments else None
            print(f"Transcrição concluída: {len(transcription)} caracteres")
            print(f"Resultado: {transcription[:100] if transcription else '(vazio)'}")
            
            if with_segments:
                return transcription, segments
            return transcription
            
        except Exception as e:
            error_msg = f"Erro na transcrição: {str(e)}"
            print(error_msg)
            if with_segments:
                return error_msg, []
            return error_msg
    
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

def get_transcription_status():
    return {
        "model_loaded": transcription_engine.model_loaded,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }