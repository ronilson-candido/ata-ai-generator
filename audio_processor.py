import subprocess
import os
import tempfile
from pydub import AudioSegment

def extract_audio_from_video(video_path):
    try:
        print(f"Extraindo áudio de: {video_path}")
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
            audio_path = audio_file.name
        
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vn',              
            '-acodec', 'pcm_s16le',
            '-ar', '16000',     
            '-ac', '1',         
            '-y',               
            audio_path
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Tentando método alternativo de extração...")
            try:
                video = AudioSegment.from_file(video_path)
                audio = video.set_frame_rate(16000).set_channels(1)
                audio.export(audio_path, format="wav")
                print("Áudio extraído com método alternativo")
            except Exception as e:
                raise Exception(f"Erro na extração alternativa: {e}")
        else:
            print("Áudio extraído")
        
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            raise Exception("Arquivo de áudio vazio ou não criado")
        
        return audio_path
        
    except Exception as e:
        raise Exception(f"Erro na extração de áudio: {str(e)}")

def get_audio_duration(audio_path):
    """Obtém a duração do áudio em segundos"""
    try:
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0 
    except:
        return 0