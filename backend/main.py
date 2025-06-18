from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth import router as auth_router
from app.api.v1.terreno import router as terreno_router
from app.core.database import engine
from app.models import Base

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

# Criar tabelas no banco (opcional, para dev)
Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(terreno_router)

@app.get("/")
async def root():
    return {"message": "Haras System API is running"}