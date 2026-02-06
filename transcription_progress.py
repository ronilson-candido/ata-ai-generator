"""
Wrapper para capturar progresso do Whisper e enviar via callback
"""
import subprocess
import re
import time
import threading

def transcribe_with_progress(model, audio_path, progress_callback=None, **kwargs):
    """
    Transcreve áudio com Whisper e captura progresso em tempo real
    """
    # Habilitar verbose para capturar tqdm
    kwargs['verbose'] = False
    
    # Capturar stderr onde tqdm escreve
    old_stderr = None
    captured_output = []
    start_time = time.time()
    
    class ProgressCapture:
        def __init__(self, callback):
            self.callback = callback
            self.last_update = 0
            self.update_interval = 1.0  # Update a cada 1 segundo
        
        def process_line(self, line):
            # Padrão tqdm: "  3%|▎         | 3780/119793 [00:35<16:58, 113.89frames/s]"
            match = re.search(r'(\d+)%\|.*\|\s+(\d+)/(\d+)\s+\[([0-9:]+)<([0-9:?]+),\s+([\d.?]+)frames/s\]', line)
            if match and self.callback:
                now = time.time()
                if now - self.last_update >= self.update_interval:
                    percent = int(match.group(1))
                    done = int(match.group(2))
                    total = int(match.group(3))
                    elapsed = match.group(4)
                    remaining = match.group(5)
                    fps = match.group(6)
                    
                    try:
                        self.callback({
                            'status': 'transcribing',
                            'percent': percent,
                            'frames_done': done,
                            'frames_total': total,
                            'elapsed': elapsed,
                            'remaining': remaining if remaining != '?' else 'Calculando...',
                            'fps': fps
                        })
                        self.last_update = now
                    except Exception as e:
                        print(f"Erro ao chamar callback: {e}")
    
    # Transcrever com captura de progresso
    capture = ProgressCapture(progress_callback) if progress_callback else None
    
    # Usar stderr hook se disponível (método mais limpo)
    import sys
    from io import StringIO
    
    old_stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        
        # Iniciar transcrição
        start = time.time()
        result = model.transcribe(audio_path, **kwargs)
        elapsed = time.time() - start
        
        if progress_callback:
            try:
                progress_callback({
                    'status': 'complete',
                    'percent': 100,
                    'elapsed_time': elapsed
                })
            except:
                pass
        
        return result
        
    finally:
        if old_stderr:
            sys.stderr = old_stderr
