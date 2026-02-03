from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import tempfile
import os
import time

from backend import models, schemas, auth
from backend.database import get_db
from audio_processor import extract_audio_from_video, get_audio_duration
from transcription_ai import transcribe_audio
from minutes_generator import generate_structured_minutes
from backend.diarization import diarize_audio

router = APIRouter()


def _seconds_to_mmss(value: float) -> str:
    mins = int(value // 60)
    secs = int(value % 60)
    return f"{mins:02d}:{secs:02d}"


def _align_speakers(whisper_segments, diar_segments):
    """Associa cada segmento de texto Whisper ao locutor com maior sobreposição."""
    if not whisper_segments or not diar_segments:
        return []

    aligned = []
    for seg in whisper_segments:
        s_start = float(seg.get("start", 0))
        s_end = float(seg.get("end", 0))
        text = seg.get("text", "").strip()
        best_speaker = "Speaker"
        best_overlap = 0.0

        for d in diar_segments:
            d_start, d_end = d.get("start", 0.0), d.get("end", 0.0)
            overlap = max(0.0, min(s_end, d_end) - max(s_start, d_start))
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = d.get("speaker", "Speaker")

        aligned.append({
            "start": s_start,
            "end": s_end,
            "speaker": best_speaker,
            "text": text
        })
    return aligned


def _format_timeline(timeline):
    if not timeline:
        return "- Diarização não disponível (sem áudio ou modelo)."
    lines = []
    for item in timeline:
        start = _seconds_to_mmss(item.get("start", 0.0))
        end = _seconds_to_mmss(item.get("end", 0.0))
        speaker = item.get("speaker", "Speaker")
        text = item.get("text", "").strip()
        if text:
            lines.append(f"- [{start} - {end}] {speaker}: {text}")
        else:
            lines.append(f"- [{start} - {end}] {speaker}")
    return "\n".join(lines)

@router.post("/upload", response_model=schemas.Minute)
async def create_minute(
    file: UploadFile = File(...),
    title: str = Form(...),
    diarize: bool = Form(True),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload e processa arquivo de áudio/vídeo para gerar ata"""
    
    try:
        print(f"\n=== UPLOAD INICIADO ===")
        print(f"Usuário: {current_user.username}")
        print(f"Arquivo: {file.filename}, Content-Type: {file.content_type}")
        
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file.filename.split(".")[-1]}') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            media_path = tmp_file.name
        
        print(f"Arquivo salvo temporariamente: {media_path}")
        print(f"Tamanho: {len(content)} bytes")
        
        file_size = len(content) / 1024 / 1024  # MB
        
        # Extract audio if video
        if file.content_type.startswith('video'):
            print("Detectado vídeo, extraindo áudio...")
            audio_path = extract_audio_from_video(media_path)
        else:
            print("Detectado áudio direto")
            audio_path = media_path
        
        print(f"Caminho de áudio: {audio_path}, Existe: {os.path.exists(audio_path)}")
        
        # Get audio duration
        duration = get_audio_duration(audio_path)
        print(f"Duração: {duration}s")
        
        # Transcribe (com segmentos para alinhamento de locutor)
        print("Iniciando transcrição...")
        start_time = time.time()
        transcription, whisper_segments = transcribe_audio(audio_path, with_segments=True)
        processing_time = time.time() - start_time
        print(f"Transcrição concluída em {processing_time}s")
        print(f"Resultado ({len(transcription)} chars): {transcription[:100] if transcription else '(vazio)'}...")

        # Diarização offline (opcional)
        timeline_md = ""
        if diarize:
            diar_segments = diarize_audio(audio_path)
            aligned = _align_speakers(whisper_segments or [], diar_segments)
            timeline_md = _format_timeline(aligned)
            if timeline_md:
                timeline_md = "\n\n## 6. Minutagem por Locutor\n" + timeline_md
        
        # Generate structured minutes
        print("Gerando ata estruturada...")
        structured_minutes = generate_structured_minutes(transcription)
        if timeline_md:
            structured_minutes += timeline_md
        
        # Save to database
        db_minute = models.Minute(
            user_id=current_user.id,
            title=title,
            original_filename=file.filename,
            file_size=file_size,
            audio_duration=duration,
            transcription=transcription,
            structured_minutes=structured_minutes,
            processing_time=processing_time
        )
        db.add(db_minute)
        db.commit()
        db.refresh(db_minute)
        print(f"Ata salva no banco: ID {db_minute.id}")
        
        # Cleanup
        if os.path.exists(media_path):
            os.unlink(media_path)
        if audio_path != media_path and os.path.exists(audio_path):
            os.unlink(audio_path)
        
        print("=== UPLOAD CONCLUÍDO ===\n")
        return db_minute
        
    except Exception as e:
        print(f"ERRO NO UPLOAD: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/live", response_model=schemas.Minute)
def create_live_minute(
    payload: schemas.LiveTranscriptionCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Salvar transcrição feita diretamente no navegador (sem upload de arquivo)"""

    if not payload.transcription.strip():
        raise HTTPException(status_code=400, detail="Transcrição não pode estar vazia")

    try:
        start_time = time.time()
        structured_minutes = generate_structured_minutes(payload.transcription)
        processing_time = time.time() - start_time

        # Captura ao vivo baseada em texto não possui áudio para diarização
        structured_minutes += "\n\n## 6. Minutagem por Locutor\n- Diarização indisponível na captura ao vivo sem áudio."

        db_minute = models.Minute(
            user_id=current_user.id,
            title=payload.title,
            original_filename="captura-ao-vivo",
            file_size=None,
            audio_duration=None,
            transcription=payload.transcription,
            structured_minutes=structured_minutes,
            processing_time=processing_time
        )

        db.add(db_minute)
        db.commit()
        db.refresh(db_minute)

        return db_minute

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar transcrição ao vivo: {str(e)}")

@router.get("/", response_model=List[schemas.Minute])
def get_my_minutes(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all minutes for current user"""
    minutes = db.query(models.Minute)\
        .filter(models.Minute.user_id == current_user.id)\
        .order_by(models.Minute.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return minutes

@router.get("/{minute_id}", response_model=schemas.Minute)
def get_minute(
    minute_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific minute by ID"""
    minute = db.query(models.Minute)\
        .filter(models.Minute.id == minute_id, models.Minute.user_id == current_user.id)\
        .first()
    
    if not minute:
        raise HTTPException(status_code=404, detail="Minute not found")
    
    return minute

@router.delete("/{minute_id}")
def delete_minute(
    minute_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a minute"""
    minute = db.query(models.Minute)\
        .filter(models.Minute.id == minute_id, models.Minute.user_id == current_user.id)\
        .first()
    
    if not minute:
        raise HTTPException(status_code=404, detail="Minute not found")
    
    db.delete(minute)
    db.commit()
    
    return {"message": "Minute deleted successfully"}
