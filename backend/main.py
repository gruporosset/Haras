from fastapi import FastAPI, Depends
from app.api.v1.auth import router as auth_router
from app.core.database import engine
from app.models import Base

app = FastAPI(title="Haras System API")

# Criar tabelas no banco (opcional, para dev)
Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Haras System API is running"}