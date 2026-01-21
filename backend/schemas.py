from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class User(UserInDB):
    pass

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Minute Schemas
class MinuteBase(BaseModel):
    title: str

class MinuteCreate(MinuteBase):
    pass

class MinuteInDB(MinuteBase):
    id: int
    user_id: int
    original_filename: Optional[str]
    file_size: Optional[float]
    audio_duration: Optional[float]
    transcription: Optional[str]
    structured_minutes: Optional[str]
    processing_time: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class Minute(MinuteInDB):
    pass

class MinuteWithUser(MinuteInDB):
    user: User

# Admin Schemas
class UserStats(BaseModel):
    total_users: int
    active_users: int
    total_minutes: int
    total_processing_time: float

class DashboardStats(BaseModel):
    user_stats: UserStats
    recent_minutes: List[MinuteWithUser]
