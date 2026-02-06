"""
Rota para upload de minuta com progresso SSE (Server-Sent Events)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import tempfile
import os
import time
import json
import asyncio

from backend import models, schemas, auth
from backend.database import get_db
from audio_processor import extract_audio_from_video, get_audio_duration
from transcription_ai import transcribe_audio
from minutes_generator import generate_structured_minutes
from config import Config

progress_router = APIRouter()

# Armazenar callbacks de progresso por upload_id
progress_callbacks = {}

def progress_callback_factory(upload_id):
    """Cria um callback que armazena o progresso"""
    def callback(progress_data):
        progress_callbacks[upload_id] = progress_data
    return callback

@progress_router.post("/upload-progress")
async def upload_with_progress(
    file: UploadFile = File(...),
    title: str = Form(...),
    diarize: bool = Form(True),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload com SSE de progresso em tempo real"""
    
    upload_id = f"{current_user.id}_{int(time.time())}"
    
    async def generate():
        try:
            # Função helper para enviar SSE
            def send_progress(data):
                yield f"data: {json.dumps({**data, 'upload_id': upload_id})}\n\n"
            
            yield "data: {\"status\": \"started\", \"message\": \"Iniciando upload...\"}\n\n"
            await asyncio.sleep(0.1)
            
            # ... rest of upload logic here
            yield "data: {\"status\": \"complete\", \"percent\": 100}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@progress_router.get("/progress/{upload_id}")
async def get_progress(
    upload_id: str,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Endpoint polling para obter progresso de um upload específico"""
    if upload_id not in progress_callbacks:
        return {"status": "not_found"}
    
    return progress_callbacks.get(upload_id, {"status": "processing"})

@progress_router.delete("/progress/{upload_id}")
async def clear_progress(
    upload_id: str,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Limpar dados de progresso após conclusão"""
    if upload_id in progress_callbacks:
        del progress_callbacks[upload_id]
    return {"status": "cleared"}
