import os
from typing import List, Dict, Optional

_pipeline = None


def _load_pipeline():
    """Lazy-load pyannote diarization pipeline if token and package are available."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    token = os.getenv("PYANNOTE_TOKEN") or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        print("[DIARIZATION] Token ausente (PYANNOTE_TOKEN/HF_TOKEN). Diarizacao desabilitada.")
        return None

    try:
        from pyannote.audio import Pipeline

        print("[DIARIZATION] Carregando pipeline pyannote.speaker-diarization@3.1...")
        _pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization@3.1",
            use_auth_token=token,
        )
        return _pipeline
    except Exception as e:
        print(f"[DIARIZATION] Falha ao carregar pipeline: {e}")
        _pipeline = None
        return None


def diarize_audio(audio_path: str) -> List[Dict[str, float]]:
    """
    Executa diarizacao offline usando pyannote, se disponivel.
    Retorna lista de dicts com start, end, speaker.
    """
    pipeline = _load_pipeline()
    if pipeline is None:
        return []

    try:
        diarization = pipeline(audio_path)
        segments: List[Dict[str, float]] = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": float(turn.start),
                "end": float(turn.end),
                "speaker": speaker or "Speaker"
            })
        print(f"[DIARIZATION] Segmentos obtidos: {len(segments)}")
        return segments
    except Exception as e:
        print(f"[DIARIZATION] Erro durante diarizacao: {e}")
        return []
