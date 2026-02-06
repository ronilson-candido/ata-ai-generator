from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import os
import uvicorn

from backend.database import engine, get_db
from backend import models, schemas, auth
from backend.routers import users, minutes, admin

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cyber Lab - Meeting Minutes API",
    description="API para transcrição e geração de atas com IA",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router, prefix="/api/auth", tags=["authentication"])
app.include_router(minutes.router, prefix="/api/minutes", tags=["minutes"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {
        "message": "Cyber Lab - Meeting Minutes API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    reload_enabled = os.environ.get("UVICORN_RELOAD", "0") == "1"
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=reload_enabled)
