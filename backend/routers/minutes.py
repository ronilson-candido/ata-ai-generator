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

router = APIRouter()

@router.post("/upload", response_model=schemas.Minute)
async def create_minute(
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload e processa arquivo de áudio/vídeo para gerar ata"""
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file.filename.split(".")[-1]}') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            media_path = tmp_file.name
        
        file_size = len(content) / 1024 / 1024  # MB
        
        # Extract audio if video
        if file.content_type.startswith('video'):
            audio_path = extract_audio_from_video(media_path)
        else:
            audio_path = media_path
        
        # Get audio duration
        duration = get_audio_duration(audio_path)
        
        # Transcribe
        start_time = time.time()
        transcription = transcribe_audio(audio_path)
        
        # Generate structured minutes
        structured_minutes = generate_structured_minutes(transcription)
        processing_time = time.time() - start_time
        
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
        
        # Cleanup
        if os.path.exists(media_path):
            os.unlink(media_path)
        if audio_path != media_path and os.path.exists(audio_path):
            os.unlink(audio_path)
        
        return db_minute
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

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
