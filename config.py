import os

class Config:
    UPLOAD_FOLDER = "/app/uploads"
    OUTPUT_FOLDER = "/app/outputs" 
    MODEL_FOLDER = "/app/models"
    
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    
    MAX_FILE_SIZE = 500 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wav', 'mp3', 'm4a'}
    
    # Configurações do Whisper (Faster-Whisper otimizado)
    # Modelos disponíveis: tiny, base, small, medium, large-v2, large-v3
    # Para PT-BR: small = bom equilíbrio (RECOMENDADO), medium = melhor qualidade
    WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "small")
    WHISPER_SPEED_MODE = os.environ.get("WHISPER_SPEED_MODE", "1")
    WHISPER_BEAM_SIZE = int(os.environ.get("WHISPER_BEAM_SIZE", "1")) 
    WHISPER_BEST_OF = int(os.environ.get("WHISPER_BEST_OF", "1"))
    WHISPER_TEMPERATURE = float(os.environ.get("WHISPER_TEMPERATURE", "0.0"))
    
    @staticmethod
    def create_folders():
        for folder in [Config.UPLOAD_FOLDER, Config.OUTPUT_FOLDER, Config.MODEL_FOLDER]:
            os.makedirs(folder, exist_ok=True)

Config.create_folders()