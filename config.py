import os

class Config:
    UPLOAD_FOLDER = "/app/uploads"
    OUTPUT_FOLDER = "/app/outputs" 
    MODEL_FOLDER = "/app/models"
    
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    
    MAX_FILE_SIZE = 500 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wav', 'mp3', 'm4a'}
    
    @staticmethod
    def create_folders():
        for folder in [Config.UPLOAD_FOLDER, Config.OUTPUT_FOLDER, Config.MODEL_FOLDER]:
            os.makedirs(folder, exist_ok=True)

Config.create_folders()