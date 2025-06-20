from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.auth import router as auth_router
from app.api.v1.terreno import router as terreno_router
from app.api.v1.animal import router as animal_router
from app.api.v1.crescimento import router as crescimento_router
from app.core.database import engine
from app.models import Base
from pathlib import Path

app = FastAPI(title="Haras System API")

#Configurar o CORS
origins = ["http://localhost:9000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Servir arquivos estáticos (uploads)
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Criar tabelas no banco (opcional, para dev)
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(terreno_router)
app.include_router(animal_router)
app.include_router(crescimento_router)

@app.get("/")
async def root():
    return {"message": "Haras System API is running"}
