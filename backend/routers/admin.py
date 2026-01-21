from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from backend import models, schemas, auth
from backend.database import get_db

router = APIRouter()

@router.get("/dashboard", response_model=schemas.DashboardStats)
async def get_dashboard_stats(
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics - Admin only"""
    
    # User stats
    total_users = db.query(func.count(models.User.id)).scalar()
    active_users = db.query(func.count(models.User.id)).filter(models.User.is_active == True).scalar()
    
    # Minutes stats
    total_minutes = db.query(func.count(models.Minute.id)).scalar()
    total_processing_time = db.query(func.sum(models.Minute.processing_time)).scalar() or 0
    
    # Recent minutes
    recent_minutes = db.query(models.Minute)\
        .order_by(models.Minute.created_at.desc())\
        .limit(10)\
        .all()
    
    return {
        "user_stats": {
            "total_users": total_users,
            "active_users": active_users,
            "total_minutes": total_minutes,
            "total_processing_time": total_processing_time
        },
        "recent_minutes": recent_minutes
    }

@router.get("/users", response_model=List[schemas.User])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users - Admin only"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user - Admin only"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.email:
        user.email = user_update.email
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete user - Admin only"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.get("/minutes/all", response_model=List[schemas.MinuteWithUser])
async def get_all_minutes(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all minutes from all users - Admin only"""
    minutes = db.query(models.Minute)\
        .order_by(models.Minute.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return minutes
