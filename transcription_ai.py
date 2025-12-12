import whisper
import torch
import tempfile
import os
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
    
    def transcribe_audio(self, audio_path):
        try:
            if not self.model_loaded:
                self.load_model()
            
            print(f"Transcrevendo áudio: {audio_path}")
            
            result = self.model.transcribe(
                audio_path,
                language='pt',
                fp16=False,  
                verbose=False
            )
            
            transcription = result["text"].strip()
            print(f"Transcrição concluída: {len(transcription)} caracteres")
            
            return transcription
            
        except Exception as e:
            error_msg = f"Erro na transcrição: {str(e)}"
            print(error_msg)
            return error_msg
    
    def convert_to_wav(self, audio_path):
        try:
            output_path = audio_path.replace('.mp3', '.wav').replace('.m4a', '.wav')
            
            if audio_path.endswith('.wav'):
                return audio_path  
            
            print(f"Convertendo {audio_path} para WAV...")
            
            audio = AudioSegment.from_file(audio_path)
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(output_path, format="wav")
            
            print(f"Conversão concluída: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Erro na conversão: {e}")
            return audio_path  

transcription_engine = TranscriptionEngine()

def transcribe_audio(audio_path):
    try:
        wav_path = transcription_engine.convert_to_wav(audio_path)
        return transcription_engine.transcribe_audio(wav_path)
        
    except Exception as e:
        return f"Erro no processo de transcrição: {str(e)}"

def get_transcription_status():
    return {
        "model_loaded": transcription_engine.model_loaded,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }