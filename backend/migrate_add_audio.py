"""
Script de migração para adicionar campos audio_path e segments ao modelo Minute

Executar no terminal dentro do container backend:
docker-compose exec backend python backend/migrate_add_audio.py
"""

from backend.database import engine, SessionLocal
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        print("Iniciando migração...")
        
        # Adicionar coluna audio_path
        try:
            db.execute(text("ALTER TABLE minutes ADD COLUMN audio_path VARCHAR"))
            print("✅ Coluna audio_path adicionada")
        except Exception as e:
            print(f"⚠️ Coluna audio_path já existe ou erro: {e}")
        
        # Adicionar coluna segments
        try:
            db.execute(text("ALTER TABLE minutes ADD COLUMN segments JSON"))
            print("✅ Coluna segments adicionada")
        except Exception as e:
            print(f"⚠️ Coluna segments já existe ou erro: {e}")
        
        db.commit()
        print(" Migração concluída com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro na migração: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
