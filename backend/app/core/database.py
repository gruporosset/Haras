from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuração adicional para o Oracle
engine = create_engine(settings.DATABASE_URL, pool_recycle=3600, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
